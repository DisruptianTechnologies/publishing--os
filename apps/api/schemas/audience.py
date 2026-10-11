from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Literal
from datetime import datetime

PLATFORM_TYPES = Literal['reddit', 'twitter_x', 'substack', 'linkedin', 'discord']
CONSENT_TYPES = Literal['email_marketing', 'product_updates', 'analytics_cookies', 'terms_of_service']
LEGAL_BASIS_TYPES = Literal['explicit_opt_in', 'contract', 'legitimate_interest']


class CommunitySourceCreate(BaseModel):
    platform: PLATFORM_TYPES
    source_name: str
    source_url: str
    rules_summary: str = ''
    topic_tags: list[str] = []
    compliance_notes: str = ''


class CommunitySourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    platform: str
    source_name: str
    source_url: str
    rules_summary: str
    topic_tags: list
    status: str
    compliance_notes: str
    created_at: datetime
    updated_at: datetime


class ContentOpportunityCreate(BaseModel):
    source_id: str
    project_id: str | None = None
    opportunity_type: Literal['question', 'discussion', 'trending_topic', 'gap']
    title: str
    url: str = ''
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    intent_class: Literal['informational', 'commercial', 'feedback'] = 'informational'
    notes: str = ''


class ContentOpportunityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    source_id: str
    project_id: str | None
    opportunity_type: str
    title: str
    url: str
    relevance_score: float
    intent_class: str
    status: str
    notes: str
    detected_at: datetime


class ContentDraftCreate(BaseModel):
    project_id: str | None = None
    opportunity_id: str | None = None
    platform: PLATFORM_TYPES
    draft_type: Literal['post', 'reply', 'thread', 'newsletter']
    title: str = ''
    body: str
    variant_options: list[dict] = []


class ContentDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    project_id: str | None
    opportunity_id: str | None
    platform: str
    draft_type: str
    title: str
    body: str
    variant_options: list
    policy_status: str
    policy_flags: list
    status: str
    external_post_id: str | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SubscriberCreate(BaseModel):
    email: str
    first_name: str = ''
    last_name: str = ''
    source: str = 'landing_page'
    tags: list[str] = []
    consent_granted: bool = True
    opt_in_mechanism: str = 'form_submit'


class SubscriberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    email: str
    first_name: str
    last_name: str
    source: str
    status: str
    tags: list
    created_at: datetime
    updated_at: datetime


class ConsentRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    subscriber_id: str
    consent_type: str
    granted: bool
    legal_basis: str
    opt_in_mechanism: str
    ip_address: str
    consent_timestamp: datetime
    revoked_at: datetime | None


class LandingPageCreate(BaseModel):
    project_id: str | None = None
    slug: str
    title: str
    headline: str
    description: str = ''
    template: str = 'clean_minimal'
    form_fields: list[str] = ['email', 'first_name']
    is_published: bool = False


class LandingPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    project_id: str | None
    slug: str
    title: str
    headline: str
    description: str
    template: str
    form_fields: list
    is_published: bool
    analytics_views: int
    analytics_conversions: int
    created_at: datetime
    updated_at: datetime


class NurtureSequenceCreate(BaseModel):
    project_id: str | None = None
    name: str
    trigger_event: Literal['opt_in', 'lead_magnet_download', 'book_purchase', 'manual'] = 'opt_in'
    steps: list[dict] = []


class NurtureSequenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    project_id: str | None
    name: str
    trigger_event: str
    status: str
    total_subscribers: int
    created_at: datetime
    updated_at: datetime


class GlobalKillSwitchToggle(BaseModel):
    scope: Literal['all_outreach', 'email_sending', 'marketplace_publishing', 'social_drafting']
    is_active: bool
    reason: str = ''


class GlobalKillSwitchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    scope: str
    is_active: bool
    activated_by: str | None
    reason: str
    activated_at: datetime | None
    deactivated_at: datetime | None
