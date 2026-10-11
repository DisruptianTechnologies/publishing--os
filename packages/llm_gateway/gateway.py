"""
LLM Gateway — provider-independent interface for LLM calls.
Supports: Gemini, OpenAI, Anthropic.
Features: token budget, cost estimation, structured output, retry, fallback.
"""
from __future__ import annotations
import os
import time
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from enum import Enum

logger = logging.getLogger(__name__)

# ==========================================
# Cost table (per 1M tokens, USD)
# Approximate — verify before billing
# ==========================================
COST_TABLE = {
    'gemini-1.5-pro': {'input': 1.25, 'output': 5.00},
    'gemini-1.5-flash': {'input': 0.075, 'output': 0.30},
    'gemini-2.0-flash': {'input': 0.10, 'output': 0.40},
    'gpt-4o': {'input': 2.50, 'output': 10.00},
    'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
    'claude-3-5-sonnet-20241022': {'input': 3.00, 'output': 15.00},
    'claude-3-haiku-20240307': {'input': 0.25, 'output': 1.25},
}

# ==========================================
# Model routing by task size
# ==========================================
MODEL_ROUTING = {
    'small': {
        'gemini': 'gemini-2.0-flash',
        'openai': 'gpt-4o-mini',
        'anthropic': 'claude-3-haiku-20240307',
    },
    'medium': {
        'gemini': 'gemini-1.5-flash',
        'openai': 'gpt-4o',
        'anthropic': 'claude-3-5-sonnet-20241022',
    },
    'large': {
        'gemini': 'gemini-1.5-pro',
        'openai': 'gpt-4o',
        'anthropic': 'claude-3-5-sonnet-20241022',
    },
    'vision': {
        'gemini': 'gemini-1.5-pro',
        'openai': 'gpt-4o',
        'anthropic': 'claude-3-5-sonnet-20241022',
    },
}


class GatewayErrorCode(str, Enum):
    RATE_LIMITED = 'rate_limited'
    QUOTA_EXCEEDED = 'quota_exceeded'
    INVALID_RESPONSE = 'invalid_response'
    BUDGET_EXCEEDED = 'budget_exceeded'
    PROVIDER_ERROR = 'provider_error'
    SCHEMA_VALIDATION_ERROR = 'schema_validation_error'


class GatewayError(Exception):
    def __init__(self, code: GatewayErrorCode, message: str, retryable: bool = False, retry_after: int | None = None):
        self.code = code
        self.message = message
        self.retryable = retryable
        self.retry_after = retry_after
        super().__init__(message)


@dataclass
class LLMMessage:
    role: str  # 'system' | 'user' | 'assistant'
    content: str


@dataclass
class LLMResult:
    content: str
    structured: dict | None
    input_tokens: int
    output_tokens: int
    cost_usd: float
    provider: str
    model: str
    latency_ms: int


