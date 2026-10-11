from sqlalchemy.ext.asyncio import AsyncSession
from models.analytics import AuditLog, UsageRecord

async def log_action(db: AsyncSession, tenant_id: str, actor_type: str, actor_id: str, action: str, resource_type: str, resource_id: str, payload: dict = None, correlation_id: str = ''):
    log = AuditLog(
        tenant_id=tenant_id,
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        payload=payload or {},
        correlation_id=correlation_id
    )
    db.add(log)
    await db.commit()

async def record_usage(db: AsyncSession, tenant_id: str, project_id: str, resource_type: str, quantity: float, unit_cost_usd: float, model_name: str = '', provider_name: str = '', workflow_run_id: str = None, agent_task_id: str = None):
    usage = UsageRecord(
        tenant_id=tenant_id,
        project_id=project_id,
        resource_type=resource_type,
        quantity=quantity,
        unit_cost_usd=unit_cost_usd,
        total_cost_usd=quantity * unit_cost_usd,
        model_name=model_name,
        provider_name=provider_name,
        workflow_run_id=workflow_run_id,
        agent_task_id=agent_task_id
    )
    db.add(usage)
    await db.commit()
