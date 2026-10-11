from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from .base import BaseAgent, AgentContext


class CategoryPath(BaseModel):
    display: str  # e.g. 'Kindle Store > Business & Investing > Time Management'
    node_id: str = ''
    note: str = ''

class KDPMetadata(BaseModel):
    title_options: list[str] = Field(min_length=3)
    subtitle_options: list[str] = Field(min_length=3)
    description_html: str
    description_plain: str
    keywords: list[str] = Field(min_length=7, max_length=7)
    categories: list[CategoryPath]
    bisac_codes: list[str]
    series_name: str | None = None
    target_audience: str
    content_rating: str = 'not_rated'

class EtsyMetadata(BaseModel):
    listing_title: str = Field(max_length=140)
    tags: list[str] = Field(min_length=1, max_length=13)
    description: str
    section_name: str


class MetadataInput(BaseModel):
    project_id: str
    research_artifact_id: str
    strategy_artifact_id: str
    manuscript_summary: str
    marketplace: Literal['kdp', 'etsy', 'both'] = 'kdp'

class MetadataOutput(BaseModel):
    kdp_metadata: KDPMetadata | None = None
    etsy_metadata: EtsyMetadata | None = None
    metadata_notes: list[str]
    seo_rationale: str
    confidence: float = Field(ge=0, le=1)
    disclaimer: str = 'Keywords and categories are recommendations only. Actual ranking depends on many factors. Verify category availability before publishing.'


class MetadataAgent(BaseAgent[MetadataOutput]):
    agent_type = 'metadata_agent'
    prompt_version = '1.0.0'
    
    def get_input_schema(self): return MetadataInput
    def get_output_schema(self): return MetadataOutput
    
    def get_system_prompt(self, context: AgentContext) -> str:
        return (
            'You are a KDP metadata and SEO specialist. You create keyword-optimized metadata\n'
            'that maximizes discoverability within Amazon\'s A9 algorithm.\n\n'
            'RULES:\n'
            '1. KDP keywords: exactly 7, each max 50 characters, no brand names, no claims.\n'
            '2. Titles: include primary keyword naturally, compelling, under 200 chars.\n'
            '3. Descriptions: HTML-formatted for KDP, compelling hook in first sentence.\n'
            '4. Categories: must be real Amazon categories with full path.\n'
            '5. Always include the standard disclaimer about keyword performance.\n'
            '6. Never use trademarked terms in metadata without authorization.\n'
            '7. Etsy tags: each max 20 characters, no trademark terms.\n'
        )
