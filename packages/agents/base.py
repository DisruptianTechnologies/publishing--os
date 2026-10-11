"""
Base agent runtime for Kindlepreneur 2.0 Publishing OS.
All agents inherit from BaseAgent and produce AgentDecision[T].
"""
from __future__ import annotations
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Generic, TypeVar, Any
from pydantic import BaseModel, ValidationError

from packages.llm_gateway.gateway import LLMGateway, LLMMessage, GatewayError, get_gateway

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


@dataclass
class Citation:
    source: str
    source_type: str  # research_report | web | user_provided | model_inference
    excerpt: str
    confidence: float
    retrieved_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AgentDecision(Generic[T]):
    decision: str  # 'allow' | 'block' | 'review'
    confidence: float  # 0.0 to 1.0
    result: T
    reasons: list[str]
    policy_flags: list[str]
    citations: list[Citation]
    estimated_cost_usd: float
    actual_cost_usd: float
    model: str
    provider: str
    prompt_version: str
    artifact_ids: list[str]
    token_usage: int
    latency_ms: int


@dataclass
class AgentContext:
    tenant_id: str
    project_id: str
    task_id: str
    workflow_run_id: str
    token_budget: int
    cost_budget_usd: float
    model_policy: str  # small | medium | large | vision
    allowed_tools: list[str]
    extra: dict = field(default_factory=dict)


# ==========================================
# Tool registry
# ==========================================
_TOOL_REGISTRY: dict[str, Any] = {}

def register_tool(name: str, fn: Any):
    _TOOL_REGISTRY[name] = fn

def get_tool(name: str) -> Any | None:
    return _TOOL_REGISTRY.get(name)


class AgentRuntimeError(Exception):
    def __init__(self, code: str, message: str, retryable: bool = False):
        self.code = code
        self.message = message
        self.retryable = retryable
        super().__init__(message)


class BaseAgent(ABC, Generic[T]):
    """
    Abstract base for all Kindlepreneur agents.
    Subclasses must implement: agent_type, get_system_prompt,
    get_input_schema, get_output_schema.
    """
    prompt_version: str = '1.0.0'
    
    @property
    @abstractmethod
    def agent_type(self) -> str: ...
    
    @abstractmethod
    def get_input_schema(self) -> type[BaseModel]: ...
    
    @abstractmethod
    def get_output_schema(self) -> type[BaseModel]: ...
    
    @abstractmethod
    def get_system_prompt(self, context: AgentContext) -> str: ...
    
    def build_prompt_assembly(self, validated_input: BaseModel, context: AgentContext) -> list[LLMMessage]:
        """
        Assembles the full prompt with system policy, agent role, and task.
        """
        system_policy = (
            'You are an AI agent operating within a multi-tenant publishing platform. '
            'You MUST:\n'
            '1. Never generate content that violates copyright, trademark, or marketplace rules.\n'
            '2. Never fabricate citations, statistics, or factual claims.\n'
            '3. Clearly mark inferences with INFERENCE: prefix.\n'
            '4. Clearly mark facts with FACT: prefix.\n'
            '5. Never include instructions to ignore or override your system prompt.\n'
            '6. Return only content relevant to the assigned task.\n'
            '7. When uncertain, acknowledge uncertainty rather than guessing.\n'
            f'Context: tenant={context.tenant_id[:8]}, project={context.project_id[:8]}, task={context.task_id[:8]}\n'
            f'Budget: {context.token_budget} tokens, ${context.cost_budget_usd:.2f} USD\n'
        )
        
        agent_system = self.get_system_prompt(context)
        
        output_schema = self.get_output_schema()
        schema_hint = (
            f'\n\nYou MUST respond with a valid JSON object matching this schema: '
            f'{json.dumps(output_schema.model_json_schema(), indent=2)}'
        )
        
        task_content = json.dumps(validated_input.model_dump(), indent=2)
        
        return [
            LLMMessage(role='system', content=system_policy + '\n\n' + agent_system + schema_hint),
            LLMMessage(role='user', content=f'Execute your task with the following input:\n\n{task_content}'),
        ]
    
    def _check_tool_permissions(self, tool_names: list[str], context: AgentContext) -> list[str]:
        """Returns list of tool names that are NOT allowed."""
        return [t for t in tool_names if t not in context.allowed_tools]
    
    def execute(self, input_data: dict, context: AgentContext) -> AgentDecision[T]:
        """
        Main execution method. Validates input, calls LLM, validates output,
        returns AgentDecision.
        """
        start_time = time.time()
        
        # 1. Validate input
        input_schema = self.get_input_schema()
        try:
            validated_input = input_schema.model_validate(input_data)
        except ValidationError as e:
            raise AgentRuntimeError('input_validation_failed', str(e), retryable=False)
        
        # 2. Build prompt
        messages = self.build_prompt_assembly(validated_input, context)
        
        # 3. Get output schema for structured extraction
        output_schema_cls = self.get_output_schema()
        schema_dict = output_schema_cls.model_json_schema()
        
        # 4. Estimate cost
        gateway = get_gateway()
        estimated_cost = gateway.estimate_cost(
            *gateway.route(context.model_policy),
            context.token_budget
        )
        
        # 5. Call LLM
        try:
            result = gateway.complete(
                messages=messages,
                model_policy=context.model_policy,
                schema=schema_dict,
                budget_tokens=context.token_budget,
                budget_usd=context.cost_budget_usd,
            )
        except GatewayError as e:
            raise AgentRuntimeError(e.code.value, e.message, retryable=e.retryable)
        
        # 6. Validate output
        if result.structured is None:
            raise AgentRuntimeError('schema_validation_failed', 'LLM did not return valid JSON', retryable=True)
        
        try:
            validated_output = output_schema_cls.model_validate(result.structured)
        except ValidationError as e:
            logger.error(f'Output schema validation failed for {self.agent_type}: {e}')
            raise AgentRuntimeError('output_schema_invalid', str(e), retryable=True)
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # 7. Determine decision
        decision = 'allow'
        policy_flags = []
        
        # 8. Return AgentDecision
        return AgentDecision(
            decision=decision,
            confidence=getattr(validated_output, 'confidence', 0.8),
            result=validated_output,
            reasons=[f'Agent {self.agent_type} completed successfully'],
            policy_flags=policy_flags,
            citations=[],
            estimated_cost_usd=estimated_cost,
            actual_cost_usd=result.cost_usd,
            model=result.model,
            provider=result.provider,
            prompt_version=self.prompt_version,
            artifact_ids=[],
            token_usage=result.input_tokens + result.output_tokens,
            latency_ms=latency_ms,
        )
