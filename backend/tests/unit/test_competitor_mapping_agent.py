"""
Unit tests for CompetitorMappingAgent

Week 10 Tests (15 tests):
- test_competitor_mapping_agent_init
- test_competitor_profile_model
- test_market_position_analysis_model
- test_swot_item_model
- test_swot_analysis_model_totals
- test_competitive_insight_model
- test_competitor_mapping_output_model
- test_get_target_company_data_valid
- test_get_target_company_data_invalid
- test_discover_competitors
- test_analyze_market_position_leader
- test_analyze_market_position_niche
- test_generate_swot_analysis
- test_calculate_confidence_score
- test_execute_full_workflow

Coverage target: Core functionality from Week 10 implementation
"""

import pytest
from datetime import datetime
from app.agents.competitor_mapping_agent import (
    CompetitorMappingAgent,
    CompetitorMappingOutput,
    CompetitorProfile,
    MarketPositionAnalysis,
    SWOTAnalysis,
    SWOTItem,
    CompetitiveInsight,
    CompetitorType,
    MarketPosition,
    SWOTCategory,
    # Week 11 models
    PorterForce,
    PorterAnalysis,
    CompetitiveAdvantage
)


# ============================================================================
# WEEK 10 TESTS: Agent Initialization & Core Functionality
# ============================================================================

def test_competitor_mapping_agent_init():
    """
    Test CompetitorMappingAgent initialization.

    Validates:
    - Agent initializes without errors
    - Agent type is set correctly
    - Tool registry is available
    - Domain knowledge is loaded
    """
    agent = CompetitorMappingAgent()

    assert agent is not None
    assert agent.agent_type == "competitor_mapping"
    assert agent.tool_registry is not None
    assert agent.domain_knowledge is not None
    assert len(agent.domain_knowledge.PKD_INDUSTRIES) > 0
    assert len(agent.domain_knowledge.VOIVODESHIPS) == 16  # 16 Polish voivodeships


def test_competitor_profile_model():
    """
    Test CompetitorProfile Pydantic model.

    Validates:
    - Model can be created with required fields
    - Enums work correctly
    - Field validations apply
    - Default values are set
    """
    competitor = CompetitorProfile(
        company_name="Test Competitor Sp. z o.o.",
        krs_number="0000123456",
        competitor_type=CompetitorType.DIRECT,
        estimated_market_share=25.5,
        similarity_score=85.0
    )

    assert competitor.company_name == "Test Competitor Sp. z o.o."
    assert competitor.krs_number == "0000123456"
    assert competitor.competitor_type == "direct"  # Enum value
    assert competitor.estimated_market_share == 25.5
    assert competitor.similarity_score == 85.0
    assert isinstance(competitor.key_products, list)
    assert len(competitor.key_products) == 0  # Default empty list


def test_market_position_analysis_model():
    """
    Test MarketPositionAnalysis Pydantic model.

    Validates:
    - Model creation with position enum
    - Market metrics fields
    - Strategic positioning fields
    """
    market_analysis = MarketPositionAnalysis(
        position=MarketPosition.CHALLENGER,
        market_share_percentage=22.5,
        rank_in_industry=2,
        total_competitors_identified=5,
        market_growth_rate=7.3,
        market_size_pln=50000000.0,
        concentration_ratio=65.0,
        positioning_strategy="differentiation"
    )

    assert market_analysis.position == "challenger"
    assert market_analysis.market_share_percentage == 22.5
    assert market_analysis.rank_in_industry == 2
    assert market_analysis.total_competitors_identified == 5
    assert market_analysis.market_growth_rate == 7.3
    assert market_analysis.positioning_strategy == "differentiation"


def test_swot_item_model():
    """
    Test SWOTItem Pydantic model.

    Validates:
    - SWOT item creation
    - Category enum
    - Impact level validation
    """
    swot_item = SWOTItem(
        category=SWOTCategory.STRENGTH,
        description="Strong market presence",
        impact_level="high",
        evidence="Market share: 25%"
    )

    assert swot_item.category == "strength"
    assert swot_item.description == "Strong market presence"
    assert swot_item.impact_level == "high"
    assert swot_item.evidence == "Market share: 25%"


