"""
Integration Tests for Multi-Agent Workflows - Week 19 Implementation

Tests for orchestrator service coordinating multiple agents:
- Full Company Analysis workflow
- Financial Deep Dive workflow
- Market Intelligence workflow
- Error handling and retries
- Agent dependency management

Author: MI-Navigator Development Team
Created: 2026-01-26 (Week 19)
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from app.services.orchestrator import (
    OrchestratorService,
    AgentStatus,
    ExecutionMode,
    Phase
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def orchestrator():
    """Create orchestrator instance for testing."""
    return OrchestratorService()


@pytest.fixture
def mock_agent_results():
    """Mock results for all 6 agents."""
    return {
        "company_profile": {
            "company_name": "Test Company S.A.",
            "nip": "1234567890",
            "status": "active",
            "confidence_score": 85.0,
            "data_sources": ["KRS", "GUS"]
        },
        "financial_analysis": {
            "financial_health_score": {
                "overall_score": 72.5,
                "risk_level": "medium"
            },
            "financial_statements": []
        },
        "digital_presence": {
            "confidence_score": 78.0,
            "tech_stack": None,
            "seo_analysis": None
        },
        "competitor_mapping": {
            "total_competitors_found": 5,
            "direct_competitors_count": 3,
            "indirect_competitors_count": 2
        },
        "fact_checker": {
            "total_claims_checked": 10,
            "verified_claims_count": 8,
            "contradicted_claims_count": 1,
            "overall_confidence_score": 82.0
        },
        "insight_generator": {
            "total_insights": 5,
            "total_patterns": 3,
            "total_predictions": 2,
            "total_risks": 1,
            "total_opportunities": 2,
            "overall_confidence_score": 78.5
        }
    }


# ============================================================================
# WORKFLOW DEFINITION TESTS
# ============================================================================

def test_full_company_analysis_workflow_definition(orchestrator):
    """Test Full Company Analysis workflow structure (Week 19 Workflow 1)."""
    plan = orchestrator._create_execution_plan(
        analysis_type="full_company_analysis",
        target="Test Company S.A.",
        context={}
    )

    # Should have 4 phases
    assert len(plan) == 4

    # Phase 1: Company Foundation
    assert plan[0].name == "company_foundation"
    assert plan[0].execution_mode == ExecutionMode.SEQUENTIAL
    assert len(plan[0].agents) == 1
    assert plan[0].agents[0]["type"] == "company_profile"

    # Phase 2: Financial Analysis
    assert plan[1].name == "financial_analysis"
    assert plan[1].execution_mode == ExecutionMode.SEQUENTIAL
    assert plan[1].agents[0]["type"] == "financial_analysis"

    # Phase 3: Digital Presence
    assert plan[2].name == "digital_presence"
    assert plan[2].execution_mode == ExecutionMode.SEQUENTIAL
    assert plan[2].agents[0]["type"] == "digital_presence"

    # Phase 4: Competitor Analysis
    assert plan[3].name == "competitor_analysis"
    assert plan[3].execution_mode == ExecutionMode.SEQUENTIAL
    assert plan[3].agents[0]["type"] == "competitor_mapping"


def test_financial_deep_dive_workflow_definition(orchestrator):
    """Test Financial Deep Dive workflow structure (Week 19 Workflow 2)."""
    plan = orchestrator._create_execution_plan(
        analysis_type="financial_deep_dive",
        target="Test Company S.A.",
        context={}
    )

    # Should have 3 phases
    assert len(plan) == 3

    # Phase 1: Company Foundation
    assert plan[0].name == "company_foundation"
    assert plan[0].agents[0]["type"] == "company_profile"

    # Phase 2: Financial Analysis
    assert plan[1].name == "financial_analysis"
    assert plan[1].agents[0]["type"] == "financial_analysis"

    # Phase 3: Fact Verification
    assert plan[2].name == "fact_verification"
    assert plan[2].agents[0]["type"] == "fact_checker"


def test_market_intelligence_workflow_definition(orchestrator):
    """Test Market Intelligence workflow structure (Week 19 Workflow 3)."""
    plan = orchestrator._create_execution_plan(
        analysis_type="market_intelligence",
        target="Manufacturing Industry",
        context={}
    )

    # Should have 3 phases
    assert len(plan) == 3

    # Phase 1: Competitor Landscape
    assert plan[0].name == "competitor_landscape"
    assert plan[0].agents[0]["type"] == "competitor_mapping"

    # Phase 2: Digital Analysis
    assert plan[1].name == "digital_analysis"
    assert plan[1].agents[0]["type"] == "digital_presence"

    # Phase 3: Insight Generation
    assert plan[2].name == "insight_generation"
    assert plan[2].agents[0]["type"] == "insight_generator"


# ============================================================================
# AGENT DEPENDENCY MANAGEMENT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_sequential_dependency_management():
    """Test that sequential phases pass context correctly (Week 19)."""
    orchestrator = OrchestratorService()

    # Mock agent execution to track context flow
    executed_agents = []

    async def mock_execute_agent(agent_type, agent_config, context):
        executed_agents.append({
            "agent_type": agent_type,
            "context": dict(context)
        })
        return {f"{agent_type}_data": "test_result"}

    with patch.object(orchestrator, '_execute_agent_logic', side_effect=mock_execute_agent):
        await orchestrator.execute_analysis(
            analysis_type="financial_deep_dive",
            target="Test Company",
            context={}
        )

    # All 3 agents should execute
    assert len(executed_agents) == 3

    # Second agent should have context from first agent (nested under agent type)
    assert "company_profile" in executed_agents[1]["context"]

    # Third agent should have context from first and second agents (nested under agent types)
    assert "company_profile" in executed_agents[2]["context"]
    assert "financial_analysis" in executed_agents[2]["context"]


# ============================================================================
# ERROR HANDLING AND RETRY TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_workflow_handles_agent_failure():
    """Test workflow continues on agent failure (Week 19)."""
    orchestrator = OrchestratorService()

    call_count = {"count": 0}

    async def mock_execute_with_failure(agent_type, agent_config, context):
        call_count["count"] += 1
        if agent_type == "financial_analysis":
            raise Exception("Simulated agent failure")
        return {f"{agent_type}_result": "success"}

    with patch.object(orchestrator, '_execute_agent_logic', side_effect=mock_execute_with_failure):
        result = await orchestrator.execute_analysis(
            analysis_type="financial_deep_dive",
            target="Test Company",
            context={}
        )

    # Should have attempted all 3 agents with retries
    # company_profile: 1 call (succeeds)
    # financial_analysis: 4 calls (1 original + 3 retries, all fail)
    # fact_checker: 1 call (succeeds)
    # Total: 6 calls
    assert call_count["count"] == 6

    # Job should complete despite failure
    job_id = list(orchestrator.active_jobs.keys())[0]
    assert orchestrator.active_jobs[job_id]["status"] == AgentStatus.COMPLETED


@pytest.mark.asyncio
async def test_retry_mechanism_for_transient_failures():
    """Test retry mechanism for transient agent failures (Week 19)."""
    orchestrator = OrchestratorService()

    call_count = {"count": 0}

    async def mock_execute_with_transient_failure(agent_type, agent_config, context):
        call_count["count"] += 1
        # Fail first time, succeed on retry
        if call_count["count"] == 1:
            raise Exception("Transient failure")
        return {"result": "success"}

    with patch.object(orchestrator, '_execute_agent_logic', side_effect=mock_execute_with_transient_failure):
        result = await orchestrator.execute_analysis(
            analysis_type="company",
            target="Test Company",
            context={}
        )

    # Should have retried (2 attempts for first agent, 1 for second)
    assert call_count["count"] >= 2


# ============================================================================
# WORKFLOW EXECUTION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_full_company_analysis_execution():
    """Test complete Full Company Analysis workflow execution (Week 19)."""
    orchestrator = OrchestratorService()

    async def mock_execute(agent_type, agent_config, context):
        return {
            f"{agent_type}_completed": True,
            "confidence_score": 80.0
        }

    with patch.object(orchestrator, '_execute_agent_logic', side_effect=mock_execute):
        result = await orchestrator.execute_analysis(
            analysis_type="full_company_analysis",
            target="Test Company S.A.",
            context={}
        )

    # Should have results from all 4 agents (nested under "results" key)
    assert "results" in result
    assert "company_profile" in result["results"]
    assert result["results"]["company_profile"]["company_profile_completed"] is True
    assert "financial_analysis" in result["results"]
    assert result["results"]["financial_analysis"]["financial_analysis_completed"] is True
    assert "digital_presence" in result["results"]
    assert result["results"]["digital_presence"]["digital_presence_completed"] is True
    assert "competitor_mapping" in result["results"]
    assert result["results"]["competitor_mapping"]["competitor_mapping_completed"] is True


@pytest.mark.asyncio
async def test_market_intelligence_execution():
    """Test Market Intelligence workflow execution (Week 19)."""
    orchestrator = OrchestratorService()

    async def mock_execute(agent_type, agent_config, context):
        return {
            f"{agent_type}_data": {
                "status": "completed",
                "insights": 5 if agent_type == "insight_generator" else None
            }
        }

    with patch.object(orchestrator, '_execute_agent_logic', side_effect=mock_execute):
        result = await orchestrator.execute_analysis(
            analysis_type="market_intelligence",
            target="Manufacturing Industry",
            context={}
        )

    # Should have data from all 3 agents (nested under "results" key)
    assert "results" in result
    assert "competitor_mapping" in result["results"]
    assert "competitor_mapping_data" in result["results"]["competitor_mapping"]
    assert "digital_presence" in result["results"]
    assert "digital_presence_data" in result["results"]["digital_presence"]
    assert "insight_generator" in result["results"]
    assert "insight_generator_data" in result["results"]["insight_generator"]

    # Insight generator should have insights
    assert result["results"]["insight_generator"]["insight_generator_data"]["insights"] == 5


@pytest.mark.asyncio
async def test_comprehensive_workflow_with_all_agents():
    """Test comprehensive workflow using all 6 agents (Week 19)."""
    orchestrator = OrchestratorService()

    executed_agents = set()

    async def mock_execute(agent_type, agent_config, context):
        executed_agents.add(agent_type)
        return {f"{agent_type}_result": "success"}

    with patch.object(orchestrator, '_execute_agent_logic', side_effect=mock_execute):
        result = await orchestrator.execute_analysis(
            analysis_type="comprehensive",
            target="Test Company",
            context={}
        )

    # Should execute all 6 agent types
    assert "company_profile" in executed_agents
    assert "financial_analysis" in executed_agents
    assert "digital_presence" in executed_agents
    assert "competitor_mapping" in executed_agents
    assert "fact_checker" in executed_agents
    assert "insight_generator" in executed_agents


# ============================================================================
# PROGRESS TRACKING TESTS
# ============================================================================

def test_job_progress_tracking():
    """Test job progress tracking through workflow (Week 19)."""
    orchestrator = OrchestratorService()

    plan = orchestrator._create_execution_plan(
        analysis_type="full_company_analysis",
        target="Test Company",
        context={}
    )

    assert len(plan) == 4

    # Each phase should have proper structure
    for phase in plan:
        assert hasattr(phase, 'phase_id')
        assert hasattr(phase, 'name')
        assert hasattr(phase, 'agents')
        assert hasattr(phase, 'execution_mode')
        assert hasattr(phase, 'status')
        assert phase.status == AgentStatus.PENDING


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
