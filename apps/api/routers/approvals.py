from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_async_db
from core.auth import require_auth, TenantContext
from models.approval import ApprovalRequest
from schemas.approval import ApprovalRequestResponse, ApprovalDecisionCreate
from services.workflow_service import handle_approval_decision

router = APIRouter(prefix="/api/v1/approvals", tags=["approvals"])

@router.get("/", response_model=dict)
async def list_approvals(
    project_id: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    query = select(ApprovalRequest).where(ApprovalRequest.tenant_id == ctx.tenant_id)
    if project_id:
        query = query.where(ApprovalRequest.project_id == project_id)
    if status:
        query = query.where(ApprovalRequest.status == status)
        
    result = await db.execute(query)
    approvals = result.scalars().all()
    return {"data": [ApprovalRequestResponse.model_validate(a).model_dump() for a in approvals], "error": None}

@router.get("/{id}", response_model=dict)
async def get_approval(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    result = await db.execute(select(ApprovalRequest).where(ApprovalRequest.id == id, ApprovalRequest.tenant_id == ctx.tenant_id))
    approval = result.scalars().first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
        
    return {"data": ApprovalRequestResponse.model_validate(approval).model_dump(), "error": None}

@router.post("/{id}/approve", response_model=dict)
async def approve_request(
    id: str,
    data: ApprovalDecisionCreate = None,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    reason = data.reason if data else ""
    await handle_approval_decision(db, id, "approved", ctx.user_id, reason=reason)
    return {"data": {"success": True}, "error": None}

@router.post("/{id}/reject", response_model=dict)
async def reject_request(
    id: str,
    data: ApprovalDecisionCreate = None,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth)
):
    reason = data.reason if data else ""
    await handle_approval_decision(db, id, "rejected", ctx.user_id, reason=reason)
    return {"data": {"success": True}, "error": None}