def test_swot_analysis_model_totals():
    """
    Test SWOTAnalysis Pydantic model with automatic total calculation.

    Validates:
    - Total counts are calculated automatically
    - Validator works correctly
    """
    strengths = [
        SWOTItem(category=SWOTCategory.STRENGTH, description="Strong brand", impact_level="high"),
        SWOTItem(category=SWOTCategory.STRENGTH, description="Experienced team", impact_level="medium")
    ]
    weaknesses = [
        SWOTItem(category=SWOTCategory.WEAKNESS, description="Limited resources", impact_level="medium")
    ]
    opportunities = [
        SWOTItem(category=SWOTCategory.OPPORTUNITY, description="Market growth", impact_level="high"),
        SWOTItem(category=SWOTCategory.OPPORTUNITY, description="New segments", impact_level="medium"),
        SWOTItem(category=SWOTCategory.OPPORTUNITY, description="Technology trends", impact_level="low")
    ]
    threats = [
        SWOTItem(category=SWOTCategory.THREAT, description="Competition", impact_level="high")
    ]

    swot = SWOTAnalysis(
        strengths=strengths,
        weaknesses=weaknesses,
        opportunities=opportunities,
        threats=threats,
        overall_strategic_position="strong"
    )

    assert swot.total_strengths == 2
    assert swot.total_weaknesses == 1
    assert swot.total_opportunities == 3
    assert swot.total_threats == 1
    assert swot.overall_strategic_position == "strong"


def test_competitive_insight_model():
    """
    Test CompetitiveInsight Pydantic model.

    Validates:
    - Insight creation with all fields
    - Priority validation
    - Recommended actions list
    """
    insight = CompetitiveInsight(
        insight_type="opportunity",
        title="Market Expansion Opportunity",
        description="Growing demand in eastern regions",
        priority="high",
        recommended_actions=[
            "Conduct market research",
            "Develop regional strategy"
        ]
    )

    assert insight.insight_type == "opportunity"
    assert insight.title == "Market Expansion Opportunity"
    assert insight.priority == "high"
    assert len(insight.recommended_actions) == 2


def test_competitor_mapping_output_model():
    """
    Test CompetitorMappingOutput Pydantic model.

    Validates:
    - Complete output model structure
    - Automatic total competitors calculation
    - All required and optional fields
    """
    competitors = [
        CompetitorProfile(
            company_name="Competitor A",
            competitor_type=CompetitorType.DIRECT,
            similarity_score=85.0
        ),
        CompetitorProfile(
            company_name="Competitor B",
            competitor_type=CompetitorType.INDIRECT,
            similarity_score=70.0
        )
    ]

    output = CompetitorMappingOutput(
        target="KRS 0000123456",
        target_company_name="Test Company",
        competitors=competitors,
        confidence_score=82.5,
        data_sources=["KRS API", "Market Analysis"]
    )

    assert output.agent_type == "competitor_mapping"
    assert output.target == "KRS 0000123456"
    assert output.total_competitors_found == 2  # Automatically calculated
    assert len(output.competitors) == 2
    assert output.confidence_score == 82.5
    assert len(output.data_sources) == 2


# ============================================================================
# AGENT METHOD TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_get_target_company_data_valid():
    """
    Test _get_target_company_data with valid target.

    Validates:
    - Valid target returns company data
    - All required fields are present
    - Data structure is correct
    """
    agent = CompetitorMappingAgent()

    # Test with KRS number
    result = await agent._get_target_company_data("KRS 0000123456")

    assert result['valid'] is True
    assert 'company_name' in result
    assert 'krs' in result
    assert 'pkd_codes' in result
    assert isinstance(result['pkd_codes'], list)
    assert len(result['pkd_codes']) > 0


@pytest.mark.asyncio
async def test_get_target_company_data_invalid():
    """
    Test _get_target_company_data with invalid target.

    Validates:
    - Invalid target returns valid=False
    - Empty or malformed targets are rejected
    """
    agent = CompetitorMappingAgent()

    # Test with invalid short string
    result = await agent._get_target_company_data("ABC")

    assert result['valid'] is False


