from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from .base import BaseAgent, AgentContext


class SectionSummary(BaseModel):
    section_title: str
    key_points: list[str]
    estimated_words: int

class ChapterSummary(BaseModel):
    chapter_number: int
    title: str
    hook: str
    key_points: list[str]
    sections: list[SectionSummary]
    estimated_words: int = Field(ge=500)
    research_slots: list[str]  # placeholders for facts to fill in
    case_study_slots: list[str]  # placeholder names for case studies
    chapter_promise: str  # what reader gains from this chapter

class BookStructure(BaseModel):
    has_introduction: bool = True
    has_conclusion: bool = True
    has_appendix: bool = False
    has_index: bool = False
    parts: list[str] = []  # groupings if any

class Entity(BaseModel):
    name: str
    entity_type: str  # character | expert | brand | concept | location
    description: str


class OutlineInput(BaseModel):
    project_id: str
    strategy_artifact_id: str
    strategy_summary: dict
    style_preferences: dict = {}

class OutlineOutput(BaseModel):
    title_candidates: list[str] = Field(min_length=3)
    subtitle_candidates: list[str] = Field(min_length=3)
    book_structure: BookStructure
    estimated_word_count: int
    chapter_summaries: list[ChapterSummary]
    style_guide_notes: list[str]
    key_entities: list[Entity] = []
    confidence: float = Field(ge=0, le=1)
    outline_rationale: str

class OutlineAgent(BaseAgent[OutlineOutput]):
    agent_type = 'outline_agent'
    prompt_version = '1.0.0'
    
    def get_input_schema(self): return OutlineInput
    def get_output_schema(self): return OutlineOutput
    
    def get_system_prompt(self, context: AgentContext) -> str:
        return (
            'You are an expert book architect specializing in non-fiction structure.\n'
            'You create detailed chapter outlines that maximize reader retention and commercial appeal.\n\n'
            'Guidelines:\n'
            '1. Each chapter must have a clear promise to the reader.\n'
            '2. Research and case study slots must be specific placeholders (not generic).\n'
            '3. Title candidates must be commercially appealing and keyword-rich.\n'
            '4. Estimate word counts realistically for the project type.\n'
            '5. Total word count should match industry standards for the genre.\n'
        )
