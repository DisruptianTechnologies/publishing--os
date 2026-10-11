"""
Workflow orchestration service.
Manages workflow lifecycle: start, task completion, approval decisions, sequence progression.
"""
from __future__ import annotations
import json
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.agent import AgentTask, WorkflowRun, WorkflowEvent
from models.approval import ApprovalRequest, ApprovalDecision
from models.project import Project
from typing import Literal

logger = logging.getLogger(__name__)

# Ordered sequences: list of (agent_type, approval_policy)
WORKFLOW_SEQUENCES: dict[str, list[tuple[str, str]]] = {
    'research':    [('research_agent',    'required')],
    'strategy':   [('strategy_agent',    'required')],
    'outline':    [('outline_agent',     'required')],
    'writing':    [('writing_agent',     'optional')],
    'editing':    [('editing_agent',     'optional')],
    'formatting': [('formatting_agent',  'none')],
    'metadata':   [('metadata_agent',    'none')],
    'compliance': [('compliance_agent',  'required')],
    'full_pipeline': [
        ('research_agent',   'required'),
        ('strategy_agent',   'required'),
        ('outline_agent',    'required'),
        ('writing_agent',    'optional'),
        ('editing_agent',    'optional'),
        ('formatting_agent', 'none'),
        ('metadata_agent',   'none'),
        ('compliance_agent', 'required'),
    ],
}

# Project status that maps to each agent completing
AGENT_TO_PROJECT_STATUS: dict[str, str] = {
    'research_agent':   'researching',
    'strategy_agent':   'strategy',
    'outline_agent':    'outlining',
    'writing_agent':    'writing',
    'editing_agent':    'editing',
    'formatting_agent': 'formatting',
    'metadata_agent':   'metadata',
    'compliance_agent': 'compliance',
}


async def _enqueue_task(task_id: str) -> bool:
    """
    Enqueue an agent task into arq via Redis.
    Returns True on success, False if Redis unavailable (logs warning).
    """
    import os
    try:
        from arq import create_pool
        from arq.connections import RedisSettings
        redis_settings = RedisSettings.from_dsn(os.getenv('REDIS_URL', 'redis://localhost:6379'))
        pool = await create_pool(redis_settings)
        await pool.enqueue_job('run_agent_task', task_id, _queue_name='kindlepreneur')
        await pool.aclose()
        logger.info(f'Enqueued task {task_id}')
        return True
    except Exception as e:
        logger.warning(f'Could not enqueue task {task_id} (worker may be unavailable): {e}')
        return False


async def _add_event(db: AsyncSession, workflow_run_id: str, tenant_id: str, event_type: str, payload: dict):
    """Add a WorkflowEvent record."""
    event = WorkflowEvent(
        workflow_run_id=workflow_run_id,
        tenant_id=tenant_id,
        event_type=event_type,
        payload=payload,
    )
    db.add(event)


async def _get_sequence_index(workflow_type: str, agent_type: str) -> int:
    """Return the index of agent_type in the workflow sequence, or -1."""
    seq = WORKFLOW_SEQUENCES.get(workflow_type, [])
    for i, (a, _) in enumerate(seq):
        if a == agent_type:
            return i
    return -1


async def start_workflow(
    db: AsyncSession,
    tenant_id: str,
    project_id: str,
    workflow_type: str,
    config: dict,
    user_id: str,
) -> WorkflowRun:
    """Create a WorkflowRun, create and enqueue the first AgentTask."""
    sequence = WORKFLOW_SEQUENCES.get(workflow_type)
    if not sequence:
        raise ValueError(f'Unknown workflow type: {workflow_type}')

    from core.config import settings

    workflow = WorkflowRun(
        tenant_id=tenant_id,
        project_id=project_id,
        workflow_type=workflow_type,
        config=config,
        status='running',
        started_at=datetime.now(timezone.utc),
    )
    db.add(workflow)
    await db.flush()

    # Update project status
    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalars().first()
    if project:
        new_status = AGENT_TO_PROJECT_STATUS.get(sequence[0][0], project.status)
        project.status = new_status

    first_agent_type, first_approval_policy = sequence[0]
    task = AgentTask(
        tenant_id=tenant_id,
        project_id=project_id,
        workflow_run_id=str(workflow.id),
        agent_type=first_agent_type,
        approval_policy=first_approval_policy,
        status='queued',
        token_budget=config.get('token_budget', settings.DEFAULT_TOKEN_BUDGET),
        cost_budget_usd=config.get('cost_budget_usd', settings.DEFAULT_COST_BUDGET_USD),
        model_policy=config.get('model_policy', 'large'),
        config=config,
    )
    db.add(task)
    await db.flush()

    await _add_event(db, str(workflow.id), tenant_id, 'workflow_started', {
        'workflow_type': workflow_type,
        'first_agent': first_agent_type,
        'task_id': str(task.id),
        'started_by': user_id,
    })

    await db.commit()
    await db.refresh(workflow)

    # Enqueue to arq (non-blocking — worker handles execution)
    await _enqueue_task(str(task.id))

    return workflow


