from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from .base import BaseAgent, AgentContext
from .research import PriceRange


class MarketplacePosition(BaseModel):
    marketplace: str
    category_path: str
    positioning_strategy: str
    expected_competition: Literal['high', 'medium', 'low']


class StrategyInput(BaseModel):
    project_id: str
    research_artifact_id: str
    research_summary: dict  # Serialized ResearchOutput
    user_preferences: dict = {}


class StrategyOutput(BaseModel):
    product_type: str
    target_customer: str
    reading_level: str
    unique_selling_proposition: str
    product_promise: str
    chapter_count_estimate: int = Field(ge=1, le=100)
    series_potential: bool
    series_concept: str | None = None
    recommended_price_range: PriceRange
    marketplace_positioning: list[MarketplacePosition]
    launch_strategy_overview: str
    key_messages: list[str]
    confidence: float = Field(ge=0, le=1)
    strategy_rationale: str


class StrategyAgent(BaseAgent[StrategyOutput]):
    agent_type = 'strategy_agent'
    prompt_version = '1.0.0'
    
    def get_input_schema(self): return StrategyInput
    def get_output_schema(self): return StrategyOutput
    
    def get_system_prompt(self, context: AgentContext) -> str:
        return (
            'You are a book publishing strategist specializing in Amazon KDP and digital product strategy.\n'
            'You receive market research and produce a detailed product strategy.\n\n'
            'Your strategy must:\n'
            '1. Define a clear, differentiating unique selling proposition.\n'
            '2. Specify realistic chapter counts for the genre/type.\n'
            '3. Provide actionable launch strategy steps.\n'
            '4. Be grounded in the research evidence provided.\n'
            '5. Never recommend illegal, deceptive, or misleading strategies.\n'
            '6. Note that series potential should only be marked true if there is genuine evidence.\n'
        )
