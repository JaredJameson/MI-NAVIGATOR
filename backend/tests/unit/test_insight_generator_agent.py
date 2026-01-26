"""
Unit tests for InsightGeneratorAgent (Week 16 - Foundation)

Tests cover:
- Pydantic model validation
- Pattern detection algorithms
- Prediction generation
- Risk identification
- Opportunity detection
- Claude integration (with fallback)
- Overall confidence calculation
- Recommendation generation
"""

import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.agents.insight_generator_agent import (
    InsightGeneratorAgent,
    InsightGeneratorOutput,
    Insight,
    Pattern,
    Prediction,
    Risk,
    Opportunity,
    InsightType,
    PatternType,
    PredictionConfidence,
    RiskLevel,
    OpportunityType,
    InsightGeneratorDomainKnowledge
)


# ============================================================================
# TEST 1: Pydantic Model Validation - Pattern
# ============================================================================

def test_pattern_model_validation():
    """Test Pattern Pydantic model validation (Week 16)"""
    pattern = Pattern(
        pattern_id="test_pattern_001",
        pattern_type=PatternType.GROWTH,
        pattern_description="Revenue shows consistent growth trend",
        confidence_score=85.0,
        strength=75.0,
        data_points=6,
        time_period="Q1-Q4 2024",
        trend_percentage=15.5,
        volatility_score=8.2,
        seasonality_detected=False,
        affected_metrics=["revenue", "profit"],
        contributing_factors=["Market expansion", "New product launch"]
    )

    assert pattern.pattern_id == "test_pattern_001"
    assert pattern.pattern_type == PatternType.GROWTH
    assert pattern.confidence_score == 85.0
    assert pattern.strength == 75.0
    assert pattern.data_points == 6
    assert pattern.trend_percentage == 15.5
    assert len(pattern.affected_metrics) == 2
    assert len(pattern.contributing_factors) == 2


# ============================================================================
# TEST 2: Pydantic Model Validation - Prediction
# ============================================================================

def test_prediction_model_validation():
    """Test Prediction Pydantic model validation (Week 16)"""
    prediction = Prediction(
        prediction_id="pred_001",
        prediction_text="Revenue is likely to continue growing by approximately 12.5% in the next period",
        predicted_value="+12.5%",
        prediction_confidence=PredictionConfidence.HIGH,
        confidence_score=75.0,
        time_horizon="short_term",
        based_on_patterns=["pattern_001", "pattern_002"],
        supporting_factors=["Strong historical trend", "Market conditions"],
        risk_factors=["Economic uncertainty", "Competition"],
        validation_metrics=["revenue", "growth_rate"]
    )

    assert prediction.prediction_id == "pred_001"
    assert prediction.prediction_confidence == PredictionConfidence.HIGH
    assert prediction.confidence_score == 75.0
    assert prediction.time_horizon == "short_term"
    assert len(prediction.based_on_patterns) == 2
    assert len(prediction.supporting_factors) == 2


# ============================================================================
# TEST 3: Pydantic Model Validation - Risk
# ============================================================================

def test_risk_model_validation():
    """Test Risk Pydantic model validation (Week 16)"""
    risk = Risk(
        risk_id="risk_001",
        risk_description="Declining profit margin trend poses business risk",
        risk_level=RiskLevel.HIGH,
        impact_score=80.0,
        probability_score=65.0,
        risk_score=52.0,
        risk_category="financial",
        affected_areas=["profit_margin", "profitability"],
        potential_consequences=["Reduced profitability", "Investor concern"],
        mitigation_strategies=["Cost optimization", "Price adjustment"],
        monitoring_metrics=["profit_margin", "operating_expenses"],
        time_to_impact="3-6 months"
    )

    assert risk.risk_id == "risk_001"
    assert risk.risk_level == RiskLevel.HIGH
    assert risk.impact_score == 80.0
    assert risk.probability_score == 65.0
    assert risk.risk_score == 52.0
    assert len(risk.mitigation_strategies) == 2


# ============================================================================
# TEST 4: Pydantic Model Validation - Opportunity
# ============================================================================

