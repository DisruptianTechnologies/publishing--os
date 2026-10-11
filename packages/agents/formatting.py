from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from .base import BaseAgent, AgentContext


class PreflightResult(BaseModel):
    check: str
    status: Literal['pass', 'warn', 'fail']
    location: str = ''
    message: str
    remediation: str

class FormatPackage(BaseModel):
    format: str  # epub | pdf | docx | paperback
    status: Literal['ready', 'needs_review']
    artifact_id: str = ''  # will be populated after actual file generation
    preflight_results: list[PreflightResult]
    format_notes: list[str]

class FormattingInput(BaseModel):
    project_id: str
    artifact_id: str
    output_formats: list[str] = ['epub', 'pdf', 'docx']
    trim_size: str = '6x9'
    font_family: str = 'Garamond'
    margin_top: float = 1.0
    margin_bottom: float = 1.0
    margin_inside: float = 1.25
    margin_outside: float = 0.75
    include_toc: bool = True
    include_page_numbers: bool = True

class FormattingOutput(BaseModel):
    format_packages: list[FormatPackage]
    overall_preflight_status: Literal['pass', 'warn', 'fail']
    is_publish_ready: bool
    formatting_notes: list[str]
    confidence: float = Field(ge=0, le=1)
    kdp_interior_requirements: dict = {}

class FormattingAgent(BaseAgent[FormattingOutput]):
    agent_type = 'formatting_agent'
    prompt_version = '1.0.0'
    
    def get_input_schema(self): return FormattingInput
    def get_output_schema(self): return FormattingOutput
    
    def get_system_prompt(self, context: AgentContext) -> str:
        return (
            'You are a professional book formatter specializing in KDP print and digital formats.\n'
            'You evaluate content for formatting requirements and flag issues.\n\n'
            'FORMATTING STANDARDS:\n'
            '1. KDP Print: 250-800 DPI images, bleed marks if images to edge, spine calculation required.\n'
            '2. EPUB: valid EPUB 3.0, no fixed layouts unless children\'s book, proper ToC.\n'
            '3. PDF for KDP: embed all fonts, proper page size for trim, no security restrictions.\n'
            '4. is_publish_ready must be false if any format has critical preflight failures.\n'
            '5. Identify realistic formatting issues based on content_type and project_type.\n'
        )
