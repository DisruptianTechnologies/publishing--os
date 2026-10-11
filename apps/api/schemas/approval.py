from pydantic import BaseModel, ConfigDict
from typing import Literal
from datetime import datetime

class ApprovalRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    project_id: str
    approval_type: str
    title: str
    description: str
    requested_by: str
    risk_score: float
    evidence_summary: str
    expected_external_effect: str
    estimated_cost_usd: float
    expires_at: datetime | None
    status: str
    artifact_id: str | None
    artifact_version: int
    created_at: datetime
    updated_at: datetime

class ApprovalDecisionCreate(BaseModel):
    decision: Literal['approved', 'rejected']
    reason: str = ''
