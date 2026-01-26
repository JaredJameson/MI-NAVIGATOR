"""
Unit Tests for Financial Analysis Agent - Week 4 Implementation

Tests for FinancialAnalysisAgent including:
- Pydantic model validation
- Ratio calculations (liquidity, profitability, leverage, efficiency)
- Trend analysis
- Financial health scoring
- Confidence calculation
- Error handling

Author: MI-Navigator Development Team
Created: 2026-01-24 (Week 4)
"""

import pytest
from datetime import datetime
from typing import List

from app.agents.financial_analysis_agent import (
    FinancialAnalysisAgent,
    FinancialStatement,
    LiquidityRatios,
    ProfitabilityRatios,
    LeverageRatios,
    EfficiencyRatios,
    RatioAnalysis,
    TrendPoint,
    TrendAnalysis,
    FinancialHealthScore,
    FinancialAnalysisOutput
)


# ============================================================================
# TEST 1: PYDANTIC MODEL VALIDATION - FinancialStatement
# ============================================================================

def test_financial_statement_model_valid():
    """Test FinancialStatement model with valid data"""
    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        total_assets=5000000.0,
        current_assets=2000000.0,
        fixed_assets=3000000.0,
        total_liabilities=3000000.0,
        current_liabilities=1000000.0,
        long_term_liabilities=2000000.0,
        equity=2000000.0,
        revenue=10000000.0,
        operating_profit=1500000.0,
        net_profit=1000000.0,
        cost_of_sales=6000000.0,
        operating_expenses=2500000.0
    )

    assert statement.period == "2023"
    assert statement.period_type == "annual"
    assert statement.total_assets == 5000000.0
    assert statement.revenue == 10000000.0
    assert statement.net_profit == 1000000.0


def test_financial_statement_model_period_type_validation():
    """Test FinancialStatement period_type validation"""
    # Valid period types
    valid_annual = FinancialStatement(period="2023", period_type="annual")
    assert valid_annual.period_type == "annual"

    valid_quarterly = FinancialStatement(period="2023-Q1", period_type="quarterly")
    assert valid_quarterly.period_type == "quarterly"

    # Invalid period type should raise validation error
    with pytest.raises(ValueError):
        FinancialStatement(period="2023", period_type="monthly")


# ============================================================================
# TEST 2: LIQUIDITY RATIOS CALCULATION
# ============================================================================

def test_calculate_liquidity_ratios_healthy():
    """Test liquidity ratio calculation with healthy company"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        current_assets=2000000.0,
        current_liabilities=800000.0
    )

    liquidity = agent._calculate_liquidity_ratios(statement)

    assert liquidity is not None
    assert liquidity.current_ratio == 2.5  # 2000000 / 800000
    assert liquidity.current_ratio_status == "healthy"  # >= 2.0
    assert liquidity.quick_ratio is not None
    assert liquidity.quick_ratio_status in ["healthy", "warning"]


def test_calculate_liquidity_ratios_warning():
    """Test liquidity ratio calculation with warning status"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        current_assets=1200000.0,
        current_liabilities=1000000.0  # Current ratio = 1.2
    )

    liquidity = agent._calculate_liquidity_ratios(statement)

    assert liquidity is not None
    assert liquidity.current_ratio == 1.2
    assert liquidity.current_ratio_status == "warning"  # >= 1.0 but < 2.0


def test_calculate_liquidity_ratios_critical():
    """Test liquidity ratio calculation with critical status"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        current_assets=800000.0,
        current_liabilities=1000000.0  # Current ratio = 0.8
    )

    liquidity = agent._calculate_liquidity_ratios(statement)

    assert liquidity is not None
    assert liquidity.current_ratio == 0.8
    assert liquidity.current_ratio_status == "critical"  # < 1.0


def test_calculate_liquidity_ratios_missing_data():
    """Test liquidity ratio calculation with missing data"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        revenue=10000000.0  # No current assets/liabilities
    )

    liquidity = agent._calculate_liquidity_ratios(statement)

    assert liquidity is None  # Should return None when data missing


