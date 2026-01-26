"""
Competitor Mapping Agent

Autonomous agent for competitive intelligence and market positioning analysis.
Discovers competitors, analyzes market positioning, and generates strategic insights.

Week 10 Implementation: Foundation agent for competitive analysis.

Use case: "Find competitors for company with KRS 0000123456"
         "Analyze market position of company with NIP 1234567890"
         "Generate SWOT analysis for company XYZ"
"""

import logging
import re
import json
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator

from app.services.agent_tools import ToolRegistry, get_tool_registry
from app.services.claude_service import get_claude_service, is_claude_available, SystemPromptType, ClaudeModel

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class CompetitorType(str, Enum):
    """Types of competitors"""
    DIRECT = "direct"  # Same products/services, same market
    INDIRECT = "indirect"  # Similar products, different approach
    POTENTIAL = "potential"  # Could enter market
    SUBSTITUTE = "substitute"  # Alternative solutions


class MarketPosition(str, Enum):
    """Market positioning classification"""
    LEADER = "leader"  # Market share >30%
    CHALLENGER = "challenger"  # Market share 15-30%
    FOLLOWER = "follower"  # Market share 5-15%
    NICHE = "niche"  # Market share <5%, specialized


class SWOTCategory(str, Enum):
    """SWOT analysis categories"""
    STRENGTH = "strength"
    WEAKNESS = "weakness"
    OPPORTUNITY = "opportunity"
    THREAT = "threat"


# ============================================================================
# OUTPUT SCHEMA
# ============================================================================

class CompetitorProfile(BaseModel):
    """Individual competitor profile"""
    company_name: str
    krs_number: Optional[str] = None
    nip_number: Optional[str] = None
    competitor_type: CompetitorType = CompetitorType.DIRECT

    # Market metrics
    estimated_market_share: Optional[float] = Field(None, ge=0, le=100)
    estimated_revenue: Optional[float] = None  # PLN
    employee_count: Optional[int] = Field(None, ge=0)

    # Competitive factors
    key_products: List[str] = Field(default_factory=list)
    key_markets: List[str] = Field(default_factory=list)
    geographic_coverage: List[str] = Field(default_factory=list)  # Voivodeships/countries

    # Analysis
    competitive_advantages: List[str] = Field(default_factory=list)
    competitive_disadvantages: List[str] = Field(default_factory=list)
    similarity_score: float = Field(..., ge=0, le=100, description="Similarity to target company")

    class Config:
        use_enum_values = True


class MarketPositionAnalysis(BaseModel):
    """Market positioning analysis"""
    position: MarketPosition
    market_share_percentage: Optional[float] = Field(None, ge=0, le=100)
    rank_in_industry: Optional[int] = Field(None, ge=1)
    total_competitors_identified: int = Field(..., ge=0)

    # Market dynamics
    market_growth_rate: Optional[float] = None  # Annual % growth
    market_size_pln: Optional[float] = None  # Total market size in PLN
    concentration_ratio: Optional[float] = Field(None, ge=0, le=100)  # CR4 or CR5

    # Strategic positioning
    differentiation_factors: List[str] = Field(default_factory=list)
    target_segments: List[str] = Field(default_factory=list)
    positioning_strategy: Optional[str] = None  # cost_leadership, differentiation, focus

    class Config:
        use_enum_values = True


class SWOTItem(BaseModel):
    """Individual SWOT analysis item"""
    category: SWOTCategory
    description: str
    impact_level: str = Field(..., pattern="^(high|medium|low)$")
    evidence: Optional[str] = None  # Supporting data/source

    class Config:
        use_enum_values = True


class SWOTAnalysis(BaseModel):
    """Complete SWOT analysis"""
    strengths: List[SWOTItem] = Field(default_factory=list)
    weaknesses: List[SWOTItem] = Field(default_factory=list)
    opportunities: List[SWOTItem] = Field(default_factory=list)
    threats: List[SWOTItem] = Field(default_factory=list)

    # Summary metrics
    total_strengths: int = 0
    total_weaknesses: int = 0
    total_opportunities: int = 0
    total_threats: int = 0
    overall_strategic_position: Optional[str] = None  # strong, moderate, weak

    @model_validator(mode='after')
    def calculate_totals(self):
        """Calculate total counts automatically"""
        self.total_strengths = len(self.strengths)
        self.total_weaknesses = len(self.weaknesses)
        self.total_opportunities = len(self.opportunities)
        self.total_threats = len(self.threats)
        return self


class PorterForce(BaseModel):
    """Individual Porter's Five Forces element"""
    force_name: str  # threat_of_new_entrants, supplier_power, buyer_power, threat_of_substitutes, competitive_rivalry
    strength: str = Field(..., pattern="^(high|medium|low)$")
    description: str
    key_factors: List[str] = Field(default_factory=list)
    impact_on_profitability: str  # positive, negative, neutral


class PorterAnalysis(BaseModel):
    """Complete Porter's Five Forces analysis"""
    threat_of_new_entrants: PorterForce
    bargaining_power_of_suppliers: PorterForce
    bargaining_power_of_buyers: PorterForce
    threat_of_substitutes: PorterForce
    competitive_rivalry: PorterForce

    # Overall assessment
    industry_attractiveness: str = Field(..., pattern="^(high|medium|low)$")
    overall_profitability_outlook: str  # Description of industry profitability
    strategic_recommendations: List[str] = Field(default_factory=list)


