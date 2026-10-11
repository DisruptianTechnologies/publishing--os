from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
from .base import BaseAgent, AgentContext


class ComplianceCheck(BaseModel):
    check_type: str  # copyright | trademark | claims | ai_disclosure | marketplace_rules | content_policy
    status: Literal['pass', 'warn', 'fail', 'manual_verification_required']
    finding: str
    severity: Literal['critical', 'major', 'minor']
    remediation: str
    policy_reference: str
    confidence: float = Field(ge=0, le=1)


class ComplianceInput(BaseModel):
    project_id: str
    artifact_ids: list[str]
    content_sample: str = Field(min_length=10)
    metadata: dict = {}
    marketplace: str = 'kdp'
    check_types: list[str] = ['copyright', 'trademark', 'claims', 'ai_disclosure', 'marketplace_rules']

class ComplianceOutput(BaseModel):
    overall_status: Literal['pass', 'warn', 'fail']
    checks: list[ComplianceCheck]
    blocks_publication: bool  # true if any critical failures
    required_disclosures: list[str]
    policy_version: str
    confidence: float = Field(ge=0, le=1)
    compliance_date: str
    auditor_notes: str

class ComplianceAgent(BaseAgent[ComplianceOutput]):
    agent_type = 'compliance_agent'
    prompt_version = '1.0.0'
    
    def get_input_schema(self): return ComplianceInput
    def get_output_schema(self): return ComplianceOutput
    
    def get_system_prompt(self, context: AgentContext) -> str:
        return (
            'You are a publishing compliance specialist. You audit content and metadata\n'
            'for policy compliance before publication.\n\n'
            'IMPORTANT LIMITATIONS:\n'
            '1. You cannot legally certify compliance — always recommend human legal review for edge cases.\n'
            '2. blocks_publication must be true if any check returns \'fail\' with severity \'critical\'.\n'
            '3. ai_disclosure check: KDP and many platforms require disclosure if AI-assisted content\n'
            '   is used. Recommend disclosure by default.\n'
            '4. claims check: flag any unverified statistical claims or promises.\n'
            '5. trademark check: flag any use of brand names that could constitute trademark infringement.\n'
            '6. Be conservative: when uncertain, recommend manual_verification_required.\n'
            '7. policy_version should reference the most recent policy you have knowledge of.\n'
        )