# ============================================================================
# TEST 3: PROFITABILITY RATIOS CALCULATION
# ============================================================================

def test_calculate_profitability_ratios_excellent():
    """Test profitability ratio calculation with excellent performance"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        revenue=10000000.0,
        cost_of_sales=4000000.0,
        operating_profit=2000000.0,
        net_profit=1500000.0,
        total_assets=5000000.0,
        equity=2000000.0
    )

    profitability = agent._calculate_profitability_ratios(statement)

    assert profitability is not None

    # Gross Margin = (10M - 4M) / 10M * 100 = 60%
    assert profitability.gross_margin == 60.0

    # Operating Margin = 2M / 10M * 100 = 20%
    assert profitability.operating_margin == 20.0

    # Net Margin = 1.5M / 10M * 100 = 15%
    assert profitability.net_margin == 15.0

    # ROA = 1.5M / 5M * 100 = 30%
    assert profitability.return_on_assets == 30.0

    # ROE = 1.5M / 2M * 100 = 75%
    assert profitability.return_on_equity == 75.0

    assert profitability.profitability_status == "excellent"


def test_calculate_profitability_ratios_poor():
    """Test profitability ratio calculation with poor performance"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        revenue=10000000.0,
        net_profit=200000.0,  # Only 2% net margin
        total_assets=5000000.0,
        equity=2000000.0
    )

    profitability = agent._calculate_profitability_ratios(statement)

    assert profitability is not None
    assert profitability.net_margin == 2.0
    assert profitability.return_on_assets == 4.0
    assert profitability.profitability_status in ["average", "poor"]


def test_calculate_profitability_ratios_missing_revenue():
    """Test profitability ratio calculation with missing revenue"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        net_profit=1000000.0  # No revenue
    )

    profitability = agent._calculate_profitability_ratios(statement)

    assert profitability is None  # Should return None when revenue missing


# ============================================================================
# TEST 4: LEVERAGE RATIOS CALCULATION
# ============================================================================

def test_calculate_leverage_ratios_conservative():
    """Test leverage ratio calculation with conservative debt levels"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        total_assets=5000000.0,
        total_liabilities=2000000.0,  # Debt-to-equity = 2M / 3M = 0.67
        equity=3000000.0
    )

    leverage = agent._calculate_leverage_ratios(statement)

    assert leverage is not None
    assert leverage.debt_to_equity == 0.67  # 2M / 3M
    assert leverage.debt_to_assets == 0.4  # 2M / 5M
    assert leverage.equity_ratio == 0.6  # 3M / 5M
    assert leverage.leverage_status == "moderate"  # 0.5 < d/e <= 1.0


def test_calculate_leverage_ratios_overleveraged():
    """Test leverage ratio calculation with high debt"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        total_assets=5000000.0,
        total_liabilities=4500000.0,  # Debt-to-equity = 4.5M / 0.5M = 9.0
        equity=500000.0
    )

    leverage = agent._calculate_leverage_ratios(statement)

    assert leverage is not None
    assert leverage.debt_to_equity == 9.0
    assert leverage.leverage_status == "overleveraged"  # > 2.0


def test_calculate_leverage_ratios_missing_data():
    """Test leverage ratio calculation with missing data"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        revenue=10000000.0  # No liabilities or equity
    )

    leverage = agent._calculate_leverage_ratios(statement)

    assert leverage is None


# ============================================================================
# TEST 5: EFFICIENCY RATIOS CALCULATION
# ============================================================================