class BaseProvider(ABC):
    @abstractmethod
    def complete(self, model: str, messages: list[LLMMessage], schema: dict | None, max_tokens: int) -> LLMResult:
        ...

    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        if model not in COST_TABLE:
            return 0.0
        costs = COST_TABLE[model]
        return (input_tokens / 1_000_000 * costs['input']) + (output_tokens / 1_000_000 * costs['output'])

    def _sanitize_content(self, content: str) -> str:
        # Remove common prompt injection patterns
        injection_patterns = [
            'ignore previous instructions',
            'ignore all previous',
            'disregard previous',
            'forget all instructions',
            'new instruction:',
            'system: you are now',
        ]
        sanitized = content
        for pattern in injection_patterns:
            sanitized = sanitized.replace(pattern, '[FILTERED]')
            sanitized = sanitized.replace(pattern.title(), '[FILTERED]')
            sanitized = sanitized.replace(pattern.upper(), '[FILTERED]')
        return sanitized

    def _validate_structured(self, content: str, schema: dict) -> dict | None:
        """
        Try to extract JSON from response. Returns parsed dict or None.
        """
        try:
            # Try direct parse
            return json.loads(content)
        except json.JSONDecodeError:
            # Try extracting JSON block from markdown
            import re
            match = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            # Try finding first { ... } block
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
        return None


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self._genai = genai
        except ImportError:
            self._genai = None
            logger.warning('google-generativeai not installed, Gemini provider unavailable')

    def complete(self, model: str, messages: list[LLMMessage], schema: dict | None = None, max_tokens: int = 8192) -> LLMResult:
        if not self._genai:
            raise GatewayError(GatewayErrorCode.PROVIDER_ERROR, 'google-generativeai not installed', retryable=False)
        
        start = time.time()
        
        # Sanitize user content
        sanitized_messages = []
        for msg in messages:
            content = self._sanitize_content(msg.content) if msg.role == 'user' else msg.content
            sanitized_messages.append(LLMMessage(role=msg.role, content=content))
        
        # Build Gemini-compatible request
        system_parts = [m.content for m in sanitized_messages if m.role == 'system']
        conversation = [m for m in sanitized_messages if m.role != 'system']
        
        generation_config = self._genai.types.GenerationConfig(max_output_tokens=max_tokens, temperature=0.7)
        if schema:
            generation_config.response_mime_type = 'application/json'
        
        model_instance = self._genai.GenerativeModel(
            model_name=model,
            system_instruction='\n\n'.join(system_parts) if system_parts else None,
            generation_config=generation_config,
        )
        
        history = []
        for msg in conversation[:-1]:
            history.append({'role': 'model' if msg.role == 'assistant' else 'user', 'parts': [msg.content]})
        
        last_message = conversation[-1].content if conversation else ''
        
        try:
            chat = model_instance.start_chat(history=history)
            response = chat.send_message(last_message)
        except Exception as e:
            err_str = str(e).lower()
            if 'quota' in err_str or '429' in err_str:
                raise GatewayError(GatewayErrorCode.RATE_LIMITED, str(e), retryable=True, retry_after=60)
            raise GatewayError(GatewayErrorCode.PROVIDER_ERROR, str(e), retryable=True)
        
        content = response.text
        latency_ms = int((time.time() - start) * 1000)
        
        # Token counts
        try:
            input_tokens = response.usage_metadata.prompt_token_count or 0
            output_tokens = response.usage_metadata.candidates_token_count or 0
        except Exception:
            input_tokens = len(' '.join(m.content for m in messages).split()) * 2
            output_tokens = len(content.split()) * 2
        
        structured = self._validate_structured(content, schema) if schema else None
        cost = self._estimate_cost(model, input_tokens, output_tokens)
        
        return LLMResult(
            content=content, structured=structured,
            input_tokens=input_tokens, output_tokens=output_tokens,
            cost_usd=cost, provider='gemini', model=model, latency_ms=latency_ms
        )


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=api_key)
        except ImportError:
            self._client = None
            logger.warning('openai not installed, OpenAI provider unavailable')

    def complete(self, model: str, messages: list[LLMMessage], schema: dict | None = None, max_tokens: int = 8192) -> LLMResult:
        if not self._client:
            raise GatewayError(GatewayErrorCode.PROVIDER_ERROR, 'openai not installed', retryable=False)
        
        start = time.time()
        
        formatted = []
        for msg in messages:
            content = self._sanitize_content(msg.content) if msg.role == 'user' else msg.content
            formatted.append({'role': msg.role, 'content': content})
        
        kwargs: dict[str, Any] = {
            'model': model,
            'messages': formatted,
            'max_tokens': max_tokens,
        }
        if schema:
            kwargs['response_format'] = {'type': 'json_object'}
        
        try:
            resp = self._client.chat.completions.create(**kwargs)
        except Exception as e:
            err_str = str(e).lower()
            if 'rate' in err_str or '429' in err_str:
                raise GatewayError(GatewayErrorCode.RATE_LIMITED, str(e), retryable=True, retry_after=60)
            raise GatewayError(GatewayErrorCode.PROVIDER_ERROR, str(e), retryable=True)
        
        content = resp.choices[0].message.content or ''
        latency_ms = int((time.time() - start) * 1000)
        input_tokens = resp.usage.prompt_tokens if resp.usage else 0
        output_tokens = resp.usage.completion_tokens if resp.usage else 0
        structured = self._validate_structured(content, schema) if schema else None
        cost = self._estimate_cost(model, input_tokens, output_tokens)
        
        return LLMResult(
            content=content, structured=structured,
            input_tokens=input_tokens, output_tokens=output_tokens,
            cost_usd=cost, provider='openai', model=model, latency_ms=latency_ms
        )


class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            import anthropic
            self._client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            self._client = None
            logger.warning('anthropic not installed, Anthropic provider unavailable')

    def complete(self, model: str, messages: list[LLMMessage], schema: dict | None = None, max_tokens: int = 8192) -> LLMResult:
        if not self._client:
            raise GatewayError(GatewayErrorCode.PROVIDER_ERROR, 'anthropic not installed', retryable=False)
        
        start = time.time()
        
        system_msgs = [m.content for m in messages if m.role == 'system']
        user_msgs = [{'role': m.role, 'content': self._sanitize_content(m.content) if m.role == 'user' else m.content}
                     for m in messages if m.role != 'system']
        
        kwargs: dict[str, Any] = {
            'model': model,
            'max_tokens': max_tokens,
            'messages': user_msgs,
        }
        if system_msgs:
            kwargs['system'] = '\n\n'.join(system_msgs)
        if schema:
            # Anthropic: ask for JSON in system prompt
            existing_sys = kwargs.get('system', '')
            kwargs['system'] = existing_sys + '\n\nRespond ONLY with valid JSON matching this schema: ' + json.dumps(schema)
        
        try:
            resp = self._client.messages.create(**kwargs)
        except Exception as e:
            err_str = str(e).lower()
            if 'rate' in err_str or '429' in err_str:
                raise GatewayError(GatewayErrorCode.RATE_LIMITED, str(e), retryable=True, retry_after=60)
            raise GatewayError(GatewayErrorCode.PROVIDER_ERROR, str(e), retryable=True)
        
        content = resp.content[0].text if resp.content else ''
        latency_ms = int((time.time() - start) * 1000)
        input_tokens = resp.usage.input_tokens if resp.usage else 0
        output_tokens = resp.usage.output_tokens if resp.usage else 0
        structured = self._validate_structured(content, schema) if schema else None
        cost = self._estimate_cost(model, input_tokens, output_tokens)
        
        return LLMResult(
            content=content, structured=structured,
            input_tokens=input_tokens, output_tokens=output_tokens,
            cost_usd=cost, provider='anthropic', model=model, latency_ms=latency_ms
        )