@pytest.mark.asyncio
async def test_discover_competitors():
    """
    Test _discover_competitors method.

    Validates:
    - Competitors are discovered
    - CompetitorProfile objects are returned
    - Similarity scores are calculated
    - Max competitors limit is respected
    """
    agent = CompetitorMappingAgent()

    target_data = {
        'valid': True,
        'company_name': "Test Company",
        'pkd_codes': ["62.01.Z"],
        'voivodeship': "Mazowieckie",
        'revenue': 5000000.0,
        'employees': 50
    }

    competitors = await agent._discover_competitors(
        target_data=target_data,
        max_competitors=5,
        geographic_scope="national"
    )

    assert isinstance(competitors, list)
    assert len(competitors) <= 5  # Respects max limit

    if len(competitors) > 0:
        competitor = competitors[0]
        assert isinstance(competitor, CompetitorProfile)
        assert hasattr(competitor, 'company_name')
        assert hasattr(competitor, 'similarity_score')
        assert 0 <= competitor.similarity_score <= 100


@pytest.mark.asyncio
async def test_analyze_market_position_leader():
    """
    Test _analyze_market_position with leader scenario.

    Validates:
    - Market share calculation
    - Position classification (LEADER for >30% share)
    - Rank calculation
    - Concentration ratio
    """
    agent = CompetitorMappingAgent()

    # Create scenario where target is market leader
    target_data = {
        'revenue': 40000000.0  # 40M PLN
    }

    competitors = [
        CompetitorProfile(
            company_name="Competitor 1",
            estimated_revenue=20000000.0,  # 20M
            similarity_score=80.0,
            competitor_type=CompetitorType.DIRECT
        ),
        CompetitorProfile(
            company_name="Competitor 2",
            estimated_revenue=15000000.0,  # 15M
            similarity_score=75.0,
            competitor_type=CompetitorType.DIRECT
        )
    ]

    market_position = await agent._analyze_market_position(
        target_data=target_data,
        competitors=competitors
    )

    # Total market: 40M + 20M + 15M = 75M
    # Target share: 40/75 = 53.3% (LEADER)
    assert isinstance(market_position, MarketPositionAnalysis)
    assert market_position.position == MarketPosition.LEADER
    assert market_position.market_share_percentage > 30.0
    assert market_position.rank_in_industry == 1
    assert market_position.total_competitors_identified == 2


@pytest.mark.asyncio
async def test_analyze_market_position_niche():
    """
    Test _analyze_market_position with niche player scenario.

    Validates:
    - Niche position classification (<5% share)
    - Lower rank calculation
    """
    agent = CompetitorMappingAgent()

    # Create scenario where target is niche player
    target_data = {
        'revenue': 2000000.0  # 2M PLN
    }

    competitors = [
        CompetitorProfile(
            company_name="Competitor 1",
            estimated_revenue=50000000.0,  # 50M
            similarity_score=70.0,
            competitor_type=CompetitorType.DIRECT
        ),
        CompetitorProfile(
            company_name="Competitor 2",
            estimated_revenue=30000000.0,  # 30M
            similarity_score=65.0,
            competitor_type=CompetitorType.DIRECT
        )
    ]

    market_position = await agent._analyze_market_position(
        target_data=target_data,
        competitors=competitors
    )

    # Total market: 2M + 50M + 30M = 82M
    # Target share: 2/82 = 2.4% (NICHE)
    assert isinstance(market_position, MarketPositionAnalysis)
    assert market_position.position == MarketPosition.NICHE
    assert market_position.market_share_percentage < 5.0
    assert market_position.rank_in_industry == 3  # Third place


@pytest.mark.asyncio
async def test_generate_swot_analysis():
    """
    Test _generate_swot_analysis method.

    Validates:
    - SWOT analysis is generated
    - All four categories are present
    - Overall strategic position is determined
    """
    agent = CompetitorMappingAgent()

    target_data = {
        'company_name': "Test Company",
        'voivodeship': "Mazowieckie",
        'employees': 50
    }

    competitors = [
        CompetitorProfile(
            company_name="Competitor 1",
            similarity_score=85.0,
            competitor_type=CompetitorType.DIRECT
        )
    ]

    market_position = MarketPositionAnalysis(
        position=MarketPosition.CHALLENGER,
        market_share_percentage=20.0,
        rank_in_industry=2,
        total_competitors_identified=1,
        market_growth_rate=5.2,
        concentration_ratio=55.0
    )

    swot = await agent._generate_swot_analysis(
        target_data=target_data,
        competitors=competitors,
        market_position=market_position
    )

    assert isinstance(swot, SWOTAnalysis)
    assert swot.total_strengths > 0
    assert swot.total_weaknesses >= 0
    assert swot.total_opportunities > 0
    assert swot.total_threats > 0
    assert swot.overall_strategic_position in ["strong", "moderate", "weak"]