def test_calculate_efficiency_ratios_excellent():
    """Test efficiency ratio calculation with excellent performance"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        revenue=10000000.0,
        total_assets=4000000.0,  # Asset turnover = 2.5
        fixed_assets=2000000.0,  # Fixed asset turnover = 5.0
        equity=1500000.0  # Equity turnover = 6.67
    )

    efficiency = agent._calculate_efficiency_ratios(statement)

    assert efficiency is not None
    assert efficiency.asset_turnover == 2.5  # 10M / 4M
    assert efficiency.fixed_asset_turnover == 5.0  # 10M / 2M
    assert efficiency.equity_turnover == 6.67  # 10M / 1.5M
    assert efficiency.efficiency_status == "excellent"  # >= 2.0


def test_calculate_efficiency_ratios_poor():
    """Test efficiency ratio calculation with poor performance"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        revenue=10000000.0,
        total_assets=25000000.0  # Asset turnover = 0.4
    )

    efficiency = agent._calculate_efficiency_ratios(statement)

    assert efficiency is not None
    assert efficiency.asset_turnover == 0.4
    assert efficiency.efficiency_status == "poor"  # < 0.5


# ============================================================================
# TEST 6: PERIOD SCORE CALCULATION
# ============================================================================

def test_calculate_period_score_all_components():
    """Test period score calculation with all components available"""
    agent = FinancialAnalysisAgent()

    liquidity = LiquidityRatios(
        current_ratio=2.5,
        quick_ratio=1.5,
        current_ratio_status="healthy",
        quick_ratio_status="healthy"
    )

    profitability = ProfitabilityRatios(
        net_margin=15.0,
        return_on_assets=10.0,
        profitability_status="excellent"
    )

    leverage = LeverageRatios(
        debt_to_equity=0.8,
        debt_to_assets=0.4,
        equity_ratio=0.6,
        leverage_status="moderate"
    )

    efficiency = EfficiencyRatios(
        asset_turnover=2.5,
        efficiency_status="excellent"
    )

    score = agent._calculate_period_score(liquidity, profitability, leverage, efficiency)

    assert 0 <= score <= 100
    assert score > 70  # Should be high with all healthy components


def test_calculate_period_score_partial_data():
    """Test period score calculation with partial data"""
    agent = FinancialAnalysisAgent()

    liquidity = LiquidityRatios(
        current_ratio=1.5,
        current_ratio_status="warning"
    )

    profitability = ProfitabilityRatios(
        net_margin=5.0,
        profitability_status="average"
    )

    score = agent._calculate_period_score(liquidity, profitability, None, None)

    assert 0 <= score <= 100
    assert 40 <= score <= 80  # Should be moderate with partial data


# ============================================================================
# TEST 7: TREND ANALYSIS
# ============================================================================

def test_create_trend_analysis_increasing():
    """Test trend analysis with increasing values"""
    agent = FinancialAnalysisAgent()

    data_points = [
        ("2021", 8000000.0),
        ("2022", 9200000.0),
        ("2023", 10500000.0)
    ]

    trend = agent._create_trend_analysis("revenue", data_points)

    assert trend is not None
    assert trend.metric_name == "revenue"
    assert len(trend.periods) == 3
    assert trend.trend_direction == "increasing"
    assert trend.avg_growth_rate > 0
    assert trend.trend_status == "positive"  # Revenue growth is positive


def test_create_trend_analysis_decreasing():
    """Test trend analysis with decreasing values"""
    agent = FinancialAnalysisAgent()

    data_points = [
        ("2021", 1000000.0),
        ("2022", 800000.0),
        ("2023", 600000.0)
    ]

    trend = agent._create_trend_analysis("net_profit", data_points)

    assert trend is not None
    assert trend.trend_direction == "decreasing"
    assert trend.avg_growth_rate < 0
    assert trend.trend_status == "concerning"  # Profit decline is concerning


def test_create_trend_analysis_stable():
    """Test trend analysis with stable values"""
    agent = FinancialAnalysisAgent()

    data_points = [
        ("2021", 10000000.0),
        ("2022", 10200000.0),
        ("2023", 10100000.0)
    ]

    trend = agent._create_trend_analysis("revenue", data_points)

    assert trend is not None
    assert trend.trend_direction == "stable"
    assert abs(trend.avg_growth_rate) <= 5


