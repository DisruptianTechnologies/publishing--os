"""
arq background worker — routes agent tasks to their specialist agents.
"""
from __future__ import annotations
import os
import sys
import json
import logging
import asyncio
from datetime import datetime, timezone
from arq.connections import RedisSettings
import redis.asyncio as aioredis

# Add root and packages to path so agents and llm_gateway can be imported
_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
_packages_dir = os.path.join(_root_dir, 'packages')
sys.path.insert(0, _root_dir)
sys.path.insert(0, _packages_dir)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logger = logging.getLogger(__name__)

# Agent registry — maps agent_type string to class
def _build_agent_registry():
    try:
        try:
            from packages.agents.research import ResearchAgent
            from packages.agents.strategy import StrategyAgent
            from packages.agents.outline import OutlineAgent
            from packages.agents.writing import WritingAgent
            from packages.agents.editing import EditingAgent
            from packages.agents.formatting import FormattingAgent
            from packages.agents.metadata import MetadataAgent
            from packages.agents.compliance import ComplianceAgent
        except ImportError:
            from agents.research import ResearchAgent
            from agents.strategy import StrategyAgent
            from agents.outline import OutlineAgent
            from agents.writing import WritingAgent
            from agents.editing import EditingAgent
            from agents.formatting import FormattingAgent
            from agents.metadata import MetadataAgent
            from agents.compliance import ComplianceAgent

        return {
            'research_agent': ResearchAgent,
            'strategy_agent': StrategyAgent,
            'outline_agent': OutlineAgent,
            'writing_agent': WritingAgent,
            'editing_agent': EditingAgent,
            'formatting_agent': FormattingAgent,
            'metadata_agent': MetadataAgent,
            'compliance_agent': ComplianceAgent,
        }
    except Exception as e:
        logger.warning(f'Could not import agents: {e}. Running in stub mode.')
        return {}

AGENT_REGISTRY = _build_agent_registry()


async def _publish(redis_client, channel: str, message: dict):
    """Publish a JSON message to a Redis pub/sub channel."""
    try:
        await redis_client.publish(channel, json.dumps(message))
    except Exception as e:
        logger.error(f'Failed to publish to {channel}: {e}')