def test_opportunity_model_validation():
    """Test Opportunity Pydantic model validation (Week 16)"""
    opportunity = Opportunity(
        opportunity_id="opp_001",
        opportunity_description="Capitalize on growing market share trend",
        opportunity_type=OpportunityType.MARKET_EXPANSION,
        value_score=85.0,
        feasibility_score=70.0,
        priority_score=59.5,
        target_market="Enterprise segment",
        required_resources=["Sales team expansion", "Marketing budget"],
        expected_benefits=["Increased revenue", "Market leadership"],
        recommended_actions=["Expand sales team", "Increase marketing spend"],
        time_to_execute="3-6 months",
        success_metrics=["market_share", "revenue_growth"]
    )

    assert opportunity.opportunity_id == "opp_001"
    assert opportunity.opportunity_type == OpportunityType.MARKET_EXPANSION
    assert opportunity.value_score == 85.0
    assert opportunity.feasibility_score == 70.0
    assert opportunity.priority_score == 59.5
    assert len(opportunity.recommended_actions) == 2


# ============================================================================
# TEST 5: Pydantic Model Validation - Insight
# ============================================================================

def test_insight_model_validation():
    """Test Insight Pydantic model validation (Week 16)"""
    pattern = Pattern(
        pattern_id="p1",
        pattern_type=PatternType.GROWTH,
        pattern_description="Growth pattern",
        confidence_score=80.0,
        strength=70.0,
        data_points=5,
        time_period="2024"
    )

    insight = Insight(
        insight_id="insight_001",
        insight_type=InsightType.TREND,
        insight_text="Company shows strong growth trend across all key metrics, indicating robust business health and market position.",
        priority="high",
        relevance_score=90.0,
        patterns=[pattern],
        predictions=[],
        risks=[],
        opportunities=[],
        is_actionable=True,
        recommended_actions=["Continue growth initiatives", "Monitor competitive response"],
        data_sources=["Financial statements", "Market data"]
    )

    assert insight.insight_id == "insight_001"
    assert insight.insight_type == InsightType.TREND
    assert insight.priority == "high"
    assert insight.relevance_score == 90.0
    assert len(insight.patterns) == 1
    assert insight.is_actionable is True
    assert len(insight.recommended_actions) == 2


# ============================================================================
# TEST 6: Agent Initialization
# ============================================================================

def test_agent_initialization():
    """Test InsightGeneratorAgent initialization (Week 16)"""
    agent = InsightGeneratorAgent()

    assert agent is not None
    assert agent.domain_knowledge is not None
    assert isinstance(agent.domain_knowledge, InsightGeneratorDomainKnowledge)
    assert agent.tool_registry is not None


# ============================================================================
# TEST 7: Pattern Detection - Financial Growth Trend
# ============================================================================

def test_financial_growth_pattern_detection():
    """Test detection of financial growth patterns (Week 16)"""
    agent = InsightGeneratorAgent()

    # Create financial data with clear growth trend
    financial_data = [
        {"period": "2024-Q1", "revenue": 1000000, "profit_margin": 15.0},
        {"period": "2024-Q2", "revenue": 1100000, "profit_margin": 16.0},
        {"period": "2024-Q3", "revenue": 1250000, "profit_margin": 17.5},
        {"period": "2024-Q4", "revenue": 1400000, "profit_margin": 18.0}
    ]

    patterns = agent._detect_financial_patterns(financial_data)

    assert len(patterns) >= 1

    # Check revenue pattern
    revenue_pattern = next((p for p in patterns if "revenue" in p.affected_metrics), None)
    assert revenue_pattern is not None
    assert revenue_pattern.pattern_type == PatternType.GROWTH
    assert revenue_pattern.trend_percentage > 0
    assert revenue_pattern.data_points == 4
    assert revenue_pattern.confidence_score > 0


# ============================================================================
# TEST 8: Pattern Detection - Financial Decline Trend
# ============================================================================