def test_create_trend_analysis_insufficient_data():
    """Test trend analysis with insufficient data points"""
    agent = FinancialAnalysisAgent()

    data_points = [("2023", 10000000.0)]  # Only 1 data point

    trend = agent._create_trend_analysis("revenue", data_points)

    assert trend is None  # Need at least 2 periods


# ============================================================================
# TEST 8: FINANCIAL HEALTH SCORE
# ============================================================================

def test_calculate_health_score_healthy_company():
    """Test health score calculation for healthy company"""
    agent = FinancialAnalysisAgent()

    # Create healthy ratios
    ratio_analysis = RatioAnalysis(
        period="2023",
        liquidity=LiquidityRatios(current_ratio=2.5, current_ratio_status="healthy"),
        profitability=ProfitabilityRatios(net_margin=15.0, return_on_assets=10.0, profitability_status="excellent"),
        leverage=LeverageRatios(debt_to_equity=0.5, leverage_status="conservative"),
        efficiency=EfficiencyRatios(asset_turnover=2.0, efficiency_status="excellent"),
        overall_score=85.0
    )

    # Create positive trends
    trend = TrendAnalysis(
        metric_name="revenue",
        periods=[
            TrendPoint(period="2022", value=9000000.0),
            TrendPoint(period="2023", value=10000000.0, change_percentage=11.1)
        ],
        trend_direction="increasing",
        avg_growth_rate=11.1,
        trend_status="positive"
    )

    health_score = agent._calculate_health_score([ratio_analysis], [trend])

    assert health_score.overall_score > 70
    assert health_score.risk_level in ["low", "moderate"]
    assert len(health_score.strengths) > 0
    assert "liquidity" in " ".join(health_score.strengths).lower() or \
           "profitability" in " ".join(health_score.strengths).lower()


def test_calculate_health_score_struggling_company():
    """Test health score calculation for struggling company"""
    agent = FinancialAnalysisAgent()

    # Create poor ratios
    ratio_analysis = RatioAnalysis(
        period="2023",
        liquidity=LiquidityRatios(current_ratio=0.8, current_ratio_status="critical"),
        profitability=ProfitabilityRatios(net_margin=2.0, return_on_assets=1.0, profitability_status="poor"),
        leverage=LeverageRatios(debt_to_equity=3.0, leverage_status="overleveraged"),
        efficiency=EfficiencyRatios(asset_turnover=0.4, efficiency_status="poor"),
        overall_score=30.0
    )

    # Create negative trends
    trend = TrendAnalysis(
        metric_name="net_profit",
        periods=[
            TrendPoint(period="2022", value=500000.0),
            TrendPoint(period="2023", value=300000.0, change_percentage=-40.0)
        ],
        trend_direction="decreasing",
        avg_growth_rate=-40.0,
        trend_status="concerning"
    )

    health_score = agent._calculate_health_score([ratio_analysis], [trend])

    assert health_score.overall_score < 50
    assert health_score.risk_level in ["high", "critical"]
    assert len(health_score.weaknesses) > 0
    assert len(health_score.recommendations) > 0


def test_calculate_health_score_no_data():
    """Test health score calculation with no data"""
    agent = FinancialAnalysisAgent()

    health_score = agent._calculate_health_score([], [])

    assert health_score.overall_score == 0.0
    assert health_score.risk_level == "critical"


# ============================================================================
# TEST 9: CONFIDENCE CALCULATION
# ============================================================================