def test_calculate_confidence_score():
    """
    Test _calculate_confidence_score method.

    Validates:
    - Confidence score calculation
    - Score is between 0-100
    - Higher scores for complete data
    """
    agent = CompetitorMappingAgent()

    # Scenario 1: Complete data (high score)
    target_data_complete = {
        'valid': True,
        'pkd_codes': ["62.01.Z"]
    }
    competitors_complete = [
        CompetitorProfile(company_name=f"Comp {i}", similarity_score=80.0, competitor_type=CompetitorType.DIRECT)
        for i in range(5)
    ]
    market_position = MarketPositionAnalysis(
        position=MarketPosition.CHALLENGER,
        market_share_percentage=20.0,
        rank_in_industry=2,
        total_competitors_identified=5
    )
    swot = SWOTAnalysis(overall_strategic_position="strong")

    score_complete = agent._calculate_confidence_score(
        target_data=target_data_complete,
        competitors=competitors_complete,
        market_position=market_position,
        swot_analysis=swot
    )

    assert 0 <= score_complete <= 100
    assert score_complete >= 90  # Should be high with complete data

    # Scenario 2: Minimal data (lower score)
    target_data_minimal = {'valid': False}
    competitors_minimal = []

    score_minimal = agent._calculate_confidence_score(
        target_data=target_data_minimal,
        competitors=competitors_minimal,
        market_position=None,
        swot_analysis=None
    )

    assert 0 <= score_minimal <= 100
    assert score_minimal < score_complete  # Should be lower


@pytest.mark.asyncio
async def test_execute_full_workflow():
    """
    Test complete execute() workflow.

    Validates:
    - Full agent execution from start to finish
    - All major components work together
    - Output structure is complete
    - Confidence score is reasonable
    """
    agent = CompetitorMappingAgent()

    # Execute with valid target
    result = await agent.execute(
        target="KRS 0000123456",
        context={
            'max_competitors': 5,
            'include_swot': True,
            'geographic_scope': 'national'
        }
    )

    # Validate output structure
    assert isinstance(result, CompetitorMappingOutput)
    assert result.agent_type == "competitor_mapping"
    assert result.target == "KRS 0000123456"
    assert result.target_company_name is not None

    # Validate data completeness
    assert len(result.data_sources) > 0
    assert 0 <= result.confidence_score <= 100

    # Validate competitors
    assert result.total_competitors_found >= 0
    assert len(result.competitors) == result.total_competitors_found

    # Validate market position
    assert result.market_position is not None
    assert isinstance(result.market_position, MarketPositionAnalysis)

    # Validate SWOT (if included)
    assert result.swot_analysis is not None
    assert isinstance(result.swot_analysis, SWOTAnalysis)

    # Validate insights and recommendations
    assert isinstance(result.competitive_insights, list)
    assert isinstance(result.strategic_recommendations, list)
    assert isinstance(result.market_gaps_identified, list)

    # Validate metadata
    assert isinstance(result.last_updated, datetime)
    assert result.confidence_score > 0  # Should have some confidence


# ============================================================================
# WEEK 11 TESTS: Advanced Analysis Features
# ============================================================================

def test_porter_force_model():
    """
    Test PorterForce Pydantic model.

    Week 11: Porter's Five Forces component validation.
    """
    force = PorterForce(
        force_name="competitive_rivalry",
        strength="high",
        description="Intense competition among existing players",
        key_factors=["Many competitors", "Low switching costs", "High exit barriers"],
        impact_on_profitability="negative"
    )

    assert force.force_name == "competitive_rivalry"
    assert force.strength == "high"
    assert len(force.key_factors) == 3
    assert force.impact_on_profitability == "negative"


