import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class ApprovalRequest(Base):
    __tablename__ = 'approval_requests'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey('projects.id'), nullable=False, index=True)
    workflow_run_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('workflow_runs.id'), nullable=True)
    task_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('agent_tasks.id'), nullable=True)
    artifact_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('artifacts.id'), nullable=True)
    artifact_version: Mapped[int] = mapped_column(Integer, default=0)
    approval_type: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text)
    requested_by: Mapped[str] = mapped_column(String(100))
    assigned_to_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    policy_result: Mapped[dict] = mapped_column(JSONB, default=dict)
    evidence_summary: Mapped[str] = mapped_column(Text, default='')
    expected_external_effect: Mapped[str] = mapped_column(Text, default='')
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default='pending')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    decisions: Mapped[list['ApprovalDecision']] = relationship('ApprovalDecision', back_populates='request')

class ApprovalDecision(Base):
    __tablename__ = 'approval_decisions'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(String(36), ForeignKey('approval_requests.id'), nullable=False, index=True)
    decided_by_user_id: Mapped[str] = mapped_column(String(36))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    decision: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str] = mapped_column(Text, default='')
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    request: Mapped['ApprovalRequest'] = relationship('ApprovalRequest', back_populates='decisions')
