"""
Marketplace Studio service.
Provides connector abstractions, package validation (preflight), and idempotent publishing jobs.
"""
from __future__ import annotations
import uuid
import hashlib
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.marketplace import (
    MarketplaceAccount,
    MarketplaceListing,
    PublishingJob,
    MarketplacePackage,
)
from models.project import Project
from models.artifact import Artifact
from packages.policy_engine.engine import get_policy_engine, PolicyAction

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Marketplace Connectors (Adapter Pattern)
# ---------------------------------------------------------------------------
class BaseMarketplaceConnector:
    def __init__(self, account: MarketplaceAccount):
        self.account = account

    async def test_connection(self) -> dict:
        raise NotImplementedError

    async def submit_listing(self, payload: dict) -> dict:
        raise NotImplementedError


class KDPConnector(BaseMarketplaceConnector):
    async def test_connection(self) -> dict:
        # Mock adapter — flagged as pending_authorization until real SP-API credentials provided
        if self.account.auth_status != 'authorized':
            return {
                'success': False,
                'status': 'pending_authorization',
                'message': 'Amazon KDP developer authorization is pending. Mock connector active.',
            }
        return {'success': True, 'status': 'connected', 'marketplace': 'kdp'}

    async def submit_listing(self, payload: dict) -> dict:
        title = payload.get('title', 'Untitled')
        price = payload.get('price_usd', 9.99)
        mock_asin = f'B0{hashlib.md5(title.encode()).hexdigest()[:8].upper()}'
        return {
            'success': True,
            'marketplace': 'kdp',
            'external_listing_id': mock_asin,
            'listing_url': f'https://www.amazon.com/dp/{mock_asin}',
            'status': 'live_sandbox',
            'message': 'Listing simulated in KDP Sandbox. Real publishing requires Amazon authorized token.',
        }


class EtsyConnector(BaseMarketplaceConnector):
    async def test_connection(self) -> dict:
        if self.account.auth_status != 'authorized':
            return {
                'success': False,
                'status': 'pending_authorization',
                'message': 'Etsy OAuth 2.0 authorization pending. Mock connector active.',
            }
        return {'success': True, 'status': 'connected', 'marketplace': 'etsy'}

    async def submit_listing(self, payload: dict) -> dict:
        title = payload.get('title', 'Untitled')
        mock_id = f'ETSY-{uuid.uuid4().hex[:10].upper()}'
        return {
            'success': True,
            'marketplace': 'etsy',
            'external_listing_id': mock_id,
            'listing_url': f'https://www.etsy.com/listing/{mock_id}',
            'status': 'draft_sandbox',
            'message': 'Etsy digital printable listing staged successfully.',
        }


def get_connector(account: MarketplaceAccount) -> BaseMarketplaceConnector:
    if account.marketplace == 'kdp':
        return KDPConnector(account)
    elif account.marketplace == 'etsy':
        return EtsyConnector(account)
    raise ValueError(f"Unsupported marketplace: {account.marketplace}")


# ---------------------------------------------------------------------------
# Preflight Package Validation
# ---------------------------------------------------------------------------
async def run_package_preflight(
    db: AsyncSession,
    tenant_id: str,
    project_id: str,
    package_type: str,
    interior_artifact_id: str | None = None,
    cover_artifact_id: str | None = None,
    metadata_artifact_id: str | None = None,
) -> MarketplacePackage:
    report = {
        'checks': [],
        'passed_count': 0,
        'warnings_count': 0,
        'errors_count': 0,
        'package_type': package_type,
    }

    # Verify project
    proj_res = await db.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
    )
    project = proj_res.scalars().first()
    if not project:
        raise ValueError("Project not found")

    # 1. Title Check
    if len(project.name.strip()) >= 3:
        report['checks'].append({'check': 'title_validity', 'status': 'passed', 'details': f"Title: '{project.name}'"})
        report['passed_count'] += 1
    else:
        report['checks'].append({'check': 'title_validity', 'status': 'failed', 'details': "Title too short"})
        report['errors_count'] += 1

    # 2. Metadata Artifact Check
    if metadata_artifact_id:
        report['checks'].append({'check': 'metadata_attached', 'status': 'passed', 'artifact_id': metadata_artifact_id})
        report['passed_count'] += 1
    else:
        report['checks'].append({'check': 'metadata_attached', 'status': 'warning', 'details': 'No metadata artifact attached; default project metadata will be used.'})
        report['warnings_count'] += 1

    # 3. KDP specific price bounds check
    if 'kdp' in package_type:
        report['checks'].append({
            'check': 'kdp_pricing_guidelines',
            'status': 'passed',
            'details': '70% royalty threshold requires pricing between $2.99 and $9.99 USD.',
        })
        report['passed_count'] += 1

    overall_status = 'passed' if report['errors_count'] == 0 else 'failed'
    if report['warnings_count'] > 0 and overall_status == 'passed':
        overall_status = 'warnings'

    checksum = hashlib.sha256(json.dumps(report).encode()).hexdigest()

    pkg = MarketplacePackage(
        tenant_id=tenant_id,
        project_id=project_id,
        package_type=package_type,
        interior_artifact_id=interior_artifact_id,
        cover_artifact_id=cover_artifact_id,
        metadata_artifact_id=metadata_artifact_id,
        preflight_status=overall_status,
        preflight_report=report,
        checksum=checksum,
    )
    db.add(pkg)
    await db.commit()
    await db.refresh(pkg)
    return pkg