async def handle_task_completion(
    db: AsyncSession,
    task_id: str,
    output_artifact_id: str,
    result_data: dict,
):
    """
    Called when an agent task completes successfully.
    - If approval_policy == 'required': create ApprovalRequest, pause workflow.
    - Else: find next task in sequence, create and enqueue it.
    - If last task: mark workflow completed, advance project status.
    """
    task_result = await db.execute(select(AgentTask).where(AgentTask.id == task_id))
    task = task_result.scalars().first()
    if not task:
        logger.error(f'handle_task_completion: task {task_id} not found')
        return

    workflow_result = await db.execute(select(WorkflowRun).where(WorkflowRun.id == task.workflow_run_id))
    workflow = workflow_result.scalars().first()
    if not workflow:
        logger.error(f'handle_task_completion: workflow {task.workflow_run_id} not found')
        return

    # Mark task completed (may already be set by worker)
    if task.status != 'completed':
        task.status = 'completed'
        task.completed_at = datetime.now(timezone.utc)
        if output_artifact_id:
            task.output_artifact_ids = [output_artifact_id]

    # Determine position in sequence
    sequence = WORKFLOW_SEQUENCES.get(workflow.workflow_type, [])
    current_index = await _get_sequence_index(workflow.workflow_type, task.agent_type)
    next_index = current_index + 1
    is_last = next_index >= len(sequence)

    if task.approval_policy == 'required':
        # Create approval request and pause workflow
        approval = ApprovalRequest(
            tenant_id=task.tenant_id,
            project_id=str(task.project_id),
            workflow_run_id=str(task.workflow_run_id),
            task_id=str(task.id),
            artifact_id=output_artifact_id if output_artifact_id else None,
            artifact_version=1,
            approval_type=task.agent_type.replace('_agent', ''),
            title=f'Review {task.agent_type.replace("_", " ").title()} Output',
            description=(
                f'The {task.agent_type} has completed its work. '
                f'Please review the output and approve or reject to continue the pipeline.'
            ),
            requested_by=task.agent_type,
            risk_score=0.3,
            evidence_summary=json.dumps(result_data, indent=2)[:2000],
            expected_external_effect='Workflow will advance to next stage upon approval.',
            estimated_cost_usd=task.cost_usd or 0.0,
        )
        db.add(approval)
        workflow.status = 'waiting_approval'

        await _add_event(db, str(workflow.id), str(task.tenant_id), 'waiting_approval', {
            'task_id': task_id,
            'agent_type': task.agent_type,
            'approval_type': approval.approval_type,
        })

    elif is_last:
        # Final task — mark workflow complete
        workflow.status = 'completed'
        workflow.completed_at = datetime.now(timezone.utc)

        # Advance project to published/marketing
        project_result = await db.execute(select(Project).where(Project.id == task.project_id))
        project = project_result.scalars().first()
        if project:
            if workflow.workflow_type == 'full_pipeline':
                project.status = 'compliance'  # Ready for final publication gate
            else:
                final_status = AGENT_TO_PROJECT_STATUS.get(task.agent_type)
                if final_status:
                    project.status = final_status

        await _add_event(db, str(workflow.id), str(task.tenant_id), 'workflow_completed', {
            'workflow_type': workflow.workflow_type,
            'final_agent': task.agent_type,
        })

    else:
        # Enqueue next task in sequence
        next_agent_type, next_approval_policy = sequence[next_index]
        from core.config import settings
        next_task = AgentTask(
            tenant_id=task.tenant_id,
            project_id=task.project_id,
            workflow_run_id=str(task.workflow_run_id),
            agent_type=next_agent_type,
            approval_policy=next_approval_policy,
            status='queued',
            input_artifact_ids=[output_artifact_id] if output_artifact_id else [],
            token_budget=task.token_budget,
            cost_budget_usd=task.cost_budget_usd,
            model_policy=task.model_policy,
            config=workflow.config,
        )
        db.add(next_task)
        await db.flush()

        # Update project status
        project_result = await db.execute(select(Project).where(Project.id == task.project_id))
        project = project_result.scalars().first()
        if project:
            new_status = AGENT_TO_PROJECT_STATUS.get(next_agent_type, project.status)
            project.status = new_status

        workflow.status = 'running'

        await _add_event(db, str(workflow.id), str(task.tenant_id), 'task_queued', {
            'next_agent': next_agent_type,
            'next_task_id': str(next_task.id),
            'sequence_index': next_index,
        })

        await db.commit()
        # Enqueue to arq
        await _enqueue_task(str(next_task.id))
        return  # Already committed above

    await db.commit()


