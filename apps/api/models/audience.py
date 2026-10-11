import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class CommunitySource(Base):
    __tablename__ = 'community_sources'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50))  # reddit | twitter_x | substack | linkedin | discord
    source_name: Mapped[str] = mapped_column(String(200))  # e.g. r/selfpublish
    source_url: Mapped[str] = mapped_column(String(500))
    rules_summary: Mapped[str] = mapped_column(Text, default='')
    topic_tags: Mapped[list] = mapped_column(JSONB, default=list)
    status: Mapped[str] = mapped_column(String(50), default='active')  # active | monitored | paused
    compliance_notes: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    opportunities: Mapped[list['ContentOpportunity']] = relationship('ContentOpportunity', back_populates='source')


class ContentOpportunity(Base):
    __tablename__ = 'content_opportunities'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey('community_sources.id'), nullable=False, index=True)
    project_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('projects.id'), nullable=True, index=True)
    opportunity_type: Mapped[str] = mapped_column(String(50))  # question | discussion | trending_topic | gap
    title: Mapped[str] = mapped_column(String(400))
    url: Mapped[str] = mapped_column(String(500), default='')
    relevance_score: Mapped[float] = mapped_column(Float, default=0.5)
    intent_class: Mapped[str] = mapped_column(String(50), default='informational')  # informational | commercial | feedback
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    status: Mapped[str] = mapped_column(String(50), default='new')  # new | drafting | addressed | dismissed
    notes: Mapped[str] = mapped_column(Text, default='')

    source: Mapped['CommunitySource'] = relationship('CommunitySource', back_populates='opportunities')
    drafts: Mapped[list['ContentDraft']] = relationship('ContentDraft', back_populates='opportunity')


class ContentDraft(Base):
    __tablename__ = 'content_drafts'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    project_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('projects.id'), nullable=True, index=True)
    opportunity_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('content_opportunities.id'), nullable=True, index=True)
    platform: Mapped[str] = mapped_column(String(50))
    draft_type: Mapped[str] = mapped_column(String(50))  # post | reply | thread | newsletter
    title: Mapped[str] = mapped_column(String(300), default='')
    body: Mapped[str] = mapped_column(Text)
    variant_options: Mapped[list] = mapped_column(JSONB, default=list)
    policy_status: Mapped[str] = mapped_column(String(50), default='compliant')  # compliant | needs_review | blocked
    policy_flags: Mapped[list] = mapped_column(JSONB, default=list)
    status: Mapped[str] = mapped_column(String(50), default='draft')  # draft | waiting_approval | approved | published | rejected
    external_post_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    opportunity: Mapped['ContentOpportunity | None'] = relationship('ContentOpportunity', back_populates='drafts')


class SubscriberProfile(Base):
    __tablename__ = 'subscriber_profiles'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    first_name: Mapped[str] = mapped_column(String(100), default='')
    last_name: Mapped[str] = mapped_column(String(100), default='')
    source: Mapped[str] = mapped_column(String(50), default='landing_page')  # landing_page | lead_magnet | import | direct
    status: Mapped[str] = mapped_column(String(50), default='active')  # active | unconfirmed | unsubscribed | suppressed | bounced
    tags: Mapped[list] = mapped_column(JSONB, default=list)
    metadata_bag: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    consents: Mapped[list['ConsentRecord']] = relationship('ConsentRecord', back_populates='subscriber')


class ConsentRecord(Base):
    __tablename__ = 'consent_records'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    subscriber_id: Mapped[str] = mapped_column(String(36), ForeignKey('subscriber_profiles.id'), nullable=False, index=True)
    consent_type: Mapped[str] = mapped_column(String(50))  # email_marketing | product_updates | analytics_cookies | terms_of_service
    granted: Mapped[bool] = mapped_column(Boolean, default=True)
    legal_basis: Mapped[str] = mapped_column(String(50), default='explicit_opt_in')  # explicit_opt_in | contract | legitimate_interest
    opt_in_mechanism: Mapped[str] = mapped_column(String(50), default='form_submit')  # checkbox | double_opt_in | form_submit
    ip_address: Mapped[str] = mapped_column(String(45), default='')
    user_agent: Mapped[str] = mapped_column(String(300), default='')
    consent_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revocation_reason: Mapped[str | None] = mapped_column(String(200), nullable=True)

    subscriber: Mapped['SubscriberProfile'] = relationship('SubscriberProfile', back_populates='consents')


class LandingPage(Base):
    __tablename__ = 'landing_pages'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    project_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('projects.id'), nullable=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), index=True)
    title: Mapped[str] = mapped_column(String(200))
    headline: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, default='')
    template: Mapped[str] = mapped_column(String(50), default='clean_minimal')
    hero_artifact_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    lead_magnet_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    form_fields: Mapped[list] = mapped_column(JSONB, default=lambda: ['email', 'first_name'])
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    analytics_views: Mapped[int] = mapped_column(Integer, default=0)
    analytics_conversions: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class NurtureSequence(Base):
    __tablename__ = 'nurture_sequences'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    project_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('projects.id'), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    trigger_event: Mapped[str] = mapped_column(String(50), default='opt_in')  # opt_in | lead_magnet_download | book_purchase | manual
    status: Mapped[str] = mapped_column(String(50), default='draft')  # draft | active | paused
    total_subscribers: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    steps: Mapped[list['NurtureStep']] = relationship('NurtureStep', back_populates='sequence', order_by='NurtureStep.step_order')


class NurtureStep(Base):
    __tablename__ = 'nurture_steps'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sequence_id: Mapped[str] = mapped_column(String(36), ForeignKey('nurture_sequences.id'), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    step_order: Mapped[int] = mapped_column(Integer, default=1)
    delay_hours: Mapped[int] = mapped_column(Integer, default=24)
    subject: Mapped[str] = mapped_column(String(300))
    body_template: Mapped[str] = mapped_column(Text)
    required_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(50), default='active')  # active | paused
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    sequence: Mapped['NurtureSequence'] = relationship('NurtureSequence', back_populates='steps')


class GlobalKillSwitch(Base):
    __tablename__ = 'global_kill_switches'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(50))  # all_outreach | email_sending | marketplace_publishing | social_drafting
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)  # True = traffic/actions killed
    activated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    reason: Mapped[str] = mapped_column(Text, default='')
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
