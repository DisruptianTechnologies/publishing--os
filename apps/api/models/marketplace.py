import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class MarketplaceAccount(Base):
    __tablename__ = 'marketplace_accounts'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    marketplace: Mapped[str] = mapped_column(String(50))  # kdp | etsy | ingram | gumroad | shopify
    name: Mapped[str] = mapped_column(String(200))
    auth_status: Mapped[str] = mapped_column(String(50), default='pending_authorization')  # pending_authorization | authorized | revoked | expired
    credentials: Mapped[dict] = mapped_column(JSONB, default=dict)
    rate_limit_remaining: Mapped[int] = mapped_column(Integer, default=100)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    listings: Mapped[list['MarketplaceListing']] = relationship('MarketplaceListing', back_populates='account')
    jobs: Mapped[list['PublishingJob']] = relationship('PublishingJob', back_populates='account')


class MarketplaceListing(Base):
    __tablename__ = 'marketplace_listings'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey('projects.id'), nullable=False, index=True)
    account_id: Mapped[str] = mapped_column(String(36), ForeignKey('marketplace_accounts.id'), nullable=False, index=True)
    marketplace: Mapped[str] = mapped_column(String(50))
    external_listing_id: Mapped[str | None] = mapped_column(String(100), nullable=True)  # ASIN or Etsy Listing ID
    status: Mapped[str] = mapped_column(String(50), default='draft')  # draft | pending_approval | publishing | live | delisted | error
    listing_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    title: Mapped[str] = mapped_column(String(300))
    price_usd: Mapped[float] = mapped_column(Float, default=9.99)
    currency: Mapped[str] = mapped_column(String(10), default='USD')
    metadata_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict)
    compliance_audit_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    account: Mapped['MarketplaceAccount'] = relationship('MarketplaceAccount', back_populates='listings')
    jobs: Mapped[list['PublishingJob']] = relationship('PublishingJob', back_populates='listing')


class PublishingJob(Base):
    __tablename__ = 'publishing_jobs'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey('projects.id'), nullable=False, index=True)
    listing_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('marketplace_listings.id'), nullable=True, index=True)
    account_id: Mapped[str] = mapped_column(String(36), ForeignKey('marketplace_accounts.id'), nullable=False, index=True)
    job_type: Mapped[str] = mapped_column(String(50))  # create_listing | update_metadata | upload_package | price_change
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default='queued')  # queued | waiting_approval | in_progress | completed | failed | cancelled
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    result: Mapped[dict] = mapped_column(JSONB, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    account: Mapped['MarketplaceAccount'] = relationship('MarketplaceAccount', back_populates='jobs')
    listing: Mapped['MarketplaceListing | None'] = relationship('MarketplaceListing', back_populates='jobs')


class MarketplacePackage(Base):
    __tablename__ = 'marketplace_packages'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey('projects.id'), nullable=False, index=True)
    package_type: Mapped[str] = mapped_column(String(50))  # kdp_ebook | kdp_paperback | etsy_printable | generic_epub
    interior_artifact_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    cover_artifact_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    metadata_artifact_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    preflight_status: Mapped[str] = mapped_column(String(50), default='pending')  # passed | warnings | failed
    preflight_report: Mapped[dict] = mapped_column(JSONB, default=dict)
    storage_location: Mapped[str] = mapped_column(String(500), default='')
    checksum: Mapped[str] = mapped_column(String(64), default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
