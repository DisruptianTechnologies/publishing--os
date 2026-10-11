import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Project(Base):
    __tablename__ = 'projects'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey('tenants.id'), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, default='')
    project_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default='idea')
    target_market: Mapped[str] = mapped_column(String(500), default='')
    idea_description: Mapped[str] = mapped_column(Text, default='')
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_by: Mapped[str] = mapped_column(String(36))
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    
    __table_args__ = (Index('ix_projects_tenant_status', 'tenant_id', 'status'),)
