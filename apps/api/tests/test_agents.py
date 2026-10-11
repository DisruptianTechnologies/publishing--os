import pytest
import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'packages'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from packages.agents.research import ResearchAgent, ResearchInput, ResearchOutput
from packages.agents.strategy import StrategyAgent, StrategyInput, StrategyOutput
from packages.agents.outline import OutlineAgent, OutlineInput, OutlineOutput
from packages.agents.compliance import ComplianceAgent, ComplianceInput, ComplianceOutput
from packages.agents.metadata import MetadataAgent, MetadataInput, MetadataOutput
from packages.agents.base import AgentContext


def test_research_agent_schemas():
    agent = ResearchAgent()
    input_schema = agent.get_input_schema()
    output_schema = agent.get_output_schema()
    
    assert input_schema == ResearchInput
    assert output_schema == ResearchOutput
    
    # Valid input
    valid_data = {
        'project_id': 'proj-123',
        'idea_description': 'A comprehensive handbook for modern indie authors publishing on KDP.',
        'target_market': 'Indie authors',
        'project_type': 'nonfiction_book',
    }
    validated = input_schema.model_validate(valid_data)
    assert validated.project_id == 'proj-123'
    
    # Context generation
    ctx = AgentContext(
        tenant_id='tenant-12345678',
        project_id='proj-12345678',
        task_id='task-12345678',
        workflow_run_id='wf-12345678',
        token_budget=100000,
        cost_budget_usd=5.0,
        model_policy='large',
        allowed_tools=['demo_search'],
    )
    prompt_msgs = agent.build_prompt_assembly(validated, ctx)
    assert len(prompt_msgs) == 2
    assert prompt_msgs[0].role == 'system'
    assert prompt_msgs[1].role == 'user'
    assert 'tenant=tenant-1' in prompt_msgs[0].content


def test_compliance_agent_schemas():
    agent = ComplianceAgent()
    input_schema = agent.get_input_schema()
    output_schema = agent.get_output_schema()
    
    assert input_schema == ComplianceInput
    assert output_schema == ComplianceOutput
    
    valid_input = {
        'project_id': 'proj-999',
        'artifact_ids': ['art-1', 'art-2'],
        'content_sample': 'Chapter 1: The Foundations of Independent Digital Publishing.',
    }
    validated = input_schema.model_validate(valid_input)
    assert validated.marketplace == 'kdp'