def test_porter_analysis_model():
    """
    Test PorterAnalysis Pydantic model.

    Week 11: Complete Porter's Five Forces analysis structure.
    """
    threat_new_entrants = PorterForce(
        force_name="threat_of_new_entrants",
        strength="medium",
        description="Moderate barriers exist",
        key_factors=["Capital requirements"],
        impact_on_profitability="negative"
    )

    supplier_power = PorterForce(
        force_name="supplier_power",
        strength="low",
        description="Many suppliers",
        key_factors=["Low concentration"],
        impact_on_profitability="positive"
    )

    buyer_power = PorterForce(
        force_name="buyer_power",
        strength="medium",
        description="Moderate power",
        key_factors=["Price sensitivity"],
        impact_on_profitability="negative"
    )

    threat_substitutes = PorterForce(
        force_name="threat_substitutes",
        strength="low",
        description="Few substitutes",
        key_factors=["Limited alternatives"],
        impact_on_profitability="positive"
    )

    rivalry = PorterForce(
        force_name="competitive_rivalry",
        strength="high",
        description="Intense competition",
        key_factors=["Many competitors"],
        impact_on_profitability="negative"
    )

    porter = PorterAnalysis(
        threat_of_new_entrants=threat_new_entrants,
        bargaining_power_of_suppliers=supplier_power,
        bargaining_power_of_buyers=buyer_power,
        threat_of_substitutes=threat_substitutes,
        competitive_rivalry=rivalry,
        industry_attractiveness="medium",
        overall_profitability_outlook="Moderate profitability expected",
        strategic_recommendations=["Focus on differentiation", "Build customer loyalty"]
    )

    assert porter.industry_attractiveness == "medium"
    assert len(porter.strategic_recommendations) == 2


def test_competitive_advantage_model():
    """
    Test CompetitiveAdvantage Pydantic model.

    Week 11: Competitive advantage framework validation.
    """
    advantage = CompetitiveAdvantage(
        advantage_type="differentiation",
        strength="strong",
        description="Unique value proposition and brand",
        sustainability="high",
        supporting_evidence=[
            "Strong brand recognition",
            "Proprietary technology",
            "High customer satisfaction"
        ]
    )

    assert advantage.advantage_type == "differentiation"
    assert advantage.strength == "strong"
    assert advantage.sustainability == "high"
    assert len(advantage.supporting_evidence) == 3


@pytest.mark.asyncio
async def test_generate_porter_analysis():
    """
    Test _generate_porter_analysis method.

    Week 11: Porter's Five Forces generation.
    """
    agent = CompetitorMappingAgent()

    target_data = {
        'company_name': "Test Company",
        'industry': "IT Services"
    }

    competitors = [
        CompetitorProfile(
            company_name=f"Competitor {i}",
            similarity_score=80.0,
            competitor_type=CompetitorType.DIRECT
        )
        for i in range(3)
    ]

    market_position = MarketPositionAnalysis(
        position=MarketPosition.CHALLENGER,
        market_share_percentage=20.0,
        rank_in_industry=2,
        total_competitors_identified=3,
        concentration_ratio=55.0
    )

    porter = await agent._generate_porter_analysis(
        target_data=target_data,
        competitors=competitors,
        market_position=market_position
    )

    assert porter is not None
    assert isinstance(porter, PorterAnalysis)
    assert porter.industry_attractiveness in ["high", "medium", "low"]
    assert len(porter.strategic_recommendations) > 0


def test_identify_competitive_advantages():
    """
    Test _identify_competitive_advantages method.

    Week 11: Competitive advantage identification.
    """
    agent = CompetitorMappingAgent()

    target_data = {
        'company_name': "Test Company"
    }

    # Niche position scenario
    market_position = MarketPositionAnalysis(
        position=MarketPosition.NICHE,
        market_share_percentage=3.0,
        rank_in_industry=5,
        total_competitors_identified=10
    )

    swot = SWOTAnalysis(
        strengths=[
            SWOTItem(category=SWOTCategory.STRENGTH, description="Strong brand", impact_level="high"),
            SWOTItem(category=SWOTCategory.STRENGTH, description="Expertise", impact_level="high"),
            SWOTItem(category=SWOTCategory.STRENGTH, description="Team", impact_level="medium")
        ],
        overall_strategic_position="strong"
    )

    advantages = agent._identify_competitive_advantages(
        target_data=target_data,
        market_position=market_position,
        swot_analysis=swot
    )

    assert isinstance(advantages, list)
    assert len(advantages) > 0

    # Niche position should have focus advantage
    focus_advantages = [a for a in advantages if a.advantage_type == "focus"]
    assert len(focus_advantages) > 0
    assert focus_advantages[0].strength == "strong"
