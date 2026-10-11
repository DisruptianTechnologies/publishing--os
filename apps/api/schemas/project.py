from pydantic import BaseModel, ConfigDict
from typing import Literal
from datetime import datetime

PROJECT_TYPES = Literal['fiction_book', 'nonfiction_book', 'low_content_journal', 'coloring_book', 'etsy_printable', 'audio_book', 'book_series', 'digital_product']
PROJECT_STATUSES = Literal['idea', 'researching', 'strategy', 'outlining', 'writing', 'editing', 'formatting', 'metadata', 'compliance', 'publishing', 'marketing', 'published', 'paused', 'cancelled']

class ProjectCreate(BaseModel):
    name: str
    description: str = ''
    project_type: PROJECT_TYPES
    target_market: str = ''
    idea_description: str = ''
    settings: dict = {}

class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: PROJECT_STATUSES | None = None
    target_market: str | None = None
    idea_description: str | None = None
    settings: dict | None = None

class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    name: str
    description: str
    project_type: str
    status: str
    target_market: str
    idea_description: str
    settings: dict
    created_by: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime

class WorkflowStartRequest(BaseModel):
    workflow_type: Literal['research', 'strategy', 'outline', 'writing', 'editing', 'formatting', 'metadata', 'compliance', 'publishing', 'marketing', 'full_pipeline']
    config: dict = {}