async def run_agent_task(ctx, task_id: str):
    """
    Main worker function. Loads task from DB, routes to correct agent,
    stores output artifact, triggers workflow progression.
    """
    from sqlalchemy.ext.asyncio import AsyncSession
    from core.database import AsyncSessionLocal
    from models.agent import AgentTask, WorkflowRun
    from models.artifact import Artifact, ArtifactVersion
    from services.workflow_service import handle_task_completion
    from services.audit_service import log_action, record_usage
    import hashlib, uuid

    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    redis_client = await aioredis.from_url(redis_url)
    log_channel = f'task:{task_id}:logs'

    async with AsyncSessionLocal() as db:
        try:
            # 1. Load task
            from sqlalchemy import select
            result = await db.execute(select(AgentTask).where(AgentTask.id == task_id))
            task = result.scalars().first()
            if not task:
                logger.error(f'Task {task_id} not found')
                return

            # 2. Mark running
            task.status = 'running'
            task.started_at = datetime.now(timezone.utc)
            task.attempt += 1
            await db.commit()

            await _publish(redis_client, log_channel, {
                'type': 'task_started',
                'task_id': task_id,
                'agent_type': task.agent_type,
                'attempt': task.attempt,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

            # 3. Route to agent
            agent_cls = AGENT_REGISTRY.get(task.agent_type)
            if not agent_cls:
                # Stub mode — simulate completion for unknown agents
                logger.warning(f'No agent class for {task.agent_type}, using stub')
                await asyncio.sleep(1)
                result_data = {
                    'stub': True,
                    'agent_type': task.agent_type,
                    'message': 'Agent class not available in worker environment. Install packages/agents dependencies.'
                }
                output_artifact_id = None
            else:
                # 4. Build AgentContext
                try:
                    from packages.agents.base import AgentContext
                except ImportError:
                    from agents.base import AgentContext
                context = AgentContext(
                    tenant_id=task.tenant_id,
                    project_id=task.project_id,
                    task_id=str(task.id),
                    workflow_run_id=str(task.workflow_run_id),
                    token_budget=task.token_budget,
                    cost_budget_usd=task.cost_budget_usd,
                    model_policy=task.model_policy,
                    allowed_tools=list(task.config.get('allowed_tools', [])),
                    extra=task.config,
                )

                await _publish(redis_client, log_channel, {
                    'type': 'agent_starting',
                    'agent_type': task.agent_type,
                    'model_policy': task.model_policy,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })

                # 5. Load input artifacts
                input_data = task.config.get('input_data', {})
                if task.input_artifact_ids:
                    # Load structured_data from first input artifact version
                    from models.artifact import ArtifactVersion
                    for art_id in task.input_artifact_ids:
                        art_res = await db.execute(
                            select(ArtifactVersion)
                            .where(ArtifactVersion.artifact_id == art_id)
                            .order_by(ArtifactVersion.version.desc())
                            .limit(1)
                        )
                        art_ver = art_res.scalars().first()
                        if art_ver and art_ver.structured_data:
                            input_data.update(art_ver.structured_data)

                # Always include project_id
                input_data['project_id'] = task.project_id

                # 6. Execute agent
                agent = agent_cls()
                try:
                    decision = agent.execute(input_data, context)
                    result_data = decision.result.model_dump()

                    await _publish(redis_client, log_channel, {
                        'type': 'agent_completed',
                        'confidence': decision.confidence,
                        'actual_cost_usd': decision.actual_cost_usd,
                        'token_usage': decision.token_usage,
                        'latency_ms': decision.latency_ms,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })

                except Exception as agent_err:
                    retryable = getattr(agent_err, 'retryable', True)
                    logger.error(f'Agent {task.agent_type} failed: {agent_err}')
                    await _publish(redis_client, log_channel, {
                        'type': 'agent_error',
                        'error': str(agent_err),
                        'retryable': retryable,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })

                    if retryable and task.attempt < task.max_attempts:
                        task.status = 'queued'  # Will be retried
                        task.error_message = str(agent_err)
                    else:
                        task.status = 'failed'
                        task.error_code = getattr(agent_err, 'code', 'agent_error')
                        task.error_message = str(agent_err)
                        task.completed_at = datetime.now(timezone.utc)
                        workflow = await db.get(WorkflowRun, task.workflow_run_id)
                        if workflow:
                            workflow.status = 'failed'
                            workflow.error_message = str(agent_err)
                    await db.commit()
                    return

                # 7. Store output artifact
                content_str = json.dumps(result_data, indent=2)
                content_bytes = content_str.encode('utf-8')
                checksum = hashlib.sha256(content_bytes).hexdigest()
                artifact_id = str(uuid.uuid4())
                storage_key = f'{task.tenant_id}/{task.project_id}/{artifact_id}/v1.json'

                # Try to save to storage
                try:
                    from core.storage import get_storage
                    storage = get_storage()
                    await storage.save(storage_key, content_str)
                except Exception as store_err:
                    logger.warning(f'Storage save failed, continuing: {store_err}')
                    storage_key = f'memory:{artifact_id}'

                artifact = Artifact(
                    id=artifact_id,
                    tenant_id=task.tenant_id,
                    project_id=task.project_id,
                    artifact_type=task.agent_type.replace('_agent', '_output'),
                    name=f'{task.agent_type} output',
                    description=f'Output from {task.agent_type} run {task.workflow_run_id}',
                    current_version=1,
                    approval_state='draft',
                    compliance_state='unchecked',
                )
                db.add(artifact)
                await db.flush()

                version = ArtifactVersion(
                    artifact_id=artifact_id,
                    tenant_id=task.tenant_id,
                    project_id=task.project_id,
                    version=1,
                    content_location=storage_key,
                    content_type='application/json',
                    size_bytes=len(content_bytes),
                    checksum=checksum,
                    structured_data=result_data,
                    creator_agent=task.agent_type,
                    model_name=decision.model,
                    provider_name=decision.provider,
                    prompt_version=decision.prompt_version,
                    token_usage=decision.token_usage,
                    cost_usd=decision.actual_cost_usd,
                    confidence=decision.confidence,
                    citations=[],
                    parent_artifact_ids=list(task.input_artifact_ids or []),
                )
                db.add(version)
                await db.commit()
                output_artifact_id = artifact_id

                # 8. Record usage
                await record_usage(
                    db, task.tenant_id, task.project_id,
                    resource_type='llm_tokens',
                    quantity=decision.token_usage,
                    unit_cost_usd=decision.actual_cost_usd / max(decision.token_usage, 1),
                    model_name=decision.model,
                    provider_name=decision.provider,
                    workflow_run_id=str(task.workflow_run_id),
                    agent_task_id=str(task.id),
                )

                # Update task with output
                task.token_usage = decision.token_usage
                task.cost_usd = decision.actual_cost_usd
                task.output_artifact_ids = [output_artifact_id]

            # 9. Mark task complete and progress workflow
            task.status = 'completed'
            task.completed_at = datetime.now(timezone.utc)
            await db.commit()

            await _publish(redis_client, log_channel, {
                'type': 'task_completed',
                'output_artifact_id': output_artifact_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })

            # 10. Progress workflow
            await handle_task_completion(
                db, task_id, output_artifact_id or '', result_data
            )

            # 11. Audit log
            await log_action(
                db, task.tenant_id, 'agent', task.agent_type,
                'task_completed', 'agent_task', task_id,
                {'output_artifact_id': output_artifact_id, 'cost_usd': task.cost_usd}
            )

        except Exception as e:
            logger.exception(f'Unhandled error in run_agent_task {task_id}: {e}')
            await _publish(redis_client, log_channel, {
                'type': 'task_failed',
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            # Mark task failed
            try:
                async with AsyncSessionLocal() as db2:
                    from sqlalchemy import select
                    r = await db2.execute(select(AgentTask).where(AgentTask.id == task_id))
                    t = r.scalars().first()
                    if t:
                        t.status = 'failed'
                        t.error_message = str(e)
                        t.completed_at = datetime.now(timezone.utc)
                        await db2.commit()
            except Exception:
                pass
        finally:
            await redis_client.aclose()


async def startup(ctx):
    logger.info('Worker starting up')


async def shutdown(ctx):
    logger.info('Worker shutting down')


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(os.getenv('REDIS_URL', 'redis://localhost:6379'))
    functions = [run_agent_task]
    queue_name = 'kindlepreneur'
    max_jobs = 10
    job_timeout = 600
    keep_result = 3600
    on_startup = startup
    on_shutdown = shutdown