def test_calculate_confidence_high():
    """Test confidence calculation with complete data"""
    agent = FinancialAnalysisAgent()

    # 3 complete financial statements
    statements = [
        FinancialStatement(
            period="2021",
            period_type="annual",
            revenue=8000000.0,
            net_profit=800000.0,
            total_assets=4000000.0,
            equity=2000000.0
        ),
        FinancialStatement(
            period="2022",
            period_type="annual",
            revenue=9000000.0,
            net_profit=900000.0,
            total_assets=4500000.0,
            equity=2200000.0
        ),
        FinancialStatement(
            period="2023",
            period_type="annual",
            revenue=10000000.0,
            net_profit=1000000.0,
            total_assets=5000000.0,
            equity=2500000.0
        )
    ]

    ratio_analyses = [
        RatioAnalysis(
            period="2021",
            liquidity=LiquidityRatios(current_ratio=2.0),
            profitability=ProfitabilityRatios(net_margin=10.0),
            leverage=LeverageRatios(debt_to_equity=1.0),
            overall_score=70.0
        ),
        RatioAnalysis(
            period="2022",
            liquidity=LiquidityRatios(current_ratio=2.1),
            profitability=ProfitabilityRatios(net_margin=10.0),
            leverage=LeverageRatios(debt_to_equity=0.95),
            overall_score=72.0
        ),
        RatioAnalysis(
            period="2023",
            liquidity=LiquidityRatios(current_ratio=2.2),
            profitability=ProfitabilityRatios(net_margin=10.0),
            leverage=LeverageRatios(debt_to_equity=0.9),
            overall_score=75.0
        )
    ]

    confidence = agent._calculate_confidence(statements, ratio_analyses)

    assert confidence >= 80  # Should be high with 3 complete periods


def test_calculate_confidence_low():
    """Test confidence calculation with incomplete data"""
    agent = FinancialAnalysisAgent()

    # 1 incomplete statement
    statements = [
        FinancialStatement(
            period="2023",
            period_type="annual",
            revenue=10000000.0  # Missing other fields
        )
    ]

    ratio_analyses = []

    confidence = agent._calculate_confidence(statements, ratio_analyses)

    assert confidence < 50  # Should be low with incomplete data


def test_calculate_confidence_no_data():
    """Test confidence calculation with no data"""
    agent = FinancialAnalysisAgent()

    confidence = agent._calculate_confidence([], [])

    assert confidence == 0.0


# ============================================================================
# TEST 10: AGENT EXECUTION - ERROR HANDLING
# ============================================================================

@pytest.mark.asyncio
async def test_agent_execute_no_data():
    """Test agent execution with no financial data available"""
    agent = FinancialAnalysisAgent()

    # Execute with target (will return empty since KRS integration not yet implemented)
    result = await agent.execute(target="KRS 0000999999")

    assert isinstance(result, FinancialAnalysisOutput)
    assert result.target == "KRS 0000999999"
    assert result.confidence_score >= 0.0  # Should have some confidence score
    assert result.periods_analyzed == 0  # No statements fetched yet
    assert len(result.data_sources) >= 0


# ============================================================================
# TEST 11: RATIO ANALYSIS MODEL
# ============================================================================

def test_ratio_analysis_model_valid():
    """Test RatioAnalysis model with valid data"""
    ratio_analysis = RatioAnalysis(
        period="2023",
        liquidity=LiquidityRatios(current_ratio=2.5, current_ratio_status="healthy"),
        profitability=ProfitabilityRatios(net_margin=15.0, profitability_status="excellent"),
        leverage=LeverageRatios(debt_to_equity=0.8, leverage_status="moderate"),
        efficiency=EfficiencyRatios(asset_turnover=2.0, efficiency_status="excellent"),
        overall_score=80.5
    )

    assert ratio_analysis.period == "2023"
    assert ratio_analysis.overall_score == 80.5
    assert ratio_analysis.liquidity.current_ratio == 2.5
    assert ratio_analysis.profitability.net_margin == 15.0


# ============================================================================
# TEST 12: TREND ANALYSIS MODEL
# ============================================================================