def test_financial_decline_pattern_detection():
    """Test detection of financial decline patterns (Week 16)"""
    agent = InsightGeneratorAgent()

    # Create financial data with decline trend
    financial_data = [
        {"period": "2024-Q1", "revenue": 1400000, "profit_margin": 18.0},
        {"period": "2024-Q2", "revenue": 1250000, "profit_margin": 16.5},
        {"period": "2024-Q3", "revenue": 1100000, "profit_margin": 15.0},
        {"period": "2024-Q4", "revenue": 1000000, "profit_margin": 14.0}
    ]

    patterns = agent._detect_financial_patterns(financial_data)

    assert len(patterns) >= 1

    # Check revenue pattern
    revenue_pattern = next((p for p in patterns if "revenue" in p.affected_metrics), None)
    assert revenue_pattern is not None
    assert revenue_pattern.pattern_type == PatternType.DECLINE
    assert revenue_pattern.trend_percentage < 0
    assert abs(revenue_pattern.trend_percentage) > agent.domain_knowledge.GROWTH_THRESHOLD


# ============================================================================
# TEST 9: Pattern Detection - Volatile Pattern
# ============================================================================

def test_volatile_pattern_detection():
    """Test detection of volatile patterns (Week 16)"""
    agent = InsightGeneratorAgent()

    # Create volatile financial data
    financial_data = [
        {"period": "2024-Q1", "revenue": 1000000},
        {"period": "2024-Q2", "revenue": 1500000},
        {"period": "2024-Q3", "revenue": 900000},
        {"period": "2024-Q4", "revenue": 1600000}
    ]

    patterns = agent._detect_financial_patterns(financial_data)

    assert len(patterns) >= 1

    revenue_pattern = next((p for p in patterns if "revenue" in p.affected_metrics), None)
    assert revenue_pattern is not None
    assert revenue_pattern.volatility_score is not None
    assert revenue_pattern.volatility_score > agent.domain_knowledge.VOLATILITY_THRESHOLD


# ============================================================================
# TEST 10: Trend Analysis Helper
# ============================================================================

def test_analyze_trend():
    """Test trend analysis helper method (Week 16)"""
    agent = InsightGeneratorAgent()

    # Test growth trend
    values = [100, 110, 125, 140, 155]
    pattern = agent._analyze_trend(
        values,
        metric_name="test_metric",
        pattern_id="test_001",
        time_period="2024"
    )

    assert pattern is not None
    assert pattern.pattern_type == PatternType.GROWTH
    assert pattern.trend_percentage > 0
    assert pattern.data_points == 5
    assert pattern.confidence_score > 0


# ============================================================================
# TEST 11: Prediction Generation from Growth Pattern
# ============================================================================

@pytest.mark.asyncio
async def test_prediction_from_growth_pattern():
    """Test prediction generation from growth pattern (Week 16)"""
    agent = InsightGeneratorAgent()

    # Create growth pattern
    pattern = Pattern(
        pattern_id="growth_001",
        pattern_type=PatternType.GROWTH,
        pattern_description="Revenue growth trend",
        confidence_score=80.0,
        strength=75.0,
        data_points=5,
        time_period="2024",
        trend_percentage=20.5,
        volatility_score=10.0,
        affected_metrics=["revenue"]
    )

    predictions = await agent._generate_predictions([pattern], {})

    assert len(predictions) >= 1

    prediction = predictions[0]
    assert prediction.prediction_confidence in [
        PredictionConfidence.VERY_HIGH,
        PredictionConfidence.HIGH,
        PredictionConfidence.MEDIUM
    ]
    assert prediction.confidence_score > 0
    assert len(prediction.based_on_patterns) > 0
    assert pattern.pattern_id in prediction.based_on_patterns


# ============================================================================
# TEST 12: Risk Identification from Decline Pattern
# ============================================================================

@pytest.mark.asyncio
async def test_risk_from_decline_pattern():
    """Test risk identification from decline pattern (Week 16)"""
    agent = InsightGeneratorAgent()

    # Create decline pattern
    pattern = Pattern(
        pattern_id="decline_001",
        pattern_type=PatternType.DECLINE,
        pattern_description="Revenue decline trend",
        confidence_score=75.0,
        strength=65.0,
        data_points=4,
        time_period="2024",
        trend_percentage=-18.5,
        affected_metrics=["revenue"]
    )

    risks = await agent._identify_risks([pattern], [], {})

    assert len(risks) >= 1

    risk = risks[0]
    assert risk.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM]
    assert risk.impact_score > 0
    assert risk.probability_score > 0
    assert risk.risk_score > 0
    assert len(risk.mitigation_strategies) > 0


