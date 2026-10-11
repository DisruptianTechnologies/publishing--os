"""Phase 2 Marketplace Studio and AudienceOS database migration

Revision ID: 002_phase2_marketplace_audience
Revises: 001_initial_schema
Create Date: 2026-10-11 08:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_phase2_marketplace_audience'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. marketplace_accounts
    op.create_table(
        'marketplace_accounts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('marketplace', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('auth_status', sa.String(length=50), nullable=False, server_default='pending_authorization'),
        sa.Column('credentials', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('rate_limit_remaining', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_marketplace_accounts_tenant_id', 'marketplace_accounts', ['tenant_id'])

    # 2. marketplace_listings
    op.create_table(
        'marketplace_listings',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('project_id', sa.String(length=36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('account_id', sa.String(length=36), sa.ForeignKey('marketplace_accounts.id'), nullable=False),
        sa.Column('marketplace', sa.String(length=50), nullable=False),
        sa.Column('external_listing_id', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('listing_url', sa.String(length=500), nullable=True),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('price_usd', sa.Float(), nullable=False, server_default='9.99'),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('metadata_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('compliance_audit_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_marketplace_listings_tenant_id', 'marketplace_listings', ['tenant_id'])
    op.create_index('ix_marketplace_listings_project_id', 'marketplace_listings', ['project_id'])
    op.create_index('ix_marketplace_listings_account_id', 'marketplace_listings', ['account_id'])

    # 3. publishing_jobs
    op.create_table(
        'publishing_jobs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('project_id', sa.String(length=36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('listing_id', sa.String(length=36), sa.ForeignKey('marketplace_listings.id'), nullable=True),
        sa.Column('account_id', sa.String(length=36), sa.ForeignKey('marketplace_accounts.id'), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('idempotency_key', sa.String(length=100), nullable=False, unique=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='queued'),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_publishing_jobs_tenant_id', 'publishing_jobs', ['tenant_id'])
    op.create_index('ix_publishing_jobs_project_id', 'publishing_jobs', ['project_id'])
    op.create_index('ix_publishing_jobs_account_id', 'publishing_jobs', ['account_id'])
    op.create_index('ix_publishing_jobs_listing_id', 'publishing_jobs', ['listing_id'])
    op.create_index('ix_publishing_jobs_idempotency_key', 'publishing_jobs', ['idempotency_key'])

    # 4. marketplace_packages
    op.create_table(
        'marketplace_packages',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('project_id', sa.String(length=36), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('package_type', sa.String(length=50), nullable=False),
        sa.Column('interior_artifact_id', sa.String(length=36), nullable=True),
        sa.Column('cover_artifact_id', sa.String(length=36), nullable=True),
        sa.Column('metadata_artifact_id', sa.String(length=36), nullable=True),
        sa.Column('preflight_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('preflight_report', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('storage_location', sa.String(length=500), nullable=False, server_default=''),
        sa.Column('checksum', sa.String(length=64), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_marketplace_packages_tenant_id', 'marketplace_packages', ['tenant_id'])
    op.create_index('ix_marketplace_packages_project_id', 'marketplace_packages', ['project_id'])

    # 5. community_sources
    op.create_table(
        'community_sources',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('source_name', sa.String(length=200), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=False),
        sa.Column('rules_summary', sa.Text(), nullable=False, server_default=''),
        sa.Column('topic_tags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('compliance_notes', sa.Text(), nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_community_sources_tenant_id', 'community_sources', ['tenant_id'])

    # 6. content_opportunities
    op.create_table(
        'content_opportunities',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('source_id', sa.String(length=36), sa.ForeignKey('community_sources.id'), nullable=False),
        sa.Column('project_id', sa.String(length=36), sa.ForeignKey('projects.id'), nullable=True),
        sa.Column('opportunity_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=400), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False, server_default=''),
        sa.Column('relevance_score', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('intent_class', sa.String(length=50), nullable=False, server_default='informational'),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='new'),
        sa.Column('notes', sa.Text(), nullable=False, server_default=''),
    )
    op.create_index('ix_content_opportunities_tenant_id', 'content_opportunities', ['tenant_id'])
    op.create_index('ix_content_opportunities_source_id', 'content_opportunities', ['source_id'])
    op.create_index('ix_content_opportunities_project_id', 'content_opportunities', ['project_id'])

    # 7. content_drafts
    op.create_table(
        'content_drafts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('project_id', sa.String(length=36), sa.ForeignKey('projects.id'), nullable=True),
        sa.Column('opportunity_id', sa.String(length=36), sa.ForeignKey('content_opportunities.id'), nullable=True),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('draft_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False, server_default=''),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('variant_options', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('policy_status', sa.String(length=50), nullable=False, server_default='compliant'),
        sa.Column('policy_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('external_post_id', sa.String(length=200), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_content_drafts_tenant_id', 'content_drafts', ['tenant_id'])
    op.create_index('ix_content_drafts_project_id', 'content_drafts', ['project_id'])
    op.create_index('ix_content_drafts_opportunity_id', 'content_drafts', ['opportunity_id'])

    # 8. subscriber_profiles
    op.create_table(
        'subscriber_profiles',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False, server_default=''),
        sa.Column('last_name', sa.String(length=100), nullable=False, server_default=''),
        sa.Column('source', sa.String(length=50), nullable=False, server_default='landing_page'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column('metadata_bag', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_subscriber_profiles_tenant_id', 'subscriber_profiles', ['tenant_id'])
    op.create_index('ix_subscriber_profiles_email', 'subscriber_profiles', ['email'])

    # 9. consent_records
    op.create_table(
        'consent_records',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('subscriber_id', sa.String(length=36), sa.ForeignKey('subscriber_profiles.id'), nullable=False),
        sa.Column('consent_type', sa.String(length=50), nullable=False),
        sa.Column('granted', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('legal_basis', sa.String(length=50), nullable=False, server_default='explicit_opt_in'),
        sa.Column('opt_in_mechanism', sa.String(length=50), nullable=False, server_default='form_submit'),
        sa.Column('ip_address', sa.String(length=45), nullable=False, server_default=''),
        sa.Column('user_agent', sa.String(length=300), nullable=False, server_default=''),
        sa.Column('consent_timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revocation_reason', sa.String(length=200), nullable=True),
    )
    op.create_index('ix_consent_records_tenant_id', 'consent_records', ['tenant_id'])
    op.create_index('ix_consent_records_subscriber_id', 'consent_records', ['subscriber_id'])

    # 10. landing_pages
    op.create_table(
        'landing_pages',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('project_id', sa.String(length=36), sa.ForeignKey('projects.id'), nullable=True),
        sa.Column('slug', sa.String(length=120), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('headline', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=False, server_default=''),
        sa.Column('template', sa.String(length=50), nullable=False, server_default='clean_minimal'),
        sa.Column('hero_artifact_id', sa.String(length=36), nullable=True),
        sa.Column('lead_magnet_id', sa.String(length=36), nullable=True),
        sa.Column('form_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[\"email\", \"first_name\"]'::jsonb")),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('analytics_views', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('analytics_conversions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_landing_pages_tenant_id', 'landing_pages', ['tenant_id'])
    op.create_index('ix_landing_pages_project_id', 'landing_pages', ['project_id'])
    op.create_index('ix_landing_pages_slug', 'landing_pages', ['slug'])

    # 11. nurture_sequences
    op.create_table(
        'nurture_sequences',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('project_id', sa.String(length=36), sa.ForeignKey('projects.id'), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('trigger_event', sa.String(length=50), nullable=False, server_default='opt_in'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('total_subscribers', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_nurture_sequences_tenant_id', 'nurture_sequences', ['tenant_id'])
    op.create_index('ix_nurture_sequences_project_id', 'nurture_sequences', ['project_id'])

    # 12. nurture_steps
    op.create_table(
        'nurture_steps',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('sequence_id', sa.String(length=36), sa.ForeignKey('nurture_sequences.id'), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('delay_hours', sa.Integer(), nullable=False, server_default='24'),
        sa.Column('subject', sa.String(length=300), nullable=False),
        sa.Column('body_template', sa.Text(), nullable=False),
        sa.Column('required_approval', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_nurture_steps_sequence_id', 'nurture_steps', ['sequence_id'])
    op.create_index('ix_nurture_steps_tenant_id', 'nurture_steps', ['tenant_id'])

    # 13. global_kill_switches
    op.create_table(
        'global_kill_switches',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('tenant_id', sa.String(length=36), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('scope', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('activated_by', sa.String(length=36), nullable=True),
        sa.Column('reason', sa.Text(), nullable=False, server_default=''),
        sa.Column('activated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deactivated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_global_kill_switches_tenant_id', 'global_kill_switches', ['tenant_id'])


def downgrade() -> None:
    op.drop_table('global_kill_switches')
    op.drop_table('nurture_steps')
    op.drop_table('nurture_sequences')
    op.drop_table('landing_pages')
    op.drop_table('consent_records')
    op.drop_table('subscriber_profiles')
    op.drop_table('content_drafts')
    op.drop_table('content_opportunities')
    op.drop_table('community_sources')
    op.drop_table('marketplace_packages')
    op.drop_table('publishing_jobs')
    op.drop_table('marketplace_listings')
    op.drop_table('marketplace_accounts')
