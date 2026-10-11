"""Initial database schema migration for Kindlepreneur 2.0

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-11 08:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. tenants
    op.create_table(
        'tenants',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False, unique=True),
        sa.Column('plan', sa.String(length=50), nullable=False, server_default='free'),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('feature_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 2. users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('clerk_user_id', sa.String(length=200), nullable=False, unique=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=False, server_default=''),
        sa.Column('roles', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('ix_users_clerk_user_id', 'users', ['clerk_user_id'])

    # 3. projects
    op.create_table(
        'projects',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('name', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('project_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='idea'),
        sa.Column('target_market', sa.String(length=500), nullable=False, server_default=''),
        sa.Column('idea_description', sa.Text(), nullable=False, server_default=''),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_by', sa.String(length=36), nullable=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_projects_tenant_id', 'projects', ['tenant_id'])
    op.create_index('ix_projects_tenant_status', 'projects', ['tenant_id', 'status'])

    # 4. artifacts
    op.create_table(
        'artifacts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('project_id', sa.String(length=36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('artifact_type', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('current_version', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('approval_state', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('compliance_state', sa.String(length=50), nullable=False, server_default='unchecked'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_artifacts_tenant_id', 'artifacts', ['tenant_id'])
    op.create_index('ix_artifacts_project_id', 'artifacts', ['project_id'])

    # 5. artifact_versions
    op.create_table(
        'artifact_versions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('artifact_id', sa.String(length=36), sa.ForeignKey('artifacts.id'), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('content_location', sa.String(length=500), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False, server_default='text/markdown'),
        sa.Column('size_bytes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('checksum', sa.String(length=64), nullable=False),
        sa.Column('structured_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('creator_agent', sa.String(length=100), nullable=False, server_default=''),
        sa.Column('creator_user_id', sa.String(length=36), nullable=True),
        sa.Column('model_name', sa.String(length=100), nullable=False, server_default=''),
        sa.Column('provider_name', sa.String(length=50), nullable=False, server_default=''),
        sa.Column('prompt_version', sa.String(length=50), nullable=False, server_default=''),
        sa.Column('token_usage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cost_usd', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('citations', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('parent_artifact_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_artifact_versions_artifact_id', 'artifact_versions', ['artifact_id'])
    op.create_index('ix_artifact_versions_tenant_id', 'artifact_versions', ['tenant_id'])

    # 6. workflow_runs
    op.create_table(
        'workflow_runs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('workflow_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='queued'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_code', sa.String(length=100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_workflow_runs_tenant_id', 'workflow_runs', ['tenant_id'])
    op.create_index('ix_workflow_runs_project_id', 'workflow_runs', ['project_id'])

    # 7. workflow_events
    op.create_table(
        'workflow_events',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('workflow_run_id', sa.String(length=36), sa.ForeignKey('workflow_runs.id'), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_workflow_events_workflow_run_id', 'workflow_events', ['workflow_run_id'])
    op.create_index('ix_workflow_events_tenant_id', 'workflow_events', ['tenant_id'])

    # 8. agent_tasks
    op.create_table(
        'agent_tasks',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('workflow_run_id', sa.String(length=36), sa.ForeignKey('workflow_runs.id'), nullable=False),
        sa.Column('parent_task_id', sa.String(length=36), nullable=True),
        sa.Column('agent_type', sa.String(length=100), nullable=False),
        sa.Column('input_artifact_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('output_artifact_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='queued'),
        sa.Column('attempt', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('model_policy', sa.String(length=50), nullable=False, server_default='large'),
        sa.Column('token_budget', sa.Integer(), nullable=False, server_default='100000'),
        sa.Column('cost_budget_usd', sa.Float(), nullable=False, server_default='5.0'),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False, server_default='300'),
        sa.Column('approval_policy', sa.String(length=50), nullable=False, server_default='none'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_code', sa.String(length=100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('token_usage', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cost_usd', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_agent_tasks_tenant_id', 'agent_tasks', ['tenant_id'])
    op.create_index('ix_agent_tasks_project_id', 'agent_tasks', ['project_id'])
    op.create_index('ix_agent_tasks_workflow_run_id', 'agent_tasks', ['workflow_run_id'])

    # 9. approval_requests
    op.create_table(
        'approval_requests',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('workflow_run_id', sa.String(length=36), sa.ForeignKey('workflow_runs.id'), nullable=True),
        sa.Column('task_id', sa.String(length=36), sa.ForeignKey('agent_tasks.id'), nullable=True),
        sa.Column('artifact_id', sa.String(length=36), sa.ForeignKey('artifacts.id'), nullable=True),
        sa.Column('artifact_version', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('approval_type', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('requested_by', sa.String(length=100), nullable=False),
        sa.Column('assigned_to_user_id', sa.String(length=36), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('policy_result', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('evidence_summary', sa.Text(), nullable=False, server_default=''),
        sa.Column('expected_external_effect', sa.Text(), nullable=False, server_default=''),
        sa.Column('estimated_cost_usd', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_approval_requests_tenant_id', 'approval_requests', ['tenant_id'])
    op.create_index('ix_approval_requests_project_id', 'approval_requests', ['project_id'])

    # 10. approval_decisions
    op.create_table(
        'approval_decisions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('request_id', sa.String(length=36), sa.ForeignKey('approval_requests.id'), nullable=False),
        sa.Column('decided_by_user_id', sa.String(length=36), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('decision', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False, server_default=''),
        sa.Column('decided_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_approval_decisions_request_id', 'approval_decisions', ['request_id'])
    op.create_index('ix_approval_decisions_tenant_id', 'approval_decisions', ['tenant_id'])

    # 11. audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=True),
        sa.Column('actor_type', sa.String(length=50), nullable=False),
        sa.Column('actor_id', sa.String(length=200), nullable=False),
        sa.Column('action', sa.String(length=200), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.String(length=200), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('ip_address', sa.String(length=45), nullable=False, server_default=''),
        sa.Column('correlation_id', sa.String(length=36), nullable=False, server_default=''),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_audit_logs_tenant_id', 'audit_logs', ['tenant_id'])
    op.create_index('ix_audit_logs_project_id', 'audit_logs', ['project_id'])
    op.create_index('ix_audit_logs_occurred_at', 'audit_logs', ['occurred_at'])

    # 12. usage_records
    op.create_table(
        'usage_records',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('project_id', sa.String(length=36), nullable=True),
        sa.Column('workflow_run_id', sa.String(length=36), nullable=True),
        sa.Column('agent_task_id', sa.String(length=36), nullable=True),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('unit_cost_usd', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_cost_usd', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('model_name', sa.String(length=100), nullable=False, server_default=''),
        sa.Column('provider_name', sa.String(length=50), nullable=False, server_default=''),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_usage_records_tenant_id', 'usage_records', ['tenant_id'])
    op.create_index('ix_usage_records_project_id', 'usage_records', ['project_id'])
    op.create_index('ix_usage_records_recorded_at', 'usage_records', ['recorded_at'])


def downgrade() -> None:
    op.drop_table('usage_records')
    op.drop_table('audit_logs')
    op.drop_table('approval_decisions')
    op.drop_table('approval_requests')
    op.drop_table('agent_tasks')
    op.drop_table('workflow_events')
    op.drop_table('workflow_runs')
    op.drop_table('artifact_versions')
    op.drop_table('artifacts')
    op.drop_table('projects')
    op.drop_table('users')
    op.drop_table('tenants')