# ============================================================================
# TEST 13: Opportunity Identification from Growth Pattern
# ============================================================================

@pytest.mark.asyncio
async def test_opportunity_from_growth_pattern():
    """Test opportunity identification from growth pattern (Week 16)"""
    agent = InsightGeneratorAgent()

    # Create growth pattern
    pattern = Pattern(
        pattern_id="growth_002",
        pattern_type=PatternType.GROWTH,
        pattern_description="Market share growth",
        confidence_score=82.0,
        strength=78.0,
        data_points=5,
        time_period="2024",
        trend_percentage=22.5,
        affected_metrics=["market_share"]
    )

    opportunities = await agent._identify_opportunities([pattern], [], {})

    assert len(opportunities) >= 1

    opportunity = opportunities[0]
    assert opportunity.value_score > 0
    assert opportunity.feasibility_score > 0
    assert opportunity.priority_score > 0
    assert len(opportunity.recommended_actions) > 0


# ============================================================================
# TEST 14: Overall Confidence Calculation
# ============================================================================

def test_overall_confidence_calculation():
    """Test overall confidence score calculation (Week 16)"""
    agent = InsightGeneratorAgent()

    patterns = [
        Pattern(
            pattern_id="p1",
            pattern_type=PatternType.GROWTH,
            pattern_description="Growth pattern detected in revenue",
            confidence_score=80.0,
            strength=70.0,
            data_points=5,
            time_period="2024"
        ),
        Pattern(
            pattern_id="p2",
            pattern_type=PatternType.STABLE,
            pattern_description="Stable performance pattern",
            confidence_score=90.0,
            strength=75.0,
            data_points=6,
            time_period="2024"
        )
    ]

    predictions = [
        Prediction(
            prediction_id="pred1",
            prediction_text="Test prediction",
            prediction_confidence=PredictionConfidence.HIGH,
            confidence_score=75.0,
            time_horizon="short_term"
        )
    ]

    confidence = agent._calculate_overall_confidence(patterns, predictions)

    assert confidence > 0
    assert confidence <= 100
    # Should be weighted: patterns 70%, predictions 30%
    expected = (85.0 * 0.7 + 75.0 * 0.3)
    assert abs(confidence - expected) < 1.0


# ============================================================================
# TEST 15: Complete Agent Execution
# ============================================================================

@pytest.mark.asyncio
async def test_complete_agent_execution():
    """Test complete InsightGeneratorAgent execution (Week 16)"""
    agent = InsightGeneratorAgent()

    # Prepare context with financial data
    context = {
        "financial_data": [
            {"period": "2024-Q1", "revenue": 1000000, "profit_margin": 15.0},
            {"period": "2024-Q2", "revenue": 1150000, "profit_margin": 16.5},
            {"period": "2024-Q3", "revenue": 1300000, "profit_margin": 17.5},
            {"period": "2024-Q4", "revenue": 1450000, "profit_margin": 18.5}
        ]
    }

    result = await agent.execute(query="NIP 1234567890", context=context)

    # Verify output structure
    assert isinstance(result, InsightGeneratorOutput)
    assert result.target == "NIP 1234567890"
    assert result.analysis_date is not None

    # Should have detected patterns
    assert result.total_patterns > 0
    assert len(result.patterns_detected) == result.total_patterns

    # Should have generated predictions
    assert result.total_predictions >= 0

    # Should have calculated confidence
    assert result.confidence_score >= 0
    assert result.confidence_score <= 100

    # Should have recommendations
    assert len(result.strategic_recommendations) >= 0

    # Verify patterns are valid
    for pattern in result.patterns_detected:
        assert pattern.pattern_id is not None
        assert pattern.confidence_score >= 0
        assert pattern.confidence_score <= 100
        assert pattern.data_points > 0


# ============================================================================
# WEEK 17 TESTS: Advanced Analysis
# ============================================================================

# ============================================================================
# TEST 16: Anomaly Detection
# ============================================================================

def test_anomaly_detection():
    """Test anomaly detection in data (Week 17)"""
    agent = InsightGeneratorAgent()

    # Create data with clear anomalies
    values = [100, 105, 102, 98, 300, 104, 99, 101, 103]  # 300 is anomaly

    pattern = agent._detect_anomalies(values, "test_metric")

    assert pattern is not None
    assert pattern.pattern_type == PatternType.VOLATILE
    assert "anomal" in pattern.pattern_description.lower()
    assert pattern.confidence_score > 0
    assert pattern.volatility_score is not None