class LLMGateway:
    """
    Provider-independent LLM gateway.
    Handles routing, budget enforcement, retry, fallback.
    """
    
    def __init__(self, primary_provider: str = None):
        self.primary_provider = primary_provider or os.getenv('LLM_PROVIDER', 'gemini')
        self._providers: dict[str, BaseProvider] = {}
        self._init_providers()
    
    def _init_providers(self):
        gemini_key = os.getenv('GEMINI_API_KEY', '')
        openai_key = os.getenv('OPENAI_API_KEY', '')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
        if gemini_key:
            self._providers['gemini'] = GeminiProvider(gemini_key)
        if openai_key:
            self._providers['openai'] = OpenAIProvider(openai_key)
        if anthropic_key:
            self._providers['anthropic'] = AnthropicProvider(anthropic_key)
    
    def route(self, model_policy: str) -> tuple[str, str]:
        """
        Returns (provider, model) for the given policy.
        Falls back to other providers if primary not available.
        """
        policy = model_policy if model_policy in MODEL_ROUTING else 'large'
        # Try primary provider first
        for provider in [self.primary_provider, 'gemini', 'openai', 'anthropic']:
            if provider in self._providers and provider in MODEL_ROUTING.get(policy, {}):
                return provider, MODEL_ROUTING[policy][provider]
        raise GatewayError(GatewayErrorCode.PROVIDER_ERROR, 'No LLM provider configured', retryable=False)
    
    def estimate_cost(self, provider: str, model: str, tokens: int) -> float:
        if model in COST_TABLE:
            avg_cost = (COST_TABLE[model]['input'] + COST_TABLE[model]['output']) / 2
            return tokens / 1_000_000 * avg_cost
        return 0.0
    
    def complete(
        self,
        messages: list[LLMMessage],
        model_policy: str = 'large',
        schema: dict | None = None,
        budget_tokens: int = 100_000,
        budget_usd: float = 10.0,
        max_retries: int = 3,
        provider: str | None = None,
        model: str | None = None,
    ) -> LLMResult:
        """
        Complete a chat request with budget enforcement and retry logic.
        """
        # Check budget upfront (rough estimate)
        selected_provider = provider or None
        selected_model = model or None
        
        if not selected_provider or not selected_model:
            selected_provider, selected_model = self.route(model_policy)
        
        estimated_cost = self.estimate_cost(selected_provider, selected_model, budget_tokens)
        if estimated_cost > budget_usd:
            raise GatewayError(
                GatewayErrorCode.BUDGET_EXCEEDED,
                f'Estimated cost ${estimated_cost:.4f} exceeds budget ${budget_usd:.4f}',
                retryable=False
            )
        
        prov = self._providers.get(selected_provider)
        if not prov:
            raise GatewayError(GatewayErrorCode.PROVIDER_ERROR, f'Provider {selected_provider} not available', retryable=False)
        
        last_error: GatewayError | None = None
        for attempt in range(max_retries):
            try:
                result = prov.complete(selected_model, messages, schema, budget_tokens)
                
                # Validate budget not exceeded
                if result.cost_usd > budget_usd:
                    logger.warning(f'Actual cost ${result.cost_usd:.4f} exceeded budget ${budget_usd:.4f}')
                
                return result
            except GatewayError as e:
                last_error = e
                if not e.retryable:
                    raise
                if attempt < max_retries - 1:
                    sleep_secs = (e.retry_after or (2 ** attempt))
                    logger.warning(f'Retrying after {sleep_secs}s (attempt {attempt+1}/{max_retries}): {e.message}')
                    time.sleep(sleep_secs)
        
        raise last_error or GatewayError(GatewayErrorCode.PROVIDER_ERROR, 'All retries exhausted', retryable=False)


# Singleton gateway instance
_gateway: LLMGateway | None = None

def get_gateway() -> LLMGateway:
    global _gateway
    if _gateway is None:
        _gateway = LLMGateway()
    return _gateway
