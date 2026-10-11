"""
Analytics routes: project stats, cost breakdown, audit log.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_async_db
from core.auth import require_auth, TenantContext
from models.analytics import AuditLog, UsageRecord
from models.agent import AgentTask, WorkflowRun
from models.artifact import Artifact
from models.project import Project

router = APIRouter(prefix='/api/v1/analytics', tags=['analytics'])


@router.get('/projects/{project_id}', response_model=dict)
async def project_analytics(
    project_id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    """Detailed analytics for a single project."""
    # Verify ownership
    proj_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == ctx.tenant_id)
    )
    project = proj_result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')

    # Task and Cost aggregations
    task_res = await db.execute(
        select(
            func.sum(AgentTask.token_usage).label('total_tokens'),
            func.sum(AgentTask.cost_usd).label('total_cost_usd')
        ).where(AgentTask.project_id == project_id, AgentTask.tenant_id == ctx.tenant_id)
    )
    task_agg = task_res.first()

    # Workflow counts
    wf_res = await db.execute(
        select(func.count(WorkflowRun.id)).where(WorkflowRun.project_id == project_id, WorkflowRun.tenant_id == ctx.tenant_id)
    )
    total_workflows = wf_res.scalar() or 0

    return {
        'data': {
            'project_id': project_id,
            'total_tokens': int(task_agg.total_tokens or 0),
            'total_cost_usd': round(float(task_agg.total_cost_usd or 0), 4),
            'total_workflows': total_workflows
        },
        'error': None
    }


@router.get('/usage', response_model=dict)
async def usage_breakdown(
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
    limit: int = 100,
    offset: int = 0
):
    """Cost breakdown and token usage."""
    result = await db.execute(
        select(UsageRecord)
        .where(UsageRecord.tenant_id == ctx.tenant_id)
        .order_by(UsageRecord.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    records = result.scalars().all()
    return {
        'data': [
            {
                'id': str(r.id),
                'project_id': str(r.project_id),
                'resource_type': r.resource_type,
                'quantity': r.quantity,
                'unit_cost_usd': r.unit_cost_usd,
                'timestamp': r.timestamp.isoformat()
            } for r in records
        ],
        'error': None
    }


@router.get('/audit-logs', response_model=dict)
async def get_audit_logs(
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
    limit: int = 100,
    offset: int = 0
):
    """System and project audit logs."""
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.tenant_id == ctx.tenant_id)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )
    logs = result.scalars().all()
    return {
        'data': [
            {
                'id': str(log.id),
                'action': log.action,
                'actor_id': str(log.actor_id),
                'actor_type': log.actor_type,
                'target_id': str(log.target_id),
                'target_type': log.target_type,
                'timestamp': log.timestamp.isoformat()
            } for log in logs
        ],
        'error': None
    }
