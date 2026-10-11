from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from datetime import datetime

MARKETPLACE_TYPES = Literal['kdp', 'etsy', 'ingram', 'gumroad', 'shopify']
AUTH_STATUS_TYPES = Literal['pending_authorization', 'authorized', 'revoked', 'expired']
LISTING_STATUS_TYPES = Literal['draft', 'pending_approval', 'publishing', 'live', 'delisted', 'error']
JOB_STATUS_TYPES = Literal['queued', 'waiting_approval', 'in_progress', 'completed', 'failed', 'cancelled']


class MarketplaceAccountCreate(BaseModel):
    marketplace: MARKETPLACE_TYPES
    name: str
    credentials: dict = {}


class MarketplaceAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    marketplace: str
    name: str
    auth_status: str
    rate_limit_remaining: int
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime


class MarketplaceListingCreate(BaseModel):
    project_id: str
    account_id: str
    marketplace: MARKETPLACE_TYPES
    title: str
    price_usd: float = Field(default=9.99, ge=0.0)
    currency: str = 'USD'
    metadata_snapshot: dict = {}


class MarketplaceListingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    project_id: str
    account_id: str
    marketplace: str
    external_listing_id: str | None
    status: str
    listing_url: str | None
    title: str
    price_usd: float
    currency: str
    metadata_snapshot: dict
    compliance_audit_id: str | None
    created_at: datetime
    updated_at: datetime


class PublishingJobCreate(BaseModel):
    project_id: str
    listing_id: str | None = None
    account_id: str
    job_type: Literal['create_listing', 'update_metadata', 'upload_package', 'price_change']
    payload: dict = {}


class PublishingJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    project_id: str
    listing_id: str | None
    account_id: str
    job_type: str
    idempotency_key: str
    status: str
    payload: dict
    result: dict
    error_message: str | None
    attempts: int
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PackagePreflightRequest(BaseModel):
    project_id: str
    package_type: Literal['kdp_ebook', 'kdp_paperback', 'etsy_printable', 'generic_epub']
    interior_artifact_id: str | None = None
    cover_artifact_id: str | None = None
    metadata_artifact_id: str | None = None


class PackagePreflightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    project_id: str
    package_type: str
    preflight_status: str
    preflight_report: dict
    checksum: str
    created_at: datetime
