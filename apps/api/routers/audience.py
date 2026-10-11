from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_async_db
from core.auth import require_auth, TenantContext
from models.audience import (
    CommunitySource,
    ContentOpportunity,
    ContentDraft,
    SubscriberProfile,
    ConsentRecord,
    LandingPage,
    GlobalKillSwitch,
)
from schemas.audience import (
    CommunitySourceCreate,
    CommunitySourceResponse,
    ContentOpportunityCreate,
    ContentOpportunityResponse,
    ContentDraftCreate,
    ContentDraftResponse,
    SubscriberCreate,
    SubscriberResponse,
    ConsentRecordResponse,
    LandingPageCreate,
    LandingPageResponse,
    GlobalKillSwitchToggle,
    GlobalKillSwitchResponse,
)
from services.audience_service import (
    check_kill_switch,
    toggle_kill_switch,
    register_subscriber_with_consent,
    revoke_subscriber_consent,
    audit_content_draft_safety,
)

router = APIRouter(prefix="/api/v1/audience", tags=["audience"])


# ---------------------------------------------------------------------------
# Community Sources & Opportunities
# ---------------------------------------------------------------------------
@router.get("/sources", response_model=dict)
async def list_sources(
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    res = await db.execute(
        select(CommunitySource).where(CommunitySource.tenant_id == ctx.tenant_id)
    )
    sources = res.scalars().all()
    return {
        "data": [CommunitySourceResponse.model_validate(s).model_dump() for s in sources],
        "error": None,
    }


@router.post("/sources", response_model=dict)
async def create_source(
    data: CommunitySourceCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    source = CommunitySource(
        tenant_id=ctx.tenant_id,
        platform=data.platform,
        source_name=data.source_name,
        source_url=data.source_url,
        rules_summary=data.rules_summary,
        topic_tags=data.topic_tags,
        compliance_notes=data.compliance_notes,
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return {
        "data": CommunitySourceResponse.model_validate(source).model_dump(),
        "error": None,
    }


@router.get("/opportunities", response_model=dict)
async def list_opportunities(
    source_id: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    query = select(ContentOpportunity).where(ContentOpportunity.tenant_id == ctx.tenant_id)
    if source_id:
        query = query.where(ContentOpportunity.source_id == source_id)
    if status:
        query = query.where(ContentOpportunity.status == status)
    query = query.order_by(ContentOpportunity.relevance_score.desc())

    res = await db.execute(query)
    opps = res.scalars().all()
    return {
        "data": [ContentOpportunityResponse.model_validate(o).model_dump() for o in opps],
        "error": None,
    }


@router.post("/opportunities", response_model=dict)
async def create_opportunity(
    data: ContentOpportunityCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    opp = ContentOpportunity(
        tenant_id=ctx.tenant_id,
        source_id=data.source_id,
        project_id=data.project_id,
        opportunity_type=data.opportunity_type,
        title=data.title,
        url=data.url,
        relevance_score=data.relevance_score,
        intent_class=data.intent_class,
        notes=data.notes,
        status='new',
    )
    db.add(opp)
    await db.commit()
    await db.refresh(opp)
    return {
        "data": ContentOpportunityResponse.model_validate(opp).model_dump(),
        "error": None,
    }


# ---------------------------------------------------------------------------
# Content Drafts (Value-First & Safety Checked)
# ---------------------------------------------------------------------------
@router.get("/drafts", response_model=dict)
async def list_drafts(
    platform: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    query = select(ContentDraft).where(ContentDraft.tenant_id == ctx.tenant_id)
    if platform:
        query = query.where(ContentDraft.platform == platform)
    if status:
        query = query.where(ContentDraft.status == status)
    query = query.order_by(ContentDraft.created_at.desc())

    res = await db.execute(query)
    drafts = res.scalars().all()
    return {
        "data": [ContentDraftResponse.model_validate(d).model_dump() for d in drafts],
        "error": None,
    }


@router.post("/drafts", response_model=dict)
async def create_draft(
    data: ContentDraftCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    # Safety scan
    policy_status, policy_flags = audit_content_draft_safety(data.body, data.platform)
    status = 'waiting_approval' if policy_status == 'compliant' else 'draft'
    if policy_status == 'blocked':
        status = 'rejected'

    draft = ContentDraft(
        tenant_id=ctx.tenant_id,
        project_id=data.project_id,
        opportunity_id=data.opportunity_id,
        platform=data.platform,
        draft_type=data.draft_type,
        title=data.title,
        body=data.body,
        variant_options=data.variant_options,
        policy_status=policy_status,
        policy_flags=policy_flags,
        status=status,
    )
    db.add(draft)
    await db.commit()
    await db.refresh(draft)
    return {
        "data": ContentDraftResponse.model_validate(draft).model_dump(),
        "error": None,
    }


# ---------------------------------------------------------------------------
# Subscribers & Consent Records
# ---------------------------------------------------------------------------
@router.get("/subscribers", response_model=dict)
async def list_subscribers(
    status: str | None = None,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    query = select(SubscriberProfile).where(SubscriberProfile.tenant_id == ctx.tenant_id)
    if status:
        query = query.where(SubscriberProfile.status == status)

    res = await db.execute(query)
    subs = res.scalars().all()
    return {
        "data": [SubscriberResponse.model_validate(s).model_dump() for s in subs],
        "error": None,
    }


@router.post("/subscribers", response_model=dict)
async def register_subscriber(
    data: SubscriberCreate,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    ip = request.client.host if request.client else '127.0.0.1'
    user_agent = request.headers.get('User-Agent', '')

    sub = await register_subscriber_with_consent(
        db=db,
        tenant_id=ctx.tenant_id,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        source=data.source,
        tags=data.tags,
        consent_granted=data.consent_granted,
        opt_in_mechanism=data.opt_in_mechanism,
        ip_address=ip,
        user_agent=user_agent,
    )
    return {
        "data": SubscriberResponse.model_validate(sub).model_dump(),
        "error": None,
    }


@router.post("/subscribers/revoke-consent", response_model=dict)
async def revoke_consent(
    email: str,
    reason: str = "user_unsubscribe",
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    revoked = await revoke_subscriber_consent(db, ctx.tenant_id, email, reason)
    if not revoked:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    return {"data": {"success": True, "email": email, "status": "unsubscribed"}, "error": None}


# ---------------------------------------------------------------------------
# Landing Pages
# ---------------------------------------------------------------------------
@router.get("/landing-pages", response_model=dict)
async def list_landing_pages(
    project_id: str | None = None,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    query = select(LandingPage).where(LandingPage.tenant_id == ctx.tenant_id)
    if project_id:
        query = query.where(LandingPage.project_id == project_id)

    res = await db.execute(query)
    pages = res.scalars().all()
    return {
        "data": [LandingPageResponse.model_validate(p).model_dump() for p in pages],
        "error": None,
    }


@router.post("/landing-pages", response_model=dict)
async def create_landing_page(
    data: LandingPageCreate,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    page = LandingPage(
        tenant_id=ctx.tenant_id,
        project_id=data.project_id,
        slug=data.slug,
        title=data.title,
        headline=data.headline,
        description=data.description,
        template=data.template,
        form_fields=data.form_fields,
        is_published=data.is_published,
    )
    db.add(page)
    await db.commit()
    await db.refresh(page)
    return {
        "data": LandingPageResponse.model_validate(page).model_dump(),
        "error": None,
    }


# ---------------------------------------------------------------------------
# Global Kill Switches
# ---------------------------------------------------------------------------
@router.get("/kill-switches", response_model=dict)
async def list_kill_switches(
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    res = await db.execute(
        select(GlobalKillSwitch).where(GlobalKillSwitch.tenant_id == ctx.tenant_id)
    )
    switches = res.scalars().all()
    return {
        "data": [GlobalKillSwitchResponse.model_validate(s).model_dump() for s in switches],
        "error": None,
    }


@router.post("/kill-switches/toggle", response_model=dict)
async def toggle_switch(
    data: GlobalKillSwitchToggle,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    switch = await toggle_kill_switch(
        db, ctx.tenant_id, data.scope, data.is_active, ctx.user_id, data.reason
    )
    return {
        "data": GlobalKillSwitchResponse.model_validate(switch).model_dump(),
        "error": None,
    }
