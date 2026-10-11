from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from .base import BaseAgent, AgentContext


class EditFinding(BaseModel):
    severity: Literal['critical', 'major', 'minor', 'suggestion']
    location: str  # 'paragraph 3', 'chapter intro', etc.
    problem: str
    evidence: str  # quoted text from the content
    suggested_correction: str
    reason: str
    confidence: float = Field(ge=0, le=1)
    status: Literal['open'] = 'open'


class EditingInput(BaseModel):
    project_id: str
    artifact_id: str
    content: str = Field(min_length=50)
    edit_type: Literal['developmental', 'structural', 'line', 'grammar', 'readability', 'style', 'full'] = 'full'
    style_guide: dict = {}
    target_reading_level: str = 'general_adult'


class EditingOutput(BaseModel):
    edit_type: str
    findings: list[EditFinding]
    overall_quality_score: float = Field(ge=0, le=10)
    readability_score: float = Field(ge=0, le=100)  # Flesch reading ease
    critical_count: int
    major_count: int
    is_publication_ready: bool
    summary: str
    confidence: float = Field(ge=0, le=1)
    positive_observations: list[str]


class EditingAgent(BaseAgent[EditingOutput]):
    agent_type = 'editing_agent'
    prompt_version = '1.0.0'
    
    def get_input_schema(self): return EditingInput
    def get_output_schema(self): return EditingOutput
    
    def get_system_prompt(self, context: AgentContext) -> str:
        return (
            'You are a senior developmental editor with 20 years of experience in publishing.\n'
            'Your job is to provide rigorous, actionable editorial feedback.\n\n'
            'EDITORIAL RULES:\n'
            '1. is_publication_ready must be false if ANY critical findings exist.\n'
            '2. Provide specific, quoted evidence for each finding (not vague claims).\n'
            '3. Overall quality score must reflect the actual content quality (be honest).\n'
            '4. Readability score should approximate Flesch Reading Ease (0-100).\n'
            '5. Include at least 1-3 positive_observations even in weak manuscripts.\n'
            '6. Suggested corrections must be concrete and implementable.\n'
            '7. critical findings are blockers; major are strong recommendations; minor are nice-to-have.\n'
        )