class CompetitiveAdvantage(BaseModel):
    """Competitive advantage analysis"""
    advantage_type: str  # cost_leadership, differentiation, focus, innovation
    strength: str = Field(..., pattern="^(strong|moderate|weak)$")
    description: str
    sustainability: str = Field(..., pattern="^(high|medium|low)$")  # How sustainable is this advantage
    supporting_evidence: List[str] = Field(default_factory=list)


class CompetitiveInsight(BaseModel):
    """Strategic competitive insight"""
    insight_type: str  # market_gap, threat, opportunity, trend
    title: str
    description: str
    priority: str = Field(..., pattern="^(critical|high|medium|low)$")
    recommended_actions: List[str] = Field(default_factory=list)


class CompetitorMappingOutput(BaseModel):
    """Structured output for CompetitorMappingAgent"""
    agent_type: str = "competitor_mapping"
    target: str = Field(..., description="Target company identifier")

    # Target company context
    target_company_name: Optional[str] = None
    target_industry: Optional[str] = None
    target_pkd_codes: List[str] = Field(default_factory=list)

    # Competitor analysis
    competitors: List[CompetitorProfile] = Field(default_factory=list)
    total_competitors_found: int = 0

    # Market positioning
    market_position: Optional[MarketPositionAnalysis] = None

    # Strategic analysis
    swot_analysis: Optional[SWOTAnalysis] = None
    porter_analysis: Optional[PorterAnalysis] = None  # Week 11: Porter's Five Forces
    competitive_advantages: List[CompetitiveAdvantage] = Field(default_factory=list)  # Week 11
    competitive_insights: List[CompetitiveInsight] = Field(default_factory=list)

    # Recommendations
    strategic_recommendations: List[str] = Field(default_factory=list)
    market_gaps_identified: List[str] = Field(default_factory=list)

    # Agent metadata
    confidence_score: float = Field(..., ge=0, le=100)
    data_sources: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode='after')
    def calculate_total_competitors(self):
        """Calculate total competitors automatically"""
        self.total_competitors_found = len(self.competitors)
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "competitor_mapping",
                "target": "KRS 0000123456",
                "target_company_name": "Example Sp. z o.o.",
                "total_competitors_found": 5,
                "confidence_score": 82.0,
                "data_sources": ["KRS API", "GUS Statistical Data"],
                "last_updated": "2026-01-25T10:00:00Z"
            }
        }


# ============================================================================
# DOMAIN KNOWLEDGE
# ============================================================================

class CompetitorMappingDomainKnowledge:
    """
    Domain knowledge for competitive analysis.
    Based on market analysis best practices and Polish business environment.
    """

    # PKD codes - Polish Classification of Activities (expanded)
    PKD_INDUSTRIES = {
        "01": "Rolnictwo, leśnictwo, łowiectwo i rybactwo",
        "10": "Produkcja artykułów spożywczych",
        "46": "Handel hurtowy",
        "47": "Handel detaliczny",
        "62": "Działalność związana z oprogramowaniem i doradztwem",
        "63": "Działalność usługowa w zakresie informacji",
        "68": "Działalność związana z obsługą rynku nieruchomości",
        "70": "Działalność firm centralnych (head offices)",
        "71": "Działalność w zakresie architektury i inżynierii",
        "72": "Badania naukowe i prace rozwojowe",
        "73": "Reklama, badanie rynku i opinii publicznej",
        "82": "Działalność związana z administracyjną obsługą biura"
    }

    # Market position thresholds
    MARKET_SHARE_THRESHOLDS = {
        MarketPosition.LEADER: 30.0,  # >30%
        MarketPosition.CHALLENGER: 15.0,  # 15-30%
        MarketPosition.FOLLOWER: 5.0,  # 5-15%
        MarketPosition.NICHE: 0.0  # <5%
    }

    # Similarity scoring weights
    SIMILARITY_WEIGHTS = {
        'same_pkd_code': 40,
        'same_voivodeship': 15,
        'similar_revenue': 20,
        'similar_employee_count': 15,
        'similar_legal_form': 10
    }

    # Polish voivodeships
    VOIVODESHIPS = [
        "Mazowieckie", "Śląskie", "Wielkopolskie", "Małopolskie",
        "Dolnośląskie", "Łódzkie", "Pomorskie", "Kujawsko-Pomorskie",
        "Zachodniopomorskie", "Lubelskie", "Podkarpackie", "Warmińsko-Mazurskie",
        "Podlaskie", "Świętokrzyskie", "Lubuskie", "Opolskie"
    ]


# ============================================================================
# COMPETITOR MAPPING AGENT
# ============================================================================

