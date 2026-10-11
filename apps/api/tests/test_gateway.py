import pytest
import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'packages'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packages.llm_gateway.gateway import LLMGateway, COST_TABLE, MODEL_ROUTING


def test_cost_table_values():
    assert 'gemini-1.5-pro' in COST_TABLE
    assert 'gemini-2.0-flash' in COST_TABLE
    assert 'gpt-4o' in COST_TABLE
    assert 'claude-3-5-sonnet-20241022' in COST_TABLE
    
    # Positive cost per million tokens
    for model, rates in COST_TABLE.items():
        assert rates['input'] > 0
        assert rates['output'] > 0


def test_model_routing_policies():
    for policy in ['small', 'medium', 'large', 'vision']:
        assert policy in MODEL_ROUTING
        assert 'gemini' in MODEL_ROUTING[policy]
        assert 'openai' in MODEL_ROUTING[policy]
        assert 'anthropic' in MODEL_ROUTING[policy]


def test_gateway_estimate_cost():
    gateway = LLMGateway()
    cost = gateway.estimate_cost('gemini', 'gemini-1.5-pro', 100_000)
    assert cost > 0
    assert cost < 1.0  # 100k tokens of 1.5-pro is ~$0.31
