"""
Agent task routes: list, get, stream (SSE), cancel.
"""
from __future__ import annotations
import json
import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_async_db
from core.auth import require_auth, TenantContext
from core.config import settings
from models.agent import AgentTask, WorkflowRun

router = APIRouter(prefix='/api/v1/tasks', tags=['tasks'])


@router.get('/projects/{project_id}/tasks', response_model=dict)
async def list_tasks(
    project_id: str,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    query = select(AgentTask).where(
        AgentTask.project_id == project_id,
        AgentTask.tenant_id == ctx.tenant_id,
    )
    if status:
        query = query.where(AgentTask.status == status)
    query = query.order_by(AgentTask.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return {
        'data': [
            {
                'id': str(t.id),
                'agent_type': t.agent_type,
                'status': t.status,
                'workflow_run_id': str(t.workflow_run_id),
                'attempt': t.attempt,
                'max_attempts': t.max_attempts,
                'approval_policy': t.approval_policy,
                'token_usage': t.token_usage,
                'cost_usd': t.cost_usd,
                'started_at': t.started_at.isoformat() if t.started_at else None,
                'completed_at': t.completed_at.isoformat() if t.completed_at else None,
                'error_code': t.error_code,
                'error_message': t.error_message,
                'created_at': t.created_at.isoformat(),
            }
            for t in tasks
        ],
        'error': None,
    }


@router.get('/{id}', response_model=dict)
async def get_task(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    result = await db.execute(
        select(AgentTask).where(
            AgentTask.id == id,
            AgentTask.tenant_id == ctx.tenant_id,
        )
    )
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')
    return {
        'data': {
            'id': str(task.id),
            'agent_type': task.agent_type,
            'status': task.status,
            'workflow_run_id': str(task.workflow_run_id),
            'project_id': str(task.project_id),
            'input_artifact_ids': task.input_artifact_ids,
            'output_artifact_ids': task.output_artifact_ids,
            'attempt': task.attempt,
            'max_attempts': task.max_attempts,
            'approval_policy': task.approval_policy,
            'model_policy': task.model_policy,
            'token_budget': task.token_budget,
            'cost_budget_usd': task.cost_budget_usd,
            'token_usage': task.token_usage,
            'cost_usd': task.cost_usd,
            'config': task.config,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'error_code': task.error_code,
            'error_message': task.error_message,
            'created_at': task.created_at.isoformat(),
        },
        'error': None,
    }


@router.get('/{id}/stream')
async def stream_task_logs(
    id: str,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    """
    Server-Sent Events stream for real-time task log updates.
    Subscribes to Redis pub/sub channel task:{id}:logs.
    Sends keep-alive every 15 seconds to prevent proxy timeouts.
    """
    # Verify task belongs to tenant
    result = await db.execute(
        select(AgentTask).where(
            AgentTask.id == id,
            AgentTask.tenant_id == ctx.tenant_id,
        )
    )
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')

    channel = f'task:{id}:logs'

    async def event_generator():
        import redis.asyncio as aioredis
        redis_client = None
        pubsub = None
        try:
            redis_client = aioredis.from_url(settings.REDIS_URL)
            pubsub = redis_client.pubsub()
            await pubsub.subscribe(channel)

            # Send initial connection event
            yield f'data: {json.dumps({"type": "connected", "task_id": id, "status": task.status})}\n\n'

            keepalive_interval = 15  # seconds
            time_since_keepalive = 0

            async for message in pubsub.listen():
                if await request.is_disconnected():
                    break

                if message['type'] == 'message':
                    data = message['data']
                    if isinstance(data, bytes):
                        data = data.decode('utf-8')
                    yield f'data: {data}\n\n'
                    time_since_keepalive = 0

                    # Check if task is done — stop streaming
                    try:
                        parsed = json.loads(data)
                        if parsed.get('type') in ('task_completed', 'task_failed', 'agent_error'):
                            # Send final status and close
                            yield f'data: {json.dumps({"type": "stream_end"})}\n\n'
                            break
                    except (json.JSONDecodeError, AttributeError):
                        pass

                elif message['type'] == 'subscribe':
                    # Connection confirmed
                    continue
                else:
                    # Keep-alive ping
                    time_since_keepalive += 1
                    if time_since_keepalive >= keepalive_interval:
                        yield f': keepalive\n\n'
                        time_since_keepalive = 0
                    await asyncio.sleep(1)

        except Exception as e:
            yield f'data: {json.dumps({"type": "error", "message": str(e)})}\n\n'
        finally:
            if pubsub:
                try:
                    await pubsub.unsubscribe(channel)
                    await pubsub.aclose()
                except Exception:
                    pass
            if redis_client:
                try:
                    await redis_client.aclose()
                except Exception:
                    pass

    return StreamingResponse(
        event_generator(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        },
    )


@router.post('/{id}/cancel', response_model=dict)
async def cancel_task(
    id: str,
    db: AsyncSession = Depends(get_async_db),
    ctx: TenantContext = Depends(require_auth),
):
    """Cancel a queued or running task."""
    result = await db.execute(
        select(AgentTask).where(
            AgentTask.id == id,
            AgentTask.tenant_id == ctx.tenant_id,
        )
    )
    task = result.scalars().first()
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')

    if task.status not in ('queued', 'running'):
        raise HTTPException(
            status_code=400,
            detail=f'Task cannot be cancelled in status: {task.status}',
        )

    # Cancel in arq
    try:
        from arq import create_pool
        from arq.connections import RedisSettings
        import os
        redis_settings = RedisSettings.from_dsn(os.getenv('REDIS_URL', 'redis://localhost:6379'))
        pool = await create_pool(redis_settings)
        await pool.cancel_job(id)
        await pool.aclose()
    except Exception as e:
        logger.warning(f'Could not cancel arq job {id}: {e}')

    task.status = 'cancelled'
    task.completed_at = datetime.now(timezone.utc)
    task.error_message = 'Cancelled by user'
    await db.commit()

    return {'data': {'success': True, 'task_id': id, 'status': 'cancelled'}, 'error': None}
