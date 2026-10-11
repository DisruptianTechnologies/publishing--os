"""
Policy Engine — blocking, deterministic policy evaluation.
Evaluated BEFORE any action that modifies external state.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Literal
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

POLICY_VERSION = 'KINDLEPRENEUR_POLICY_2024_v1'


@dataclass
class PolicyAction:
    action_type: str  # publish_content | send_email | create_listing | start_workflow | delete_resource
    tenant_id: str
    project_id: str
    resource_ids: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    requested_by: str = 'system'  # user_id or agent_type
    estimated_cost_usd: float = 0.0


@dataclass
class PolicyDecision:
    decision: Literal['allow', 'review', 'block']
    risk_score: float  # 0-1
    reasons: list[str]
    failed_rules: list[str]
    policy_version: str
    requires_approval: bool
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PolicyRule:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def evaluate(self, action: PolicyAction, context: dict) -> tuple[bool, str]:
        """Returns (passed, reason_if_failed)."""
        raise NotImplementedError


class TenantActiveRule(PolicyRule):
    def __init__(self):
        super().__init__('tenant_active', 'Tenant must be active to perform actions')
    
    def evaluate(self, action: PolicyAction, context: dict) -> tuple[bool, str]:
        tenant = context.get('tenant')
        if tenant and not tenant.get('is_active', True):
            return False, f'Tenant {action.tenant_id} is not active'
        return True, ''


class FeatureFlagRule(PolicyRule):
    def __init__(self):
        super().__init__('feature_flag', 'Required feature must be enabled for tenant')
    
    def evaluate(self, action: PolicyAction, context: dict) -> tuple[bool, str]:
        required_feature = context.get('required_feature')
        if not required_feature:
            return True, ''
        tenant_flags = context.get('feature_flags', {})
        if not tenant_flags.get(required_feature, True):  # default: features enabled
            return False, f'Feature {required_feature} not enabled for tenant'
        return True, ''


class BudgetRule(PolicyRule):
    def __init__(self):
        super().__init__('budget', 'Action must be within tenant budget')
    
    def evaluate(self, action: PolicyAction, context: dict) -> tuple[bool, str]:
        remaining_budget = context.get('remaining_budget_usd', 999.0)
        if action.estimated_cost_usd > remaining_budget:
            return False, f'Estimated cost ${action.estimated_cost_usd:.2f} exceeds remaining budget ${remaining_budget:.2f}'
        return True, ''


class ExternalEffectApprovalRule(PolicyRule):
    """Actions with external effects (publishing, sending emails) require approval."""
    APPROVAL_REQUIRED_ACTIONS = {
        'publish_content', 'send_email', 'create_listing', 'delete_resource'
    }
    
    def __init__(self):
        super().__init__('external_effect_approval', 'Actions with external effects require human approval')
    
    def evaluate(self, action: PolicyAction, context: dict) -> tuple[bool, str]:
        if action.action_type in self.APPROVAL_REQUIRED_ACTIONS:
            autonomy_level = context.get('autonomy_level', 2)
            if autonomy_level < 4:  # Below level 4 requires approval
                return False, f'Action {action.action_type} requires human approval (autonomy_level={autonomy_level})'
        return True, ''


class PolicyEngine:
    def __init__(self):
        self._rules = [
            TenantActiveRule(),
            FeatureFlagRule(),
            BudgetRule(),
            ExternalEffectApprovalRule(),
        ]
    
    def evaluate(self, action: PolicyAction, context: dict | None = None) -> PolicyDecision:
        ctx = context or {}
        failed_rules = []
        reasons = []
        risk_score = 0.0
        requires_approval = False
        
        for rule in self._rules:
            try:
                passed, reason = rule.evaluate(action, ctx)
                if not passed:
                    failed_rules.append(rule.name)
                    reasons.append(reason)
                    if rule.name == 'external_effect_approval':
                        requires_approval = True
                        risk_score = max(risk_score, 0.5)
                    else:
                        risk_score = max(risk_score, 0.8)
            except Exception as e:
                logger.error(f'Policy rule {rule.name} failed with exception: {e}')
                failed_rules.append(rule.name)
                reasons.append(f'Rule evaluation error: {e}')
                risk_score = max(risk_score, 0.9)
        
        if not failed_rules:
            decision = 'allow'
        elif requires_approval and len([r for r in failed_rules if r != 'external_effect_approval']) == 0:
            decision = 'review'  # Only needs approval, not blocked
        else:
            decision = 'block'
        
        return PolicyDecision(
            decision=decision,
            risk_score=risk_score,
            reasons=reasons,
            failed_rules=failed_rules,
            policy_version=POLICY_VERSION,
            requires_approval=requires_approval,
        )


# Singleton
_engine: PolicyEngine | None = None

def get_policy_engine() -> PolicyEngine:
    global _engine
    if _engine is None:
        _engine = PolicyEngine()
    return _engine
