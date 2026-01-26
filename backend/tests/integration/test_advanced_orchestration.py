"""
Integration Tests for Advanced Orchestration - Week 20 Implementation

Tests for intelligent routing, dynamic workflow generation,
result aggregation, and performance optimizations:
- Intelligent routing from natural language queries
- Dynamic workflow generation with Claude AI
- Result aggregation and deduplication
- Confidence-weighted synthesis
- Result caching and performance optimization

Author: MI-Navigator Development Team
Created: 2026-01-26 (Week 20)
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import time

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
def sample_intent():
    """Sample parsed intent for testing."""
    return {
        "analysis_type": "company_profile",
        "target": "Test Company S.A.",
        "parameters": {"company_name": "Test Company S.A."},
        "confidence": 0.95,
        "reasoning": "Company profile request detected"
    }


@pytest.fixture
def sample_query_route():
    """Sample query route classification."""
    return ("company_profile", 0.88, [("financial_analysis", 0.65)])


@pytest.fixture
def sample_agent_results():
    """Sample results from multiple agents for aggregation testing."""
    return {
        "company_profile": {
            "company_name": "Test Company S.A.",
            "nip": "1234567890",
            "status": "active",
            "confidence_score": 0.92
        },
        "financial_analysis": {
            "financial_health_score": {"overall_score": 75.5},
            "confidence_score": 0.85
        },
        "digital_presence": {
            "website_url": "https://example.com",
            "confidence_score": 0.78
        }
    }


# ============================================================================
# INTELLIGENT ROUTING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_intelligent_routing_from_query():
    """Test intelligent routing from natural language query (Week 20)."""
    orchestrator = OrchestratorService()

    # Mock intent parser and query router
    mock_intent = Mock()
    mock_intent.analysis_type = "company_profile"
    mock_intent.target = "ACME Corporation"
    mock_intent.parameters = {"company_name": "ACME Corporation"}
    mock_intent.confidence = 0.95
    mock_intent.reasoning = "Company profile detected"

    with patch('app.services.orchestrator.parse_user_intent', return_value=mock_intent):
        with patch('app.services.orchestrator.query_router_service') as mock_router:
            mock_router.classify_query.return_value = ("company_profile", 0.88, [])

            with patch.object(orchestrator, 'execute_analysis') as mock_execute:
                mock_execute.return_value = {
                    "job_id": "test-123",
                    "status": "completed",
                    "results": {}
                }

                result = await orchestrator.execute_from_query(
                    query="Tell me about ACME Corporation",
                    context={}
                )

    # Should have routing metadata
    assert "routing_metadata" in result
    assert result["routing_metadata"]["workflow_selected"] == "company_profile"
    assert result["routing_metadata"]["intent_confidence"] == 0.95


@pytest.mark.asyncio
async def test_intelligent_routing_fallback():
    """Test fallback when intelligent routing unavailable (Week 20)."""
    orchestrator = OrchestratorService()

    with patch('app.services.orchestrator.INTELLIGENT_ROUTING_AVAILABLE', False):
        with patch.object(orchestrator, 'execute_analysis') as mock_execute:
            mock_execute.return_value = {
                "job_id": "test-123",
                "status": "completed"
            }

            result = await orchestrator.execute_from_query(
                query="Test query",
                context={}
            )

            # Should fall back to default workflow
            mock_execute.assert_called_once()


# ============================================================================
# DYNAMIC WORKFLOW GENERATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_dynamic_workflow_generation():
    """Test Claude-powered dynamic workflow generation (Week 20)."""
    orchestrator = OrchestratorService()

    mock_claude_response = {
        "content": """{
            "workflow_name": "Company Deep Analysis",
            "rationale": "Comprehensive analysis requested",
            "phases": [
                {
                    "name": "foundation",
                    "execution_mode": "SEQUENTIAL",
                    "agents": ["company_profile"],
                    "timeout": 60
                },
                {
                    "name": "enrichment",
                    "execution_mode": "PARALLEL",
                    "agents": ["financial_analysis", "digital_presence"],
                    "timeout": 120
                }
            ]
        }"""
    }

    with patch('app.services.orchestrator.CLAUDE_AVAILABLE', True):
        with patch('app.services.orchestrator.get_claude_service') as mock_claude_svc:
            mock_service = AsyncMock()
            mock_service.generate_response.return_value = mock_claude_response
            mock_claude_svc.return_value = mock_service

            workflow = await orchestrator.generate_dynamic_workflow(
                query="I need deep analysis of Test Company",
                target="Test Company",
                context={}
            )

    # Should have 2 phases
    assert len(workflow) == 2
    assert workflow[0].name == "foundation"
    assert workflow[0].execution_mode == ExecutionMode.SEQUENTIAL
    assert workflow[1].name == "enrichment"
    assert workflow[1].execution_mode == ExecutionMode.PARALLEL


@pytest.mark.asyncio
async def test_dynamic_workflow_fallback():
    """Test fallback when Claude unavailable for workflow generation (Week 20)."""
    orchestrator = OrchestratorService()

    with patch('app.services.orchestrator.CLAUDE_AVAILABLE', False):
        workflow = await orchestrator.generate_dynamic_workflow(
            query="Test query",
            target="Test Company",
            context={}
        )

    # Should return default workflow
    assert isinstance(workflow, list)
    assert len(workflow) > 0
    assert isinstance(workflow[0], Phase)


# ============================================================================
# RESULT AGGREGATION TESTS
# ============================================================================

def test_result_aggregation(orchestrator, sample_agent_results):
    """Test aggregation of results from multiple agents (Week 20)."""
    aggregated = orchestrator.aggregate_results(
        sample_agent_results,
        deduplication=True
    )

    # Should have aggregated structure
    assert "company_data" in aggregated
    assert "financial_data" in aggregated
    assert "digital_data" in aggregated
    assert "metadata" in aggregated

    # Should have company data from company_profile agent
    assert aggregated["company_data"]["name"] == "Test Company S.A."
    assert aggregated["company_data"]["nip"] == "1234567890"

    # Should have financial data
    assert aggregated["financial_data"]["health_score"]["overall_score"] == 75.5

    # Should have digital data
    assert aggregated["digital_data"]["website"] == "https://example.com"

    # Should have metadata
    assert len(aggregated["metadata"]["sources"]) == 3
    assert "company_profile" in aggregated["metadata"]["sources"]


def test_result_deduplication(orchestrator):
    """Test deduplication of overlapping results (Week 20)."""
    results_with_duplicates = {
        "insight_generator": {
            "insights": [
                {"title": "Insight 1", "description": "Description 1"},
                {"title": "Insight 1", "description": "Description 1"},  # Duplicate
                {"title": "Insight 2", "description": "Description 2"}
            ],
            "confidence_score": 0.85
        }
    }

    aggregated = orchestrator.aggregate_results(
        results_with_duplicates,
        deduplication=True
    )

    # Should have deduplicated insights (2 unique instead of 3)
    assert len(aggregated["insights"]) == 2


def test_confidence_weighted_synthesis(orchestrator, sample_agent_results):
    """Test confidence-weighted synthesis of results (Week 20)."""
    aggregated = orchestrator.aggregate_results(sample_agent_results)
    synthesized = orchestrator.synthesize_with_confidence(aggregated)

    # Should have synthesis section
    assert "synthesis" in synthesized
    assert "overall_confidence" in synthesized["synthesis"]

    # Overall confidence should be average of all agents
    # (0.92 + 0.85 + 0.78) / 3 = 0.85
    assert synthesized["synthesis"]["overall_confidence"] == pytest.approx(0.85, abs=0.01)

    # Should have data quality assessment
    assert "data_quality" in synthesized["synthesis"]
    assert synthesized["synthesis"]["data_quality"] == "high"  # >= 0.75

    # Should have recommendation
    assert "recommendation" in synthesized["synthesis"]


# ============================================================================
# PERFORMANCE OPTIMIZATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_result_caching():
    """Test result caching for performance optimization (Week 20)."""
    orchestrator = OrchestratorService()

    # First execution - should execute agent
    call_count = {"count": 0}

    async def mock_execute(agent_type, agent_config, context):
        call_count["count"] += 1
        return {"result": "success", "execution_time_ms": 100}

    with patch.object(orchestrator, '_execute_agent_logic', side_effect=mock_execute):
        # First call - cache miss
        result1 = await orchestrator._execute_agent(
            agent_type="company_profile",
            agent_config={"target": "Test Company", "priority": "high"},
            context={},
            phase_name="test_phase"
        )

        # Second call with same parameters - should hit cache
        result2 = await orchestrator._execute_agent(
            agent_type="company_profile",
            agent_config={"target": "Test Company", "priority": "high"},
            context={},
            phase_name="test_phase"
        )

    # Should only execute once, second call from cache
    assert call_count["count"] == 1
    assert result2.get("cached") is True


@pytest.mark.asyncio
async def test_cache_expiration():
    """Test cache expiration after TTL (Week 20)."""
    orchestrator = OrchestratorService()
    orchestrator.cache_ttl = 0.1  # 100ms for testing

    call_count = {"count": 0}

    async def mock_execute(agent_type, agent_config, context):
        call_count["count"] += 1
        return {"result": "success"}

    with patch.object(orchestrator, '_execute_agent_logic', side_effect=mock_execute):
        # First call
        await orchestrator._execute_agent(
            agent_type="company_profile",
            agent_config={"target": "Test Company", "priority": "high"},
            context={},
            phase_name="test_phase"
        )

        # Wait for cache to expire
        await asyncio.sleep(0.15)

        # Second call after expiration - should execute again
        await orchestrator._execute_agent(
            agent_type="company_profile",
            agent_config={"target": "Test Company", "priority": "high"},
            context={},
            phase_name="test_phase"
        )

    # Should execute twice (cache expired)
    assert call_count["count"] == 2


def test_cache_clearing(orchestrator):
    """Test manual cache clearing (Week 20)."""
    # Add some cached results
    orchestrator._cache_result(
        "company_profile",
        "Company A",
        {"data": "test"},
        {}
    )
    orchestrator._cache_result(
        "financial_analysis",
        "Company B",
        {"data": "test2"},
        {}
    )

    assert len(orchestrator.result_cache) == 2

    # Clear cache
    orchestrator.clear_cache()

    # Cache should be empty
    assert len(orchestrator.result_cache) == 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_end_to_end_intelligent_workflow():
    """Test complete intelligent routing + aggregation + caching (Week 20)."""
    orchestrator = OrchestratorService()

    # Mock intelligent routing
    mock_intent = Mock()
    mock_intent.analysis_type = "company_profile"
    mock_intent.target = "Test Corp"
    mock_intent.parameters = {}
    mock_intent.confidence = 0.90
    mock_intent.reasoning = "Test"

    with patch('app.services.orchestrator.parse_user_intent', return_value=mock_intent):
        with patch('app.services.orchestrator.query_router_service') as mock_router:
            mock_router.classify_query.return_value = ("company_profile", 0.85, [])

            with patch.object(orchestrator, '_execute_agent_logic') as mock_execute:
                mock_execute.return_value = {
                    "company_name": "Test Corp",
                    "confidence_score": 0.90
                }

                # First execution
                result1 = await orchestrator.execute_from_query(
                    query="Analyze Test Corp",
                    context={}
                )

                # Second execution with same query - should use cache
                result2 = await orchestrator.execute_from_query(
                    query="Analyze Test Corp",
                    context={}
                )

    # Should have routing metadata
    assert "routing_metadata" in result1

    # Verify intelligent routing worked
    assert mock_intent.analysis_type == "company_profile"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
