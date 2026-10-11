from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ArtifactVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    artifact_id: str
    version: int
    content_type: str
    size_bytes: int
    checksum: str
    structured_data: dict
    creator_agent: str
    model_name: str
    provider_name: str
    token_usage: int
    cost_usd: float
    confidence: float
    citations: list
    created_at: datetime

class ArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    project_id: str
    artifact_type: str
    name: str
    description: str
    current_version: int
    approval_state: str
    compliance_state: str
    created_at: datetime
    updated_at: datetime
    current_version_detail: ArtifactVersionResponse | None = None