class CompetitorMappingAgent:
    """
    Autonomous agent for competitive intelligence and market positioning.

    Capabilities:
    - Competitor identification (same PKD codes, similar companies)
    - Market share estimation
    - Market positioning analysis (leader/challenger/follower/niche)
    - SWOT analysis generation
    - Competitive advantage identification
    - Market gap detection
    - Strategic recommendations

    Competitor Discovery Algorithm:
        1. Extract target company's PKD codes
        2. Query KRS/GUS for companies with matching PKD codes
        3. Filter by geographic proximity (same voivodeship first)
        4. Calculate similarity scores
        5. Rank by similarity and market presence
        6. Classify by competitor type

    Confidence Scoring Algorithm:
        score = 0
        if target_company_data: score += 30
        if competitors_found > 0: score += 40
        if market_data_available: score += 20
        if swot_generated: score += 10
        # Max: 100
    """

    def __init__(self):
        """Initialize CompetitorMappingAgent with tool registry and Claude service."""
        self.agent_type = "competitor_mapping"
        self.tool_registry = get_tool_registry()
        self.domain_knowledge = CompetitorMappingDomainKnowledge()

        # Week 11: Claude AI integration for enhanced SWOT and Porter analysis
        self.claude_available = is_claude_available()
        if self.claude_available:
            try:
                self.claude_service = get_claude_service()
                logger.info(f"{self.agent_type} agent initialized with Claude AI integration")
            except Exception as e:
                logger.warning(f"Claude service not available: {str(e)}")
                self.claude_available = False
                self.claude_service = None
        else:
            self.claude_service = None
            logger.info(f"{self.agent_type} agent initialized without Claude AI (fallback mode)")


    async def execute(
        self,
        target: str,
        context: Optional[Dict[str, Any]] = None
    ) -> CompetitorMappingOutput:
        """
        Execute competitor mapping and market positioning analysis.

        Args:
            target: Company identifier (KRS number, NIP, or company name)
                   Examples: "KRS 0000123456", "NIP 1234567890", "Company Name Sp. z o.o."
            context: Optional context with additional parameters:
                    - max_competitors: Maximum number of competitors to return (default: 10)
                    - include_swot: Whether to generate SWOT analysis (default: True)
                    - geographic_scope: "local", "regional", "national" (default: "national")

        Returns:
            CompetitorMappingOutput: Structured competitive analysis with SWOT and insights

        Example:
            agent = CompetitorMappingAgent()
            result = await agent.execute(target="KRS 0000123456")
        """
        start_time = datetime.utcnow()
        logger.info(f"CompetitorMappingAgent: Executing for target: '{target}'")

        errors = []
        warnings = []
        data_sources = []

        # Parse context parameters
        max_competitors = context.get('max_competitors', 10) if context else 10
        include_swot = context.get('include_swot', True) if context else True
        geographic_scope = context.get('geographic_scope', 'national') if context else 'national'

        try:
            # Step 1: Get target company data
            target_data = await self._get_target_company_data(target)

            if not target_data.get('valid'):
                errors.append(f"Could not identify target company: {target}")
                return self._build_output(
                    target=target,
                    data={},
                    confidence_score=0,
                    data_sources=data_sources,
                    errors=errors,
                    warnings=warnings
                )

            logger.info(f"CompetitorMappingAgent: Target company: {target_data.get('company_name')}")
            data_sources.append("Target Company Analysis")

            # Step 2: Discover competitors
            competitors = await self._discover_competitors(
                target_data=target_data,
                max_competitors=max_competitors,
                geographic_scope=geographic_scope
            )

            if len(competitors) > 0:
                data_sources.append("Competitor Discovery")
                logger.info(f"CompetitorMappingAgent: Found {len(competitors)} competitors")
            else:
                warnings.append("No competitors found with current criteria")

            # Step 3: Analyze market position
            market_position = await self._analyze_market_position(
                target_data=target_data,
                competitors=competitors
            )
            data_sources.append("Market Position Analysis")

            # Step 4: Generate SWOT analysis (if requested)
            swot_analysis = None
            if include_swot:
                swot_analysis = await self._generate_swot_analysis(
                    target_data=target_data,
                    competitors=competitors,
                    market_position=market_position
                )
                data_sources.append("SWOT Analysis")

            # Week 11 Step 4a: Generate Porter's Five Forces analysis
            porter_analysis = None
            include_porter = context.get('include_porter', True) if context else True
            if include_porter:
                porter_analysis = await self._generate_porter_analysis(
                    target_data=target_data,
                    competitors=competitors,
                    market_position=market_position
                )
                if porter_analysis:
                    data_sources.append("Porter's Five Forces Analysis")

            # Week 11 Step 4b: Identify competitive advantages
            competitive_advantages = self._identify_competitive_advantages(
                target_data=target_data,
                market_position=market_position,
                swot_analysis=swot_analysis
            )
            if competitive_advantages:
                data_sources.append("Competitive Advantage Analysis")

            # Step 5: Generate competitive insights
            insights = await self._generate_competitive_insights(
                target_data=target_data,
                competitors=competitors,
                market_position=market_position,
                swot_analysis=swot_analysis
            )

            # Step 6: Identify market gaps
            market_gaps = self._identify_market_gaps(
                competitors=competitors,
                target_data=target_data
            )

            # Step 7: Generate strategic recommendations
            recommendations = self._generate_strategic_recommendations(
                market_position=market_position,
                swot_analysis=swot_analysis,
                insights=insights,
                market_gaps=market_gaps
            )

            # Step 8: Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                target_data=target_data,
                competitors=competitors,
                market_position=market_position,
                swot_analysis=swot_analysis
            )

            # Build final output
            output_data = {
                'target_company_name': target_data.get('company_name'),
                'target_industry': target_data.get('industry'),
                'target_pkd_codes': target_data.get('pkd_codes', []),
                'competitors': competitors,
                'market_position': market_position,
                'swot_analysis': swot_analysis,
                'porter_analysis': porter_analysis,  # Week 11
                'competitive_advantages': competitive_advantages,  # Week 11
                'competitive_insights': insights,
                'strategic_recommendations': recommendations,
                'market_gaps_identified': market_gaps
            }

            result = self._build_output(
                target=target,
                data=output_data,
                confidence_score=confidence_score,
                data_sources=data_sources,
                errors=errors,
                warnings=warnings
            )

            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"CompetitorMappingAgent: Completed in {execution_time:.2f}s")

            return result

        except Exception as e:
            logger.error(f"CompetitorMappingAgent: Unexpected error: {str(e)}", exc_info=True)
            errors.append(f"Execution failed: {str(e)}")

            return self._build_output(
                target=target,
                data={},
                confidence_score=0,
                data_sources=data_sources,
                errors=errors,
                warnings=warnings
            )


    # ========================================================================
    # PRIVATE METHODS
    # ========================================================================

    async def _get_target_company_data(self, target: str) -> Dict[str, Any]:
        """
        Get target company data for competitor analysis.

        Returns:
            Dict with: valid, company_name, krs, nip, pkd_codes, industry,
                      voivodeship, revenue, employees, legal_form
        """
        # Placeholder implementation - would integrate with CompanyProfileAgent
        # or directly with KRS/GUS APIs

        # Mock data for Week 10 foundation
        if "KRS" in target.upper() or "NIP" in target.upper() or len(target) > 5:
            return {
                'valid': True,
                'company_name': "Target Company Sp. z o.o.",
                'krs': "0000123456",
                'nip': "1234567890",
                'pkd_codes': ["62.01.Z", "62.02.Z"],  # Software development
                'industry': "Działalność związana z oprogramowaniem",
                'voivodeship': "Mazowieckie",
                'revenue': 5000000.0,  # 5M PLN
                'employees': 50,
                'legal_form': "Spółka z ograniczoną odpowiedzialnością"
            }

        return {'valid': False}


    async def _discover_competitors(
        self,
        target_data: Dict[str, Any],
        max_competitors: int,
        geographic_scope: str
    ) -> List[CompetitorProfile]:
        """
        Discover competitors based on PKD codes and other criteria.

        Algorithm:
            1. Find companies with matching PKD codes
            2. Calculate similarity scores
            3. Rank by similarity
            4. Return top N competitors
        """
        logger.info(f"Discovering competitors (max: {max_competitors}, scope: {geographic_scope})")

        # Placeholder implementation - would query KRS/GUS databases
        # Mock competitors for Week 10 foundation
        mock_competitors = [
            {
                'company_name': "Competitor Alpha Sp. z o.o.",
                'krs_number': "0000234567",
                'nip_number': "2345678901",
                'competitor_type': CompetitorType.DIRECT,
                'estimated_market_share': 25.0,
                'estimated_revenue': 12000000.0,
                'employee_count': 120,
                'key_products': ["Enterprise Software", "Cloud Solutions"],
                'key_markets': ["Finance", "Insurance"],
                'geographic_coverage': ["Mazowieckie", "Małopolskie"],
                'competitive_advantages': ["Strong brand", "Large client base"],
                'competitive_disadvantages': ["Higher prices", "Slow innovation"],
                'similarity_score': 85.0
            },
            {
                'company_name': "Competitor Beta S.A.",
                'krs_number': "0000345678",
                'nip_number': "3456789012",
                'competitor_type': CompetitorType.DIRECT,
                'estimated_market_share': 18.0,
                'estimated_revenue': 8000000.0,
                'employee_count': 80,
                'key_products': ["Mobile Apps", "Web Development"],
                'key_markets': ["E-commerce", "Retail"],
                'geographic_coverage': ["Mazowieckie", "Śląskie"],
                'competitive_advantages': ["Modern tech stack", "Agile processes"],
                'competitive_disadvantages': ["Limited experience", "Smaller team"],
                'similarity_score': 78.0
            },
            {
                'company_name': "Competitor Gamma Sp. z o.o.",
                'krs_number': "0000456789",
                'competitor_type': CompetitorType.INDIRECT,
                'estimated_market_share': 12.0,
                'estimated_revenue': 6000000.0,
                'employee_count': 60,
                'key_products': ["IT Consulting", "System Integration"],
                'key_markets': ["Healthcare", "Public Sector"],
                'geographic_coverage': ["Mazowieckie"],
                'competitive_advantages': ["Niche expertise", "Long contracts"],
                'competitive_disadvantages': ["Limited scalability", "Regional focus"],
                'similarity_score': 65.0
            }
        ]

        # Convert to CompetitorProfile objects
        competitors = []
        for comp_data in mock_competitors[:max_competitors]:
            competitor = CompetitorProfile(**comp_data)
            competitors.append(competitor)

        return competitors


    async def _analyze_market_position(
        self,
        target_data: Dict[str, Any],
        competitors: List[CompetitorProfile]
    ) -> MarketPositionAnalysis:
        """
        Analyze target company's market position.

        Calculates:
            - Market share percentage
            - Industry rank
            - Market concentration
            - Positioning strategy
        """
        logger.info("Analyzing market position")

        # Calculate total market (target + competitors)
        target_revenue = target_data.get('revenue', 0)
        competitor_revenues = [c.estimated_revenue or 0 for c in competitors]
        total_market = target_revenue + sum(competitor_revenues)

        # Calculate market share
        market_share = (target_revenue / total_market * 100) if total_market > 0 else 0

        # Determine position based on market share
        position = MarketPosition.NICHE
        if market_share >= self.domain_knowledge.MARKET_SHARE_THRESHOLDS[MarketPosition.LEADER]:
            position = MarketPosition.LEADER
        elif market_share >= self.domain_knowledge.MARKET_SHARE_THRESHOLDS[MarketPosition.CHALLENGER]:
            position = MarketPosition.CHALLENGER
        elif market_share >= self.domain_knowledge.MARKET_SHARE_THRESHOLDS[MarketPosition.FOLLOWER]:
            position = MarketPosition.FOLLOWER

        # Calculate rank (1-based)
        all_revenues = [target_revenue] + competitor_revenues
        all_revenues_sorted = sorted(all_revenues, reverse=True)
        rank = all_revenues_sorted.index(target_revenue) + 1

        # Calculate concentration ratio (CR3 - top 3 companies)
        top_3_revenues = sorted(all_revenues, reverse=True)[:3]
        concentration_ratio = (sum(top_3_revenues) / total_market * 100) if total_market > 0 else 0

        return MarketPositionAnalysis(
            position=position,
            market_share_percentage=round(market_share, 2),
            rank_in_industry=rank,
            total_competitors_identified=len(competitors),
            market_growth_rate=5.2,  # Mock: 5.2% annual growth
            market_size_pln=total_market,
            concentration_ratio=round(concentration_ratio, 2),
            differentiation_factors=["Custom solutions", "Industry expertise"],
            target_segments=["SMB", "Enterprise"],
            positioning_strategy="differentiation"
        )


    async def _generate_swot_analysis(
        self,
        target_data: Dict[str, Any],
        competitors: List[CompetitorProfile],
        market_position: MarketPositionAnalysis
    ) -> SWOTAnalysis:
        """
        Generate SWOT analysis based on competitive landscape.

        Week 11: Enhanced with Claude AI integration for deeper insights.
        Falls back to rule-based analysis if Claude is unavailable.
        """
        logger.info("Generating SWOT analysis")

        # Week 11: Try Claude-powered SWOT analysis first
        if self.claude_available and self.claude_service:
            try:
                return await self._generate_swot_with_claude(
                    target_data, competitors, market_position
                )
            except Exception as e:
                logger.warning(f"Claude SWOT generation failed: {str(e)}, using fallback")

        # Fallback: Rule-based SWOT analysis (Week 10 implementation)

        strengths = [
            SWOTItem(
                category=SWOTCategory.STRENGTH,
                description="Established market presence with solid customer base",
                impact_level="high",
                evidence=f"Market position: {market_position.position}"
            ),
            SWOTItem(
                category=SWOTCategory.STRENGTH,
                description="Experienced team with domain expertise",
                impact_level="medium",
                evidence=f"{target_data.get('employees', 0)} employees"
            )
        ]

        weaknesses = [
            SWOTItem(
                category=SWOTCategory.WEAKNESS,
                description="Limited geographic coverage compared to larger competitors",
                impact_level="medium",
                evidence=f"Operating primarily in {target_data.get('voivodeship')}"
            )
        ]

        opportunities = [
            SWOTItem(
                category=SWOTCategory.OPPORTUNITY,
                description="Growing market demand for digital transformation services",
                impact_level="high",
                evidence=f"Market growth rate: {market_position.market_growth_rate}%"
            ),
            SWOTItem(
                category=SWOTCategory.OPPORTUNITY,
                description="Potential for geographic expansion to underserved regions",
                impact_level="medium",
                evidence="Competitor analysis shows gaps in certain voivodeships"
            )
        ]

        threats = [
            SWOTItem(
                category=SWOTCategory.THREAT,
                description="Intense competition from well-funded competitors",
                impact_level="high",
                evidence=f"{len(competitors)} direct competitors identified"
            ),
            SWOTItem(
                category=SWOTCategory.THREAT,
                description="Market concentration risk with top players dominating",
                impact_level="medium",
                evidence=f"Market concentration: {market_position.concentration_ratio}%"
            )
        ]

        # Determine overall strategic position
        strength_score = len([s for s in strengths if s.impact_level == "high"]) * 3 + len([s for s in strengths if s.impact_level == "medium"]) * 2
        weakness_score = len([w for w in weaknesses if w.impact_level == "high"]) * 3 + len([w for w in weaknesses if w.impact_level == "medium"]) * 2

        if strength_score > weakness_score * 1.5:
            overall_position = "strong"
        elif strength_score < weakness_score * 0.7:
            overall_position = "weak"
        else:
            overall_position = "moderate"

        return SWOTAnalysis(
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            threats=threats,
            overall_strategic_position=overall_position
        )


    async def _generate_swot_with_claude(
        self,
        target_data: Dict[str, Any],
        competitors: List[CompetitorProfile],
        market_position: MarketPositionAnalysis
    ) -> SWOTAnalysis:
        """
        Generate SWOT analysis using Claude AI for deeper insights.

        Week 11: AI-powered SWOT generation with natural language processing.
        """
        logger.info("Generating SWOT analysis with Claude AI")

        # Prepare context data for Claude
        context_data = {
            "company_name": target_data.get('company_name', 'Target Company'),
            "industry": target_data.get('industry', 'Unknown'),
            "market_position": market_position.position,
            "market_share": f"{market_position.market_share_percentage:.1f}%" if market_position.market_share_percentage else "Unknown",
            "rank": market_position.rank_in_industry,
            "total_competitors": len(competitors),
            "employees": target_data.get('employees', 0),
            "revenue": target_data.get('revenue', 0),
            "voivodeship": target_data.get('voivodeship', 'Unknown'),
            "competitors_summary": [
                {
                    "name": c.company_name,
                    "type": c.competitor_type,
                    "similarity": c.similarity_score
                }
                for c in competitors[:5]  # Top 5 competitors
            ]
        }

        # Generate SWOT with Claude
        response = await self.claude_service.generate_report(
            report_type="swot_analysis",
            data=context_data,
            company_name=target_data.get('company_name'),
            language="pl"
        )

        # Parse Claude response (expecting JSON-like structure)
        # Note: Claude might not return perfect JSON, so we'll parse flexibly
        try:
            # Try to extract JSON from response
            swot_data = self._parse_claude_swot_response(response)

            # Convert to SWOTAnalysis model
            strengths = [
                SWOTItem(
                    category=SWOTCategory.STRENGTH,
                    description=item.get('description', ''),
                    impact_level=item.get('impact', 'medium'),
                    evidence=item.get('evidence')
                )
                for item in swot_data.get('strengths', [])
            ]

            weaknesses = [
                SWOTItem(
                    category=SWOTCategory.WEAKNESS,
                    description=item.get('description', ''),
                    impact_level=item.get('impact', 'medium'),
                    evidence=item.get('evidence')
                )
                for item in swot_data.get('weaknesses', [])
            ]

            opportunities = [
                SWOTItem(
                    category=SWOTCategory.OPPORTUNITY,
                    description=item.get('description', ''),
                    impact_level=item.get('impact', 'medium'),
                    evidence=item.get('evidence')
                )
                for item in swot_data.get('opportunities', [])
            ]

            threats = [
                SWOTItem(
                    category=SWOTCategory.THREAT,
                    description=item.get('description', ''),
                    impact_level=item.get('impact', 'medium'),
                    evidence=item.get('evidence')
                )
                for item in swot_data.get('threats', [])
            ]

            # Determine overall position based on balance
            strength_score = len([s for s in strengths if s.impact_level == "high"]) * 3 + \
                           len([s for s in strengths if s.impact_level == "medium"]) * 2
            weakness_score = len([w for w in weaknesses if w.impact_level == "high"]) * 3 + \
                           len([w for w in weaknesses if w.impact_level == "medium"]) * 2

            if strength_score > weakness_score * 1.5:
                overall_position = "strong"
            elif strength_score < weakness_score * 0.7:
                overall_position = "weak"
            else:
                overall_position = "moderate"

            return SWOTAnalysis(
                strengths=strengths,
                weaknesses=weaknesses,
                opportunities=opportunities,
                threats=threats,
                overall_strategic_position=overall_position
            )

        except Exception as e:
            logger.error(f"Error parsing Claude SWOT response: {str(e)}")
            raise


    def _parse_claude_swot_response(self, response: str) -> Dict[str, List[Dict[str, str]]]:
        """
        Parse Claude's SWOT response into structured format.

        Handles both JSON and natural language responses.
        """
        # Try JSON parsing first
        try:
            # Look for JSON block in response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass

        # Fallback: Parse natural language (simplified for Week 11)
        # Return minimal structure
        return {
            "strengths": [
                {"description": "Market presence and customer base", "impact": "high", "evidence": "Established position"}
            ],
            "weaknesses": [
                {"description": "Limited geographic coverage", "impact": "medium", "evidence": "Analysis shows concentration"}
            ],
            "opportunities": [
                {"description": "Market growth potential", "impact": "high", "evidence": "Industry trends"}
            ],
            "threats": [
                {"description": "Competitive pressure", "impact": "high", "evidence": "Multiple competitors"}
            ]
        }


    async def _generate_competitive_insights(
        self,
        target_data: Dict[str, Any],
        competitors: List[CompetitorProfile],
        market_position: MarketPositionAnalysis,
        swot_analysis: Optional[SWOTAnalysis]
    ) -> List[CompetitiveInsight]:
        """
        Generate actionable competitive insights.
        """
        logger.info("Generating competitive insights")

        insights = []

        # Market opportunity insight
        if market_position.market_growth_rate and market_position.market_growth_rate > 5:
            insights.append(CompetitiveInsight(
                insight_type="opportunity",
                title="High Market Growth Opportunity",
                description=f"Market is growing at {market_position.market_growth_rate}% annually, presenting expansion opportunities",
                priority="high",
                recommended_actions=[
                    "Increase marketing investment to capture growing demand",
                    "Expand service offerings to address emerging needs",
                    "Consider geographic expansion to new regions"
                ]
            ))

        # Competitive threat insight
        if len(competitors) > 3:
            insights.append(CompetitiveInsight(
                insight_type="threat",
                title="Fragmented Competitive Landscape",
                description=f"Identified {len(competitors)} competitors, indicating high market fragmentation",
                priority="medium",
                recommended_actions=[
                    "Strengthen brand differentiation",
                    "Focus on niche segments where competition is lower",
                    "Build strategic partnerships for competitive advantage"
                ]
            ))

        # Market gap insight
        insights.append(CompetitiveInsight(
            insight_type="market_gap",
            title="Potential Underserved Market Segments",
            description="Analysis reveals potential gaps in specific geographic regions and industry verticals",
            priority="medium",
            recommended_actions=[
                "Conduct detailed market research on identified gaps",
                "Develop targeted offerings for underserved segments",
                "Pilot new services in selected regions"
            ]
        ))

        return insights


    def _identify_market_gaps(
        self,
        competitors: List[CompetitorProfile],
        target_data: Dict[str, Any]
    ) -> List[str]:
        """
        Identify market gaps and opportunities.
        """
        logger.info("Identifying market gaps")

        gaps = []

        # Geographic gaps
        all_voivodeships = set(self.domain_knowledge.VOIVODESHIPS)
        covered_voivodeships = set()
        for competitor in competitors:
            covered_voivodeships.update(competitor.geographic_coverage)

        uncovered = all_voivodeships - covered_voivodeships
        if uncovered:
            gaps.append(f"Geographic expansion opportunity: {', '.join(list(uncovered)[:3])}")

        # Service gaps (analyze key products)
        all_products = set()
        for competitor in competitors:
            all_products.update(competitor.key_products)

        if len(all_products) < 10:  # Low product diversity
            gaps.append("Limited product diversity in market - opportunity for innovative offerings")

        # Market segment gaps
        all_markets = set()
        for competitor in competitors:
            all_markets.update(competitor.key_markets)

        potential_segments = {"Healthcare", "Education", "Manufacturing", "Energy", "Transportation"}
        underserved = potential_segments - all_markets
        if underserved:
            gaps.append(f"Underserved market segments: {', '.join(list(underserved)[:2])}")

        return gaps


    def _generate_strategic_recommendations(
        self,
        market_position: MarketPositionAnalysis,
        swot_analysis: Optional[SWOTAnalysis],
        insights: List[CompetitiveInsight],
        market_gaps: List[str]
    ) -> List[str]:
        """
        Generate strategic recommendations based on all analyses.
        """
        logger.info("Generating strategic recommendations")

        recommendations = []

        # Position-based recommendations
        if market_position.position == MarketPosition.LEADER:
            recommendations.append("Maintain market leadership through continuous innovation and customer retention programs")
            recommendations.append("Consider strategic acquisitions to consolidate market position")
        elif market_position.position == MarketPosition.CHALLENGER:
            recommendations.append("Invest in differentiation to challenge market leader")
            recommendations.append("Focus on capturing market share through competitive pricing and superior service")
        elif market_position.position == MarketPosition.FOLLOWER:
            recommendations.append("Develop niche expertise to avoid direct competition with larger players")
            recommendations.append("Form strategic alliances to increase market presence")
        else:  # NICHE
            recommendations.append("Deepen specialization in chosen niche to build competitive moat")
            recommendations.append("Expand within niche before considering broader market entry")

        # SWOT-based recommendations
        if swot_analysis:
            if swot_analysis.total_opportunities > swot_analysis.total_threats:
                recommendations.append("Capitalize on identified opportunities through aggressive growth strategy")
            if swot_analysis.total_threats > swot_analysis.total_strengths:
                recommendations.append("Implement risk mitigation strategies to address key threats")

        # Gap-based recommendations
        if market_gaps:
            recommendations.append("Explore identified market gaps as potential growth vectors")

        return recommendations


    async def _generate_porter_analysis(
        self,
        target_data: Dict[str, Any],
        competitors: List[CompetitorProfile],
        market_position: MarketPositionAnalysis
    ) -> Optional[PorterAnalysis]:
        """
        Generate Porter's Five Forces analysis.

        Week 11: Strategic industry analysis framework.
        """
        logger.info("Generating Porter's Five Forces analysis")

        try:
            # Create Porter forces
            threat_of_new_entrants = PorterForce(
                force_name="threat_of_new_entrants",
                strength="medium",
                description="Moderate barriers to entry exist in the industry",
                key_factors=[
                    "Capital requirements moderate",
                    "Regulatory requirements present",
                    "Brand loyalty of existing players"
                ],
                impact_on_profitability="negative"
            )

            supplier_power = PorterForce(
                force_name="bargaining_power_of_suppliers",
                strength="low",
                description="Multiple suppliers available, limited supplier concentration",
                key_factors=[
                    "Many alternative suppliers",
                    "Low switching costs",
                    "Standardized inputs"
                ],
                impact_on_profitability="positive"
            )

            buyer_power = PorterForce(
                force_name="bargaining_power_of_buyers",
                strength="medium",
                description="Buyers have moderate negotiating power",
                key_factors=[
                    "Multiple competitors available",
                    "Price sensitivity varies by segment",
                    "Some switching costs exist"
                ],
                impact_on_profitability="negative"
            )

            threat_of_substitutes = PorterForce(
                force_name="threat_of_substitutes",
                strength="medium",
                description="Alternative solutions exist but not perfect substitutes",
                key_factors=[
                    "Substitute products available",
                    "Performance-price trade-offs",
                    "Customer inertia present"
                ],
                impact_on_profitability="negative"
            )

            # Base competitive rivalry on actual market data
            rivalry_strength = "high" if len(competitors) > 5 else "medium"
            competitive_rivalry = PorterForce(
                force_name="competitive_rivalry",
                strength=rivalry_strength,
                description=f"{'Intense' if rivalry_strength == 'high' else 'Moderate'} competition among {len(competitors)} identified competitors",
                key_factors=[
                    f"{len(competitors)} direct competitors",
                    f"Market concentration: {market_position.concentration_ratio}%",
                    "Product differentiation varies"
                ],
                impact_on_profitability="negative"
            )

            # Determine industry attractiveness
            negative_forces = sum(1 for f in [threat_of_new_entrants, buyer_power, threat_of_substitutes, competitive_rivalry]
                                if f.strength in ["high", "medium"])

            if negative_forces <= 2:
                attractiveness = "high"
            elif negative_forces == 3:
                attractiveness = "medium"
            else:
                attractiveness = "low"

            return PorterAnalysis(
                threat_of_new_entrants=threat_of_new_entrants,
                bargaining_power_of_suppliers=supplier_power,
                bargaining_power_of_buyers=buyer_power,
                threat_of_substitutes=threat_of_substitutes,
                competitive_rivalry=competitive_rivalry,
                industry_attractiveness=attractiveness,
                overall_profitability_outlook=f"Industry profitability is {attractiveness} due to competitive dynamics",
                strategic_recommendations=[
                    "Focus on differentiation to reduce buyer power",
                    "Build switching costs to retain customers",
                    "Monitor new entrants and respond quickly"
                ]
            )

        except Exception as e:
            logger.error(f"Error generating Porter analysis: {str(e)}")
            return None


    def _identify_competitive_advantages(
        self,
        target_data: Dict[str, Any],
        market_position: MarketPositionAnalysis,
        swot_analysis: Optional[SWOTAnalysis]
    ) -> List[CompetitiveAdvantage]:
        """
        Identify competitive advantages of the target company.

        Week 11: Competitive advantage framework (cost leadership, differentiation, focus).
        """
        logger.info("Identifying competitive advantages")

        advantages = []

        # Cost leadership potential
        if market_position.position in [MarketPosition.LEADER, MarketPosition.CHALLENGER]:
            advantages.append(CompetitiveAdvantage(
                advantage_type="cost_leadership",
                strength="moderate",
                description="Scale advantages enable competitive cost structure",
                sustainability="medium",
                supporting_evidence=[
                    f"Market position: {market_position.position}",
                    f"Market share: {market_position.market_share_percentage}%"
                ]
            ))

        # Differentiation potential
        if swot_analysis and swot_analysis.total_strengths > 2:
            advantages.append(CompetitiveAdvantage(
                advantage_type="differentiation",
                strength="moderate",
                description="Strong capabilities and resources enable differentiation",
                sustainability="medium",
                supporting_evidence=[
                    f"{swot_analysis.total_strengths} key strengths identified",
                    "Established market presence"
                ]
            ))

        # Focus/niche strategy
        if market_position.position == MarketPosition.NICHE:
            advantages.append(CompetitiveAdvantage(
                advantage_type="focus",
                strength="strong",
                description="Specialized focus on niche market segment",
                sustainability="high",
                supporting_evidence=[
                    "Niche market positioning",
                    "Specialized expertise"
                ]
            ))

        return advantages


    def _calculate_confidence_score(
        self,
        target_data: Dict[str, Any],
        competitors: List[CompetitorProfile],
        market_position: Optional[MarketPositionAnalysis],
        swot_analysis: Optional[SWOTAnalysis]
    ) -> float:
        """
        Calculate confidence score for the analysis.

        Scoring:
            - Target company data: 30 points
            - Competitors found: 40 points (scaled)
            - Market position analyzed: 20 points
            - SWOT generated: 10 points
        """
        score = 0.0

        # Target company data (30 points)
        if target_data.get('valid'):
            score += 30
            if target_data.get('pkd_codes'):
                score += 5  # Bonus for detailed data

        # Competitors found (40 points, scaled by count)
        if len(competitors) > 0:
            # Scale: 1 competitor = 20, 5+ competitors = 40
            competitor_score = min(40, len(competitors) * 8)
            score += competitor_score

        # Market position (20 points)
        if market_position:
            score += 20

        # SWOT analysis (10 points)
        if swot_analysis:
            score += 10

        return min(100.0, round(score, 2))


    def _build_output(
        self,
        target: str,
        data: Dict[str, Any],
        confidence_score: float,
        data_sources: List[str],
        errors: List[str],
        warnings: List[str]
    ) -> CompetitorMappingOutput:
        """
        Build final output structure.
        """
        return CompetitorMappingOutput(
            target=target,
            target_company_name=data.get('target_company_name'),
            target_industry=data.get('target_industry'),
            target_pkd_codes=data.get('target_pkd_codes', []),
            competitors=data.get('competitors', []),
            market_position=data.get('market_position'),
            swot_analysis=data.get('swot_analysis'),
            competitive_insights=data.get('competitive_insights', []),
            strategic_recommendations=data.get('strategic_recommendations', []),
            market_gaps_identified=data.get('market_gaps_identified', []),
            confidence_score=confidence_score,
            data_sources=data_sources,
            errors=errors,
            warnings=warnings,
            last_updated=datetime.utcnow()
        )
