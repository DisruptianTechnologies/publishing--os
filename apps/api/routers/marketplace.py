from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_async_db
from core.auth import require_auth, TenantContext
from models.marketplace import (
    MarketplaceAccount,
    MarketplaceListing,
    PublishingJob,
    MarketplacePackage,
)
from schemas.marketplace import (
    MarketplaceAccountCreate,
    MarketplaceAccountResponse,
    MarketplaceListingCreate,
    MarketplaceListingResponse,
    PublishingJobCreate,
    PublishingJobResponse,
    PackagePreflightRequest,
    PackagePreflightResponse,
)
from services.marketplace_service import (
    run_package_preflight,
    create_and_execute_publishing_job,
    get_connector,
)

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])


@router.get("/accounts", response_model=dict)
async def list_accounts(
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    query = select(MarketplaceAccount).where(MarketplaceAccount.tenant_id == ctx.tenant_id)
    res = await db.execute(query)
    accounts = res.scalars().all()
    return {
        "data": [MarketplaceAccountResponse.model_validate(a).model_dump() for a in accounts],
        "error": None,
    }


@router.post("/accounts", response_model=dict)
async def create_account(
    data: MarketplaceAccountCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    account = MarketplaceAccount(
        tenant_id=ctx.tenant_id,
        marketplace=data.marketplace,
        name=data.name,
        credentials=data.credentials,
        auth_status='authorized' if data.credentials else 'pending_authorization',
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return {
        "data": MarketplaceAccountResponse.model_validate(account).model_dump(),
        "error": None,
    }


@router.get("/listings", response_model=dict)
async def list_listings(
    project_id: str | None = None,
    marketplace: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    query = select(MarketplaceListing).where(MarketplaceListing.tenant_id == ctx.tenant_id)
    if project_id:
        query = query.where(MarketplaceListing.project_id == project_id)
    if marketplace:
        query = query.where(MarketplaceListing.marketplace == marketplace)
    if status:
        query = query.where(MarketplaceListing.status == status)

    res = await db.execute(query)
    listings = res.scalars().all()
    return {
        "data": [MarketplaceListingResponse.model_validate(item).model_dump() for item in listings],
        "error": None,
    }


@router.post("/listings", response_model=dict)
async def create_listing(
    data: MarketplaceListingCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    listing = MarketplaceListing(
        tenant_id=ctx.tenant_id,
        project_id=data.project_id,
        account_id=data.account_id,
        marketplace=data.marketplace,
        title=data.title,
        price_usd=data.price_usd,
        currency=data.currency,
        metadata_snapshot=data.metadata_snapshot,
        status='draft',
    )
    db.add(listing)
    await db.commit()
    await db.refresh(listing)
    return {
        "data": MarketplaceListingResponse.model_validate(listing).model_dump(),
        "error": None,
    }


@router.post("/preflight", response_model=dict)
async def preflight_package(
    data: PackagePreflightRequest,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    try:
        pkg = await run_package_preflight(
            db,
            ctx.tenant_id,
            data.project_id,
            data.package_type,
            data.interior_artifact_id,
            data.cover_artifact_id,
            data.metadata_artifact_id,
        )
        return {
            "data": PackagePreflightResponse.model_validate(pkg).model_dump(),
            "error": None,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/publish", response_model=dict)
async def publish_job(
    data: PublishingJobCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    try:
        job = await create_and_execute_publishing_job(
            db,
            ctx.tenant_id,
            data.project_id,
            data.account_id,
            data.job_type,
            data.payload,
            data.listing_id,
        )
        return {
            "data": PublishingJobResponse.model_validate(job).model_dump(),
            "error": None,
        }
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jobs", response_model=dict)
async def list_jobs(
    project_id: str | None = None,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    query = select(PublishingJob).where(PublishingJob.tenant_id == ctx.tenant_id)
    if project_id:
        query = query.where(PublishingJob.project_id == project_id)
    query = query.order_by(PublishingJob.created_at.desc())

    res = await db.execute(query)
    jobs = res.scalars().all()
    return {
        "data": [PublishingJobResponse.model_validate(j).model_dump() for j in jobs],
        "error": None,
    }
