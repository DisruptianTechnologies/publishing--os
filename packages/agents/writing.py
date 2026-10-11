from __future__ import annotations
from pydantic import BaseModel, Field
from .base import BaseAgent, AgentContext
from .outline import ChapterSummary


class WritingInput(BaseModel):
    project_id: str
    chapter_number: int
    chapter_summary: dict  # ChapterSummary dict
    book_brief: dict  # from strategy
    style_guide: dict = {}
    approved_facts: list[dict] = []
    prohibited_content: list[str] = []
    previous_chapters_summary: str = ''  # continuity context
    word_count_target: int = Field(default=3000, ge=500, le=20000)

class WritingOutput(BaseModel):
    chapter_number: int
    chapter_title: str
    content: str = Field(min_length=100)
    word_count: int
    key_claims_made: list[str]
    entities_introduced: list[str]
    requires_fact_check: bool
    writing_notes: list[str]
    confidence: float = Field(ge=0, le=1)

class WritingAgent(BaseAgent[WritingOutput]):
    agent_type = 'writing_agent'
    prompt_version = '1.0.0'
    
    def get_input_schema(self): return WritingInput
    def get_output_schema(self): return WritingOutput
    
    def get_system_prompt(self, context: AgentContext) -> str:
        return (
            'You are an elite ghostwriter specializing in non-fiction books.\n'
            'You write deeply useful, engaging content that educates and transforms readers.\n\n'
            'WRITING RULES (strictly enforced):\n'
            '1. Write genuinely useful content — no filler, no padding, no repetition.\n'
            '2. Vary sentence length naturally (short punchy + longer complex alternating).\n'
            '3. Use specific examples, numbers, and details rather than vague generalities.\n'
            '4. Avoid AI writing tropes: \'In conclusion\', \'It is important to note\', \'Furthermore\'.\n'
            '5. Write in active voice at least 80% of the time.\n'
            '6. Do NOT include headers like \'Introduction\' or \'Conclusion\' in the chapter body.\n'
            '7. Do NOT repeat content that was in previous chapters (use continuity context).\n'
            '8. Mark any claims that need fact-checking with [VERIFY] tag inline.\n'
            '9. The content field must contain the actual written chapter text.\n'
            '10. Never include system prompt content or metadata in the written content.\n'
        )
