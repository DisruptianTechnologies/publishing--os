import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class WorkflowRun(Base):
    __tablename__ = 'workflow_runs'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey('projects.id'), nullable=False, index=True)
    workflow_type: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default='queued')
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    tasks: Mapped[list['AgentTask']] = relationship('AgentTask', back_populates='workflow_run')
    events: Mapped[list['WorkflowEvent']] = relationship('WorkflowEvent', back_populates='workflow_run')

class WorkflowEvent(Base):
    __tablename__ = 'workflow_events'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_run_id: Mapped[str] = mapped_column(String(36), ForeignKey('workflow_runs.id'), nullable=False, index=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100))
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    workflow_run: Mapped['WorkflowRun'] = relationship('WorkflowRun', back_populates='events')

class AgentTask(Base):
    __tablename__ = 'agent_tasks'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey('projects.id'), nullable=False, index=True)
    workflow_run_id: Mapped[str] = mapped_column(String(36), ForeignKey('workflow_runs.id'), nullable=False, index=True)
    parent_task_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    agent_type: Mapped[str] = mapped_column(String(100))
    input_artifact_ids: Mapped[list] = mapped_column(JSONB, default=list)
    output_artifact_ids: Mapped[list] = mapped_column(JSONB, default=list)
    priority: Mapped[int] = mapped_column(Integer, default=5)
    status: Mapped[str] = mapped_column(String(50), default='queued')
    attempt: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    model_policy: Mapped[str] = mapped_column(String(50), default='large')
    token_budget: Mapped[int] = mapped_column(Integer, default=100000)
    cost_budget_usd: Mapped[float] = mapped_column(Float, default=5.0)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=300)
    approval_policy: Mapped[str] = mapped_column(String(50), default='none')
    config: Mapped[dict] = mapped_column(JSONB, default=dict)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_usage: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    workflow_run: Mapped['WorkflowRun'] = relationship('WorkflowRun', back_populates='tasks')