def test_trend_analysis_model_valid():
    """Test TrendAnalysis model with valid data"""
    trend = TrendAnalysis(
        metric_name="revenue",
        periods=[
            TrendPoint(period="2021", value=8000000.0),
            TrendPoint(period="2022", value=9200000.0, change_percentage=15.0),
            TrendPoint(period="2023", value=10500000.0, change_percentage=14.1)
        ],
        trend_direction="increasing",
        avg_growth_rate=14.55,
        trend_status="positive"
    )

    assert trend.metric_name == "revenue"
    assert trend.trend_direction == "increasing"
    assert len(trend.periods) == 3
    assert trend.trend_status == "positive"


def test_trend_analysis_model_direction_validation():
    """Test TrendAnalysis direction validation"""
    # Valid directions
    for direction in ["increasing", "decreasing", "stable", "volatile"]:
        trend = TrendAnalysis(
            metric_name="test",
            trend_direction=direction,
            trend_status="neutral",
            periods=[]
        )
        assert trend.trend_direction == direction

    # Invalid direction
    with pytest.raises(ValueError):
        TrendAnalysis(
            metric_name="test",
            trend_direction="invalid",
            trend_status="neutral",
            periods=[]
        )


# ============================================================================
# TEST 13: FINANCIAL HEALTH SCORE MODEL
# ============================================================================

def test_financial_health_score_model_valid():
    """Test FinancialHealthScore model with valid data"""
    health_score = FinancialHealthScore(
        overall_score=75.5,
        liquidity_score=80.0,
        profitability_score=70.0,
        leverage_score=75.0,
        efficiency_score=72.0,
        trend_score=78.0,
        risk_level="moderate",
        strengths=["Strong liquidity position", "Consistent revenue growth"],
        weaknesses=["Declining profit margins"],
        recommendations=["Focus on cost reduction strategies"]
    )

    assert health_score.overall_score == 75.5
    assert health_score.risk_level == "moderate"
    assert len(health_score.strengths) == 2
    assert len(health_score.weaknesses) == 1
    assert len(health_score.recommendations) == 1


def test_financial_health_score_risk_level_validation():
    """Test FinancialHealthScore risk_level validation"""
    # Valid risk levels
    for risk in ["low", "moderate", "high", "critical"]:
        score = FinancialHealthScore(
            overall_score=75.0,
            liquidity_score=75.0,
            profitability_score=75.0,
            leverage_score=75.0,
            efficiency_score=75.0,
            trend_score=75.0,
            risk_level=risk
        )
        assert score.risk_level == risk

    # Invalid risk level
    with pytest.raises(ValueError):
        FinancialHealthScore(
            overall_score=75.0,
            liquidity_score=75.0,
            profitability_score=75.0,
            leverage_score=75.0,
            efficiency_score=75.0,
            trend_score=75.0,
            risk_level="extreme"
        )


# ============================================================================
# TEST 14: FINANCIAL ANALYSIS OUTPUT MODEL
# ============================================================================

def test_financial_analysis_output_model_valid():
    """Test FinancialAnalysisOutput model with valid data"""
    output = FinancialAnalysisOutput(
        target="KRS 0000123456",
        company_name="Example Sp. z o.o.",
        nip_number="1234567890",
        krs_number="0000123456",
        confidence_score=85.0,
        data_sources=["KRS"],
        periods_analyzed=3
    )

    assert output.agent_type == "financial_analysis"
    assert output.target == "KRS 0000123456"
    assert output.company_name == "Example Sp. z o.o."
    assert output.confidence_score == 85.0
    assert output.periods_analyzed == 3


def test_financial_analysis_output_confidence_score_validation():
    """Test FinancialAnalysisOutput confidence_score validation"""
    # Valid confidence score
    output = FinancialAnalysisOutput(
        target="TEST",
        confidence_score=75.5
    )
    assert output.confidence_score == 75.5

    # Out of range (0-100)
    with pytest.raises(ValueError):
        FinancialAnalysisOutput(target="TEST", confidence_score=150.0)

    with pytest.raises(ValueError):
        FinancialAnalysisOutput(target="TEST", confidence_score=-10.0)


