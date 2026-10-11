import pytest
import os
import sys

# Ensure packages is on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'packages'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packages.policy_engine.engine import (
    PolicyEngine,
    PolicyAction,
    TenantActiveRule,
    FeatureFlagRule,
    BudgetRule,
    ExternalEffectApprovalRule,
)


def test_tenant_active_rule():
    rule = TenantActiveRule()
    action = PolicyAction(
        action_type='publish_content',
        tenant_id='tenant-1',
        project_id='proj-1',
    )
    
    # Active tenant passes
    passed, reason = rule.evaluate(action, {'tenant': {'is_active': True}})
    assert passed is True
    assert reason == ''
    
    # Inactive tenant fails
    passed, reason = rule.evaluate(action, {'tenant': {'is_active': False}})
    assert passed is False
    assert 'not active' in reason


def test_budget_rule():
    rule = BudgetRule()
    action = PolicyAction(
        action_type='start_workflow',
        tenant_id='tenant-1',
        project_id='proj-1',
        estimated_cost_usd=10.0,
    )
    
    # Within budget
    passed, _ = rule.evaluate(action, {'remaining_budget_usd': 15.0})
    assert passed is True
    
    # Exceeds budget
    passed, reason = rule.evaluate(action, {'remaining_budget_usd': 5.0})
    assert passed is False
    assert 'exceeds remaining budget' in reason


def test_external_effect_approval_rule():
    rule = ExternalEffectApprovalRule()
    action = PolicyAction(
        action_type='publish_content',
        tenant_id='tenant-1',
        project_id='proj-1',
    )
    
    # Autonomy level 2 (< 4) requires approval
    passed, reason = rule.evaluate(action, {'autonomy_level': 2})
    assert passed is False
    assert 'requires human approval' in reason
    
    # Autonomy level 4 allows directly
    passed, reason = rule.evaluate(action, {'autonomy_level': 4})
    assert passed is True


def test_policy_engine_overall_decision():
    engine = PolicyEngine()
    
    # Action needing review
    action_review = PolicyAction(
        action_type='publish_content',
        tenant_id='tenant-1',
        project_id='proj-1',
        estimated_cost_usd=1.0,
    )
    decision = engine.evaluate(action_review, {'autonomy_level': 2, 'remaining_budget_usd': 50.0})
    assert decision.decision == 'review'
    assert decision.requires_approval is True
    
    # Action completely blocked (tenant inactive + over budget)
    action_blocked = PolicyAction(
        action_type='publish_content',
        tenant_id='tenant-1',
        project_id='proj-1',
        estimated_cost_usd=100.0,
    )
    decision_blocked = engine.evaluate(
        action_blocked,
        {'tenant': {'is_active': False}, 'remaining_budget_usd': 5.0}
    )
    assert decision_blocked.decision == 'block'
    assert len(decision_blocked.failed_rules) >= 2
