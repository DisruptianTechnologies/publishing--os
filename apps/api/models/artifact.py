import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Artifact(Base):
    __tablename__ = 'artifacts'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey('projects.id'), nullable=False, index=True)
    artifact_type: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, default='')
    current_version: Mapped[int] = mapped_column(Integer, default=0)
    approval_state: Mapped[str] = mapped_column(String(50), default='draft')
    compliance_state: Mapped[str] = mapped_column(String(50), default='unchecked')
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    versions: Mapped[list['ArtifactVersion']] = relationship('ArtifactVersion', back_populates='artifact', order_by='ArtifactVersion.version')

class ArtifactVersion(Base):
    __tablename__ = 'artifact_versions'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    artifact_id: Mapped[str] = mapped_column(String(36), ForeignKey('artifacts.id'), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(36), nullable=False)
    version: Mapped[int] = mapped_column(Integer)
    content_location: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(100), default='text/markdown')
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    checksum: Mapped[str] = mapped_column(String(64))
    structured_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    creator_agent: Mapped[str] = mapped_column(String(100), default='')
    creator_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    model_name: Mapped[str] = mapped_column(String(100), default='')
    provider_name: Mapped[str] = mapped_column(String(50), default='')
    prompt_version: Mapped[str] = mapped_column(String(50), default='')
    token_usage: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    citations: Mapped[list] = mapped_column(JSONB, default=list)
    parent_artifact_ids: Mapped[list] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    artifact: Mapped['Artifact'] = relationship('Artifact', back_populates='versions')