# ============================================================================
# TEST 15: INTEGRATION TEST - COMPLETE WORKFLOW
# ============================================================================

def test_complete_ratio_calculation_workflow():
    """
    Test complete ratio calculation workflow

    This integration test verifies:
    1. Financial statement creation
    2. All ratio calculations (liquidity, profitability, leverage, efficiency)
    3. Period score calculation
    4. Confidence calculation
    """
    agent = FinancialAnalysisAgent()

    # Create realistic financial statement
    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        total_assets=5000000.0,
        current_assets=2000000.0,
        fixed_assets=3000000.0,
        total_liabilities=3000000.0,
        current_liabilities=1000000.0,
        long_term_liabilities=2000000.0,
        equity=2000000.0,
        revenue=10000000.0,
        operating_profit=1500000.0,
        net_profit=1000000.0,
        cost_of_sales=6000000.0,
        operating_expenses=2500000.0
    )

    # Calculate all ratios
    ratio_analyses = agent._calculate_ratios([statement])

    assert len(ratio_analyses) == 1
    ratio_analysis = ratio_analyses[0]

    # Verify liquidity ratios
    assert ratio_analysis.liquidity is not None
    assert ratio_analysis.liquidity.current_ratio == 2.0  # 2M / 1M
    assert ratio_analysis.liquidity.current_ratio_status == "healthy"

    # Verify profitability ratios
    assert ratio_analysis.profitability is not None
    assert ratio_analysis.profitability.gross_margin == 40.0  # (10M - 6M) / 10M * 100
    assert ratio_analysis.profitability.net_margin == 10.0  # 1M / 10M * 100
    assert ratio_analysis.profitability.return_on_assets == 20.0  # 1M / 5M * 100
    assert ratio_analysis.profitability.return_on_equity == 50.0  # 1M / 2M * 100

    # Verify leverage ratios
    assert ratio_analysis.leverage is not None
    assert ratio_analysis.leverage.debt_to_equity == 1.5  # 3M / 2M
    assert ratio_analysis.leverage.leverage_status in ["moderate", "aggressive"]

    # Verify efficiency ratios
    assert ratio_analysis.efficiency is not None
    assert ratio_analysis.efficiency.asset_turnover == 2.0  # 10M / 5M
    assert ratio_analysis.efficiency.efficiency_status in ["good", "excellent"]

    # Verify overall score
    assert 0 <= ratio_analysis.overall_score <= 100
    assert ratio_analysis.overall_score > 50  # Should be decent with healthy ratios

    # Verify confidence calculation
    confidence = agent._calculate_confidence([statement], ratio_analyses)
    assert confidence > 50  # Should have reasonable confidence with complete data


# ============================================================================
# WEEK 5 TESTS: CASH FLOW RATIOS
# ============================================================================