async def handle_approval_decision(
    db: AsyncSession,
    approval_id: str,
    decision: Literal['approved', 'rejected'],
    user_id: str,
    reason: str = '',
):
    """
    Called when a human makes an approval decision.
    - approved: resume workflow by enqueuing next task.
    - rejected: pause workflow, record event.
    """
    approval_result = await db.execute(
        select(ApprovalRequest).where(ApprovalRequest.id == approval_id)
    )
    approval = approval_result.scalars().first()
    if not approval:
        logger.error(f'Approval {approval_id} not found')
        return

    if approval.status not in ('pending',):
        logger.warning(f'Approval {approval_id} already decided: {approval.status}')
        return

    approval.status = decision

    decision_record = ApprovalDecision(
        request_id=str(approval.id),
        tenant_id=str(approval.tenant_id),
        decision=decision,
        decided_by_user_id=user_id,
        reason=reason,
    )
    db.add(decision_record)

    workflow_result = await db.execute(
        select(WorkflowRun).where(WorkflowRun.id == approval.workflow_run_id)
    )
    workflow = workflow_result.scalars().first()

    if workflow:
        if decision == 'approved':
            # Find the completed task this approval was for
            task_result = await db.execute(
                select(AgentTask).where(AgentTask.id == approval.task_id)
            )
            task = task_result.scalars().first()

            if task:
                sequence = WORKFLOW_SEQUENCES.get(workflow.workflow_type, [])
                current_index = await _get_sequence_index(workflow.workflow_type, task.agent_type)
                next_index = current_index + 1
                is_last = next_index >= len(sequence)

                if is_last:
                    workflow.status = 'completed'
                    workflow.completed_at = datetime.now(timezone.utc)
                    await _add_event(db, str(workflow.id), str(workflow.tenant_id), 'workflow_completed', {
                        'final_agent': task.agent_type,
                        'approved_by': user_id,
                    })
                else:
                    next_agent_type, next_approval_policy = sequence[next_index]
                    output_artifact_id = (task.output_artifact_ids or [None])[0]

                    next_task = AgentTask(
                        tenant_id=task.tenant_id,
                        project_id=task.project_id,
                        workflow_run_id=str(task.workflow_run_id),
                        agent_type=next_agent_type,
                        approval_policy=next_approval_policy,
                        status='queued',
                        input_artifact_ids=[output_artifact_id] if output_artifact_id else [],
                        token_budget=task.token_budget,
                        cost_budget_usd=task.cost_budget_usd,
                        model_policy=task.model_policy,
                        config=workflow.config,
                    )
                    db.add(next_task)
                    await db.flush()

                    # Advance project status
                    project_result = await db.execute(
                        select(Project).where(Project.id == task.project_id)
                    )
                    project = project_result.scalars().first()
                    if project:
                        project.status = AGENT_TO_PROJECT_STATUS.get(next_agent_type, project.status)

                    workflow.status = 'running'

                    await _add_event(db, str(workflow.id), str(workflow.tenant_id), 'task_queued_after_approval', {
                        'next_agent': next_agent_type,
                        'next_task_id': str(next_task.id),
                        'approved_by': user_id,
                    })

                    await db.commit()
                    await _enqueue_task(str(next_task.id))
                    return

        else:  # rejected
            workflow.status = 'paused'
            await _add_event(db, str(workflow.id), str(workflow.tenant_id), 'workflow_paused', {
                'reason': 'approval_rejected',
                'rejected_by': user_id,
                'approval_id': approval_id,
                'reason_text': reason,
            })

    await db.commit()