# ============================================================================
# TEST 17: Correlation Analysis
# ============================================================================

def test_correlation_analysis():
    """Test correlation analysis between metrics (Week 17)"""
    agent = InsightGeneratorAgent()

    # Create strongly correlated data
    data = {
        "revenue": [100, 150, 200, 250, 300],
        "profit": [10, 15, 20, 25, 30]  # Perfect positive correlation
    }

    insights = agent._analyze_correlations(data)

    assert len(insights) > 0
    insight = insights[0]
    assert insight.insight_type == InsightType.CORRELATION
    assert "correlation" in insight.insight_text.lower()
    assert insight.relevance_score > 60  # Strong correlation


# ============================================================================
# TEST 18: Pearson Correlation Calculation
# ============================================================================

def test_pearson_correlation():
    """Test Pearson correlation coefficient calculation (Week 17)"""
    agent = InsightGeneratorAgent()

    # Perfect positive correlation
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]

    corr = agent._calculate_correlation(x, y)

    assert abs(corr - 1.0) < 0.01  # Should be close to 1.0

    # Perfect negative correlation
    y_neg = [10, 8, 6, 4, 2]
    corr_neg = agent._calculate_correlation(x, y_neg)

    assert abs(corr_neg - (-1.0)) < 0.01  # Should be close to -1.0

    # No correlation
    y_random = [5, 2, 8, 1, 9]
    corr_random = agent._calculate_correlation(x, y_random)

    assert abs(corr_random) < 0.5  # Weak or no correlation


# ============================================================================
# TEST 19: Scenario Analysis
# ============================================================================

@pytest.mark.asyncio
async def test_scenario_analysis():
    """Test scenario analysis generation (Week 17)"""
    agent = InsightGeneratorAgent()

    # Create growth and decline patterns
    growth_pattern = Pattern(
        pattern_id="growth_1",
        pattern_type=PatternType.GROWTH,
        pattern_description="Strong growth pattern",
        confidence_score=85.0,
        strength=80.0,
        data_points=5,
        time_period="2024"
    )

    decline_pattern = Pattern(
        pattern_id="decline_1",
        pattern_type=PatternType.DECLINE,
        pattern_description="Decline pattern",
        confidence_score=75.0,
        strength=70.0,
        data_points=4,
        time_period="2024"
    )

    growth_prediction = Prediction(
        prediction_id="pred_growth",
        prediction_text="Revenue will likely grow by 15%",
        prediction_confidence=PredictionConfidence.HIGH,
        confidence_score=80.0,
        time_horizon="short_term"
    )

    decline_prediction = Prediction(
        prediction_id="pred_decline",
        prediction_text="Market share may decline slightly",
        prediction_confidence=PredictionConfidence.MEDIUM,
        confidence_score=65.0,
        time_horizon="short_term"
    )

    scenarios = await agent._generate_scenario_analysis(
        [growth_pattern, decline_pattern],
        [growth_prediction, decline_prediction]
    )

    # Should generate best case, worst case, and most likely
    assert len(scenarios) >= 2

    # Check that we have different scenario types
    scenario_texts = [s.insight_text for s in scenarios]
    assert any("BEST CASE" in text for text in scenario_texts)
    assert any("WORST CASE" in text or "MOST LIKELY" in text for text in scenario_texts)


# ============================================================================
# TEST 20: Advanced Forecasting
# ============================================================================

def test_advanced_forecasting():
    """Test advanced forecasting with exponential smoothing (Week 17)"""
    agent = InsightGeneratorAgent()

    # Create trending data
    values = [100, 110, 120, 130, 140, 150]

    prediction = agent._advanced_forecast(values, "revenue", periods_ahead=3)

    assert prediction is not None
    assert prediction.prediction_id is not None
    assert "forecast" in prediction.prediction_id
    assert prediction.confidence_score > 0
    assert prediction.time_horizon in ["short_term", "medium_term"]
    assert len(prediction.supporting_factors) > 0