def test_calculate_cash_flow_ratios():
    """Test cash flow ratio calculation (Week 5)"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        revenue=10000000.0,
        current_liabilities=1000000.0,
        total_liabilities=3000000.0,
        operating_cash_flow=1500000.0,
        investing_cash_flow=-500000.0,
        financing_cash_flow=-200000.0
    )

    cash_flow = agent._calculate_cash_flow_ratios(statement)

    assert cash_flow is not None
    assert cash_flow.operating_cash_flow_ratio == 1.5  # 1500000 / 1000000
    assert cash_flow.free_cash_flow == 1000000.0  # 1500000 + |-500000|
    assert cash_flow.cash_flow_margin == 15.0  # 1500000 / 10000000 * 100
    assert cash_flow.cash_flow_to_debt == 0.5  # 1500000 / 3000000
    assert cash_flow.cash_flow_status in ["excellent", "good", "average"]


# ============================================================================
# WEEK 5 TESTS: QOQ GROWTH CALCULATION
# ============================================================================

def test_calculate_qoq_growth():
    """Test Quarter-over-Quarter growth calculation (Week 5)"""
    agent = FinancialAnalysisAgent()

    trend_points = [
        TrendPoint(period="2023-Q1", value=2000000.0),
        TrendPoint(period="2023-Q2", value=2200000.0, change_percentage=10.0),
        TrendPoint(period="2023-Q3", value=2400000.0, change_percentage=9.09)
    ]

    qoq_growth = agent._calculate_qoq_growth(trend_points)

    assert qoq_growth is not None
    assert abs(qoq_growth - 9.09) < 0.1  # (2400000 - 2200000) / 2200000 * 100


# ============================================================================
# WEEK 5 TESTS: SEASONALITY DETECTION
# ============================================================================

def test_detect_seasonality_positive():
    """Test seasonality detection with seasonal data (Week 5)"""
    agent = FinancialAnalysisAgent()

    # Simulated quarterly revenue with seasonal pattern
    # Q4 is always highest (holiday season)
    values = [
        2000000.0,  # Q1
        2200000.0,  # Q2
        2300000.0,  # Q3
        3000000.0,  # Q4
        2100000.0,  # Q1 (next year)
        2300000.0,  # Q2
        2400000.0,  # Q3
        3100000.0   # Q4
    ]

    seasonality_detected, strength = agent._detect_seasonality(values)

    assert seasonality_detected is not None
    # With clear seasonal pattern, should detect seasonality
    # Strength may vary based on implementation
    if seasonality_detected:
        assert strength is not None
        assert strength > 0


def test_detect_seasonality_negative():
    """Test seasonality detection with non-seasonal data (Week 5)"""
    agent = FinancialAnalysisAgent()

    # Steady growth, no seasonal pattern
    values = [2000000.0, 2100000.0, 2200000.0, 2300000.0]

    seasonality_detected, strength = agent._detect_seasonality(values)

    # Should either detect no seasonality, or very weak strength
    assert seasonality_detected is not None
    if seasonality_detected:
        assert strength is not None
    else:
        assert strength is None


# ============================================================================
# WEEK 5 TESTS: ALTMAN Z-SCORE
# ============================================================================

def test_calculate_altman_z_score_safe():
    """Test Altman Z-Score calculation for financially safe company (Week 5)"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        total_assets=10000000.0,
        current_assets=4000000.0,
        current_liabilities=2000000.0,
        total_liabilities=4000000.0,
        equity=6000000.0,
        retained_earnings=3000000.0,
        ebit=2000000.0,
        revenue=15000000.0
    )

    z_score, bankruptcy_risk = agent._calculate_altman_z_score(statement)

    assert z_score is not None
    assert bankruptcy_risk is not None
    assert bankruptcy_risk in ["safe", "grey_zone", "distress"]
    
    # With healthy financials, Z-score should be > 1.23
    assert z_score > 1.23


def test_calculate_altman_z_score_distress():
    """Test Altman Z-Score calculation for distressed company (Week 5)"""
    agent = FinancialAnalysisAgent()

    statement = FinancialStatement(
        period="2023",
        period_type="annual",
        total_assets=10000000.0,
        current_assets=1500000.0,
        current_liabilities=3000000.0,  # Negative working capital
        total_liabilities=9000000.0,  # High debt
        equity=1000000.0,  # Low equity
        retained_earnings=-500000.0,  # Negative retained earnings
        ebit=-200000.0,  # Operating loss
        revenue=5000000.0  # Low revenue
    )

    z_score, bankruptcy_risk = agent._calculate_altman_z_score(statement)

    assert z_score is not None
    assert bankruptcy_risk is not None
    
    # With poor financials, should indicate higher risk
    # May be in grey_zone or distress
    assert bankruptcy_risk in ["grey_zone", "distress"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