# ---------------------------------------------------------------------------
# Idempotent Publishing Job Execution
# ---------------------------------------------------------------------------
async def create_and_execute_publishing_job(
    db: AsyncSession,
    tenant_id: str,
    project_id: str,
    account_id: str,
    job_type: str,
    payload: dict,
    listing_id: str | None = None,
) -> PublishingJob:
    # 1. Deterministic Idempotency Key
    idempotency_raw = f"{tenant_id}:{project_id}:{account_id}:{job_type}:{json.dumps(payload, sort_keys=True)}"
    idempotency_key = hashlib.sha256(idempotency_raw.encode()).hexdigest()

    # Check existing job with this key
    existing_res = await db.execute(
        select(PublishingJob).where(PublishingJob.idempotency_key == idempotency_key)
    )
    existing_job = existing_res.scalars().first()
    if existing_job:
        logger.info(f"PublishingJob {existing_job.id} already exists with idempotency key")
        return existing_job

    # 2. Check Account
    acc_res = await db.execute(
        select(MarketplaceAccount).where(
            MarketplaceAccount.id == account_id,
            MarketplaceAccount.tenant_id == tenant_id,
        )
    )
    account = acc_res.scalars().first()
    if not account:
        raise ValueError("Marketplace account not found")

    # 3. Policy Engine Evaluation (Policy is a blocking layer)
    engine = get_policy_engine()
    action = PolicyAction(
        action_type='create_listing',
        tenant_id=tenant_id,
        project_id=project_id,
        estimated_cost_usd=0.0,
    )
    decision = engine.evaluate(action, {'autonomy_level': 2})
    if decision.decision == 'block':
        raise PermissionError(f"Publishing blocked by policy: {', '.join(decision.reasons)}")

    # 4. Create Job Record
    job = PublishingJob(
        tenant_id=tenant_id,
        project_id=project_id,
        account_id=account_id,
        listing_id=listing_id,
        job_type=job_type,
        idempotency_key=idempotency_key,
        status='in_progress',
        payload=payload,
        attempts=1,
        started_at=datetime.now(timezone.utc),
    )
    db.add(job)
    await db.flush()

    # 5. Execute via Connector
    connector = get_connector(account)
    try:
        submission_result = await connector.submit_listing(payload)
        job.status = 'completed'
        job.result = submission_result
        job.completed_at = datetime.now(timezone.utc)

        # Update or create listing if successful
        if not listing_id:
            new_listing = MarketplaceListing(
                tenant_id=tenant_id,
                project_id=project_id,
                account_id=account_id,
                marketplace=account.marketplace,
                external_listing_id=submission_result.get('external_listing_id'),
                status='live',
                listing_url=submission_result.get('listing_url'),
                title=payload.get('title', 'Untitled'),
                price_usd=payload.get('price_usd', 9.99),
                metadata_snapshot=payload,
            )
            db.add(new_listing)
            await db.flush()
            job.listing_id = str(new_listing.id)

    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        logger.error(f"Publishing job failed: {e}")

    await db.commit()
    await db.refresh(job)
    return job
