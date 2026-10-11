from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_async_db
from core.auth import require_auth, TenantContext
from core.config import settings
from models.approval import ApprovalRequest
from schemas.approval import ApprovalRequestResponse, ApprovalDecisionCreate
from services.workflow_service import handle_approval_decision

router = APIRouter(prefix="/api/v1/approvals", tags=["approvals"])

DEMO_APPROVALS_LIST = [
    {
        "id": "appr-001",
        "tenant_id": "demo-tenant-00000000",
        "project_id": "demo-project-001",
        "approval_type": "chapter",
        "title": "Review Chapter 1 Draft & AI Editorial Critique",
        "description": "Chapter 1 has been drafted and verified for trope removal. Ready for author sign-off.",
        "requested_by": "writing_agent",
        "risk_score": 0.15,
        "evidence_summary": "Passed Flesch readability (64.2) and zero copyright risks.",
        "expected_external_effect": "Advances project pipeline to developmental editing phase.",
        "estimated_cost_usd": 0.42,
        "expires_at": None,
        "status": "pending",
        "artifact_id": "art-001",
        "artifact_version": 1,
        "created_at": "2026-10-11T04:00:00Z",
        "updated_at": "2026-10-11T04:00:00Z"
    },
    {
        "id": "appr-002",
        "tenant_id": "demo-tenant-00000000",
        "project_id": "demo-project-001",
        "approval_type": "opportunity",
        "title": "Approve High-Volume Keyword Category Placement",
        "description": "Selected 7 KDP backend keywords and 3 primary BISAC category browse nodes.",
        "requested_by": "metadata_agent",
        "risk_score": 0.05,
        "evidence_summary": "Estimated 4,200 monthly searches across low competition niches.",
        "expected_external_effect": "Locks KDP metadata for publication staging.",
        "estimated_cost_usd": 0.12,
        "expires_at": None,
        "status": "pending",
        "artifact_id": "art-002",
        "artifact_version": 1,
        "created_at": "2026-10-11T03:30:00Z",
        "updated_at": "2026-10-11T03:30:00Z"
    }
]

@router.get("/", response_model=dict)
async def list_approvals(
    project_id: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    try:
        query = select(ApprovalRequest).where(ApprovalRequest.tenant_id == ctx.tenant_id)
        if project_id:
            query = query.where(ApprovalRequest.project_id == project_id)
        if status:
            query = query.where(ApprovalRequest.status == status)
            
        result = await db.execute(query)
        approvals = result.scalars().all()
        if approvals:
            return {"data": [ApprovalRequestResponse.model_validate(a).model_dump() for a in approvals], "error": None}
    except Exception:
        pass
        
    if settings.DEMO_MODE:
        filtered = DEMO_APPROVALS_LIST
        if project_id:
            filtered = [a for a in filtered if a["project_id"] == project_id]
        if status:
            filtered = [a for a in filtered if a["status"] == status]
        return {"data": filtered, "error": None}
    return {"data": [], "error": None}

@router.get("/{id}", response_model=dict)
async def get_approval(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    try:
        result = await db.execute(select(ApprovalRequest).where(ApprovalRequest.id == id, ApprovalRequest.tenant_id == ctx.tenant_id))
        approval = result.scalars().first()
        if approval:
            return {"data": ApprovalRequestResponse.model_validate(approval).model_dump(), "error": None}
    except Exception:
        pass
        
    if settings.DEMO_MODE:
        match = next((a for a in DEMO_APPROVALS_LIST if a["id"] == id), None)
        if match:
            return {"data": match, "error": None}
        return {"data": DEMO_APPROVALS_LIST[0], "error": None}
        
    raise HTTPException(status_code=404, detail="Approval not found")

@router.post("/{id}/approve", response_model=dict)
async def approve_request(
    id: str,
    data: ApprovalDecisionCreate = None,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    reason = data.reason if data else ""
    try:
        await handle_approval_decision(db, id, "approved", ctx.user_id, reason=reason)
    except Exception:
        if not settings.DEMO_MODE:
            raise
    return {"data": {"success": True, "status": "approved", "id": id}, "error": None}

@router.post("/{id}/reject", response_model=dict)
async def reject_request(
    id: str,
    data: ApprovalDecisionCreate = None,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    reason = data.reason if data else ""
    try:
        await handle_approval_decision(db, id, "rejected", ctx.user_id, reason=reason)
    except Exception:
        if not settings.DEMO_MODE:
            raise
    return {"data": {"success": True, "status": "rejected", "id": id}, "error": None}
