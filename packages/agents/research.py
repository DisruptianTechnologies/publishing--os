from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from .base import BaseAgent, AgentContext


class DemandSignal(BaseModel):
    signal: str
    strength: Literal['strong', 'moderate', 'weak']
    evidence: str
    source_type: Literal['bestseller_data', 'keyword_data', 'review_analysis', 'model_inference']

class CompetitionSignal(BaseModel):
    signal: str
    level: Literal['high', 'medium', 'low']
    evidence: str

class AudienceProfile(BaseModel):
    primary_description: str
    age_range: str
    pain_points: list[str]
    goals: list[str]
    preferred_content_style: str

class PriceRange(BaseModel):
    low_usd: float
    high_usd: float
    recommended_usd: float
    rationale: str

class CompetitorExample(BaseModel):
    title: str
    estimated_rank: str
    price_usd: float
    strengths: list[str]
    weaknesses: list[str]
    review_themes: list[str]

class Risk(BaseModel):
    risk: str
    severity: Literal['high', 'medium', 'low']
    mitigation: str

class Evidence(BaseModel):
    claim: str
    source_type: Literal['market_data', 'model_inference', 'user_provided', 'demo_data']
    confidence: float
    note: str = ''


class ResearchInput(BaseModel):
    project_id: str
    idea_description: str = Field(min_length=10)
    target_market: str = ''
    project_type: str = 'nonfiction_book'
    research_depth: Literal['quick', 'standard', 'deep'] = 'standard'


class ResearchOutput(BaseModel):
    opportunity_score: float = Field(ge=0, le=10)
    demand_signals: list[DemandSignal]
    competition_signals: list[CompetitionSignal]
    audience: AudienceProfile
    price_range: PriceRange
    competitor_examples: list[CompetitorExample]
    unmet_needs: list[str]
    proposed_product: str
    differentiators: list[str]
    risks: list[Risk]
    evidence: list[Evidence]
    confidence: float = Field(ge=0, le=1)
    research_date: str
    recommended_next_experiment: str
    freshness_class: Literal['live', 'recent', 'stale', 'unknown']
    disclaimer: str = 'This analysis combines model inferences with demo data. Verify market data independently before making publishing decisions.'


class ResearchAgent(BaseAgent[ResearchOutput]):
    agent_type = 'research_agent'
    prompt_version = '1.0.0'
    
    def get_input_schema(self): return ResearchInput
    def get_output_schema(self): return ResearchOutput
    
    def get_system_prompt(self, context: AgentContext) -> str:
        return (
            'You are a senior publishing market research analyst. Your job is to evaluate a book idea\n'
            'for commercial viability on Amazon KDP and similar platforms.\n\n'
            'RULES YOU MUST FOLLOW:\n'
            '1. NEVER fabricate specific sales numbers, review counts, or ranking data.\n'
            '2. ALL market data inferences must be labeled with INFERENCE: prefix.\n'
            '3. ALL factual claims must be labeled with FACT: prefix.\n'
            '4. If you cannot determine something with confidence, say so explicitly.\n'
            '5. opportunity_score must reflect genuine analysis (0=no market, 10=exceptional market).\n'
            '6. freshness_class should be unknown when operating without live data tools.\n'
            '7. Always include the standard disclaimer about demo data.\n\n'
            'SCORING GUIDE:\n'
            '0-3: Very high competition, low demand, avoid\n'
            '4-6: Moderate opportunity, proceed with differentiation\n'
            '7-8: Strong opportunity, clear path to market\n'
            '9-10: Exceptional opportunity (rare, be conservative)\n'
        )
