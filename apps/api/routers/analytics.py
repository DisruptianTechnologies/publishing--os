"""
Analytics routes: project stats, cost breakdown, audit log.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_async_db
from core.auth import require_auth, TenantContext
from core.config import settings
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
    try:
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
                'total_tokens': int(task_agg.total_tokens or 0) if task_agg else 0,
                'total_cost_usd': round(float(task_agg.total_cost_usd or 0), 4) if task_agg else 0.0,
                'total_workflows': total_workflows
            },
            'error': None
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        if settings.DEMO_MODE:
            return {
                'data': {
                    'project_id': project_id,
                    'total_tokens': 184500,
                    'total_cost_usd': 2.45,
                    'total_workflows': 6
                },
                'error': None
            }
        raise


@router.get('/usage', response_model=dict)
async def usage_breakdown(
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
    limit: int = 100,
    offset: int = 0
):
    """Cost breakdown and token usage."""
    try:
        result = await db.execute(
            select(UsageRecord)
            .where(UsageRecord.tenant_id == ctx.tenant_id)
            .order_by(UsageRecord.recorded_at.desc())
            .limit(limit)
            .offset(offset)
        )
        records = result.scalars().all()
        return {
            'data': [
                {
                    'id': str(r.id),
                    'project_id': str(r.project_id) if r.project_id else None,
                    'resource_type': r.resource_type,
                    'quantity': r.quantity,
                    'unit_cost_usd': r.unit_cost_usd,
                    'total_cost_usd': r.total_cost_usd,
                    'model_name': r.model_name,
                    'provider_name': r.provider_name,
                    'recorded_at': r.recorded_at.isoformat()
                } for r in records
            ],
            'error': None
        }
    except Exception:
        if settings.DEMO_MODE:
            demo_records = [
                {
                    'id': 'usg-001',
                    'project_id': 'demo-project-001',
                    'resource_type': 'llm_tokens',
                    'quantity': 38000,
                    'unit_cost_usd': 0.000005,
                    'total_cost_usd': 0.19,
                    'model_name': 'gemini-1.5-pro',
                    'provider_name': 'gemini',
                    'recorded_at': '2026-10-11T04:20:00Z'
                },
                {
                    'id': 'usg-002',
                    'project_id': 'demo-project-001',
                    'resource_type': 'llm_tokens',
                    'quantity': 14200,
                    'unit_cost_usd': 0.000001,
                    'total_cost_usd': 0.0142,
                    'model_name': 'gemini-2.0-flash',
                    'provider_name': 'gemini',
                    'recorded_at': '2026-10-11T04:15:00Z'
                }
            ]
            return {'data': demo_records, 'error': None}
        raise


@router.get('/audit-logs', response_model=dict)
async def get_audit_logs(
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
    limit: int = 100,
    offset: int = 0
):
    """System and project audit logs."""
    try:
        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.tenant_id == ctx.tenant_id)
            .order_by(AuditLog.occurred_at.desc())
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
                    'resource_id': str(log.resource_id),
                    'resource_type': log.resource_type,
                    'occurred_at': log.occurred_at.isoformat()
                } for log in logs
            ],
            'error': None
        }
    except Exception:
        if settings.DEMO_MODE:
            demo_logs = [
                {
                    'id': 'aud-001',
                    'action': 'compile_manuscript',
                    'actor_id': ctx.user_id,
                    'actor_type': 'user',
                    'resource_id': 'demo-project-001',
                    'resource_type': 'project',
                    'occurred_at': '2026-10-11T04:20:00Z'
                },
                {
                    'id': 'aud-002',
                    'action': 'ai_assist_clean_tropes',
                    'actor_id': 'editing_agent',
                    'actor_type': 'agent',
                    'resource_id': 'chapter-1',
                    'resource_type': 'chapter',
                    'occurred_at': '2026-10-11T04:18:00Z'
                }
            ]
            return {'data': demo_logs, 'error': None}
        raise
