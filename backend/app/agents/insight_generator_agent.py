"""
Insight Generator Agent

Autonomous agent for pattern recognition and predictive insights.
Analyzes data from multiple sources to identify trends, risks, and opportunities.

Week 16 Implementation: Foundation agent for insight generation.

Use case: "Generate insights for company with NIP 1234567890"
         "Identify growth patterns in financial data"
         "Predict market trends for PKD 6201"
"""

import logging
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field, field_validator

from app.services.agent_tools import ToolRegistry, get_tool_registry
from app.services.claude_service import get_claude_service, is_claude_available, SystemPromptType, ClaudeModel

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class InsightType(str, Enum):
    """Types of insights"""
    TREND = "trend"  # Historical patterns and trends
    PREDICTION = "prediction"  # Future forecasts
    RISK = "risk"  # Potential threats
    OPPORTUNITY = "opportunity"  # Growth opportunities
    ANOMALY = "anomaly"  # Unusual patterns
    CORRELATION = "correlation"  # Relationships between metrics
    STRATEGIC = "strategic"  # Strategic recommendations


class PatternType(str, Enum):
    """Types of patterns detected"""
    GROWTH = "growth"  # Upward trend
    DECLINE = "decline"  # Downward trend
    SEASONAL = "seasonal"  # Seasonal variations
    CYCLICAL = "cyclical"  # Business cycles
    VOLATILE = "volatile"  # High variability
    STABLE = "stable"  # Consistent performance
    BREAKOUT = "breakout"  # Sudden change
    REVERSAL = "reversal"  # Trend reversal


class PredictionConfidence(str, Enum):
    """Confidence levels for predictions"""
    VERY_HIGH = "very_high"  # 90-100%: Strong evidence
    HIGH = "high"  # 70-89%: Good indicators
    MEDIUM = "medium"  # 50-69%: Moderate confidence
    LOW = "low"  # 30-49%: Weak signals
    VERY_LOW = "very_low"  # 0-29%: Highly uncertain


class RiskLevel(str, Enum):
    """Risk severity classification"""
    CRITICAL = "critical"  # Immediate threat
    HIGH = "high"  # Major concern
    MEDIUM = "medium"  # Moderate risk
    LOW = "low"  # Minor risk
    MINIMAL = "minimal"  # Negligible risk


class OpportunityType(str, Enum):
    """Types of opportunities"""
    MARKET_EXPANSION = "market_expansion"  # New market entry
    PRODUCT_INNOVATION = "product_innovation"  # New products/services
    COST_REDUCTION = "cost_reduction"  # Efficiency improvements
    REVENUE_GROWTH = "revenue_growth"  # Revenue opportunities
    PARTNERSHIP = "partnership"  # Strategic partnerships
    ACQUISITION = "acquisition"  # M&A opportunities
    DIGITAL_TRANSFORMATION = "digital_transformation"  # Tech opportunities


# ============================================================================
# DOMAIN KNOWLEDGE
# ============================================================================

class InsightGeneratorDomainKnowledge:
    """
    Domain knowledge for pattern recognition and predictive analytics.
    Based on data science, business analytics, and forecasting best practices.
    """

    # Pattern detection thresholds
    GROWTH_THRESHOLD = 5.0  # % growth to be considered significant
    DECLINE_THRESHOLD = -5.0  # % decline to be considered significant
    VOLATILITY_THRESHOLD = 20.0  # Coefficient of variation threshold
    SEASONAL_MIN_PERIODS = 4  # Minimum periods for seasonal detection
    TREND_MIN_PERIODS = 3  # Minimum periods for trend detection

    # Prediction confidence scoring
    CONFIDENCE_FACTORS = {
        "data_points": 0.30,  # Weight of historical data availability
        "consistency": 0.25,  # Weight of pattern consistency
        "external_validation": 0.20,  # Weight of external confirmation
        "time_horizon": 0.15,  # Weight of prediction timeframe
        "volatility": 0.10,  # Weight of data stability
    }

    # Risk assessment weights
    RISK_WEIGHTS = {
        "financial_risk": 0.30,  # Financial stability concerns
        "market_risk": 0.25,  # Market conditions
        "operational_risk": 0.20,  # Operational issues
        "competitive_risk": 0.15,  # Competitive threats
        "regulatory_risk": 0.10,  # Legal/regulatory changes
    }

    # Time horizon for predictions (days)
    PREDICTION_HORIZONS = {
        "short_term": 90,  # 3 months
        "medium_term": 365,  # 1 year
        "long_term": 1095,  # 3 years
    }


# ============================================================================
# OUTPUT SCHEMA
# ============================================================================

class Pattern(BaseModel):
    """Detected pattern in data"""
    pattern_id: str = Field(..., description="Unique pattern identifier")
    pattern_type: PatternType
    pattern_description: str = Field(..., min_length=10, description="Human-readable pattern description")

    # Pattern characteristics
    confidence_score: float = Field(..., ge=0, le=100, description="Pattern confidence 0-100")
    strength: float = Field(..., ge=0, le=100, description="Pattern strength/significance")

    # Data support
    data_points: int = Field(..., ge=1, description="Number of data points supporting pattern")
    time_period: str = Field(..., description="Time period covered (e.g., '2023-2024', 'Q1-Q4 2024')")

    # Statistical measures
    trend_percentage: Optional[float] = Field(None, description="Percentage change if trend")
    volatility_score: Optional[float] = Field(None, ge=0, description="Volatility measure")
    seasonality_detected: bool = False

    # Context
    affected_metrics: List[str] = Field(default_factory=list, description="Metrics showing this pattern")
    contributing_factors: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class Prediction(BaseModel):
    """Predictive forecast"""
    prediction_id: str = Field(..., description="Unique prediction identifier")
    prediction_text: str = Field(..., min_length=10, description="What is being predicted")

    # Prediction details
    predicted_value: Optional[str] = Field(None, description="Specific predicted value/outcome")
    prediction_confidence: PredictionConfidence
    confidence_score: float = Field(..., ge=0, le=100, description="Numerical confidence 0-100")

    # Time frame
    time_horizon: str = Field(..., pattern="^(short_term|medium_term|long_term)$")
    prediction_date: datetime = Field(default_factory=datetime.utcnow)
    target_date: Optional[datetime] = Field(None, description="When prediction applies")

    # Supporting evidence
    based_on_patterns: List[str] = Field(default_factory=list, description="Pattern IDs supporting prediction")
    supporting_factors: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)

    # Validation
    can_be_validated: bool = True
    validation_metrics: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class Risk(BaseModel):
    """Identified risk"""
    risk_id: str = Field(..., description="Unique risk identifier")
    risk_description: str = Field(..., min_length=10, description="What the risk is")
    risk_level: RiskLevel

    # Impact assessment
    impact_score: float = Field(..., ge=0, le=100, description="Potential impact 0-100")
    probability_score: float = Field(..., ge=0, le=100, description="Likelihood 0-100")
    risk_score: float = Field(..., ge=0, le=100, description="Overall risk score (impact * probability)")

    # Risk details
    risk_category: str = Field(..., description="e.g., 'financial', 'operational', 'market'")
    affected_areas: List[str] = Field(default_factory=list)
    potential_consequences: List[str] = Field(default_factory=list)

    # Mitigation
    mitigation_strategies: List[str] = Field(default_factory=list)
    monitoring_metrics: List[str] = Field(default_factory=list)

    # Timeline
    time_to_impact: Optional[str] = Field(None, description="e.g., 'immediate', '3-6 months', '1 year'")

    class Config:
        use_enum_values = True


class Opportunity(BaseModel):
    """Identified opportunity"""
    opportunity_id: str = Field(..., description="Unique opportunity identifier")
    opportunity_description: str = Field(..., min_length=10, description="What the opportunity is")
    opportunity_type: OpportunityType

    # Value assessment
    value_score: float = Field(..., ge=0, le=100, description="Potential value 0-100")
    feasibility_score: float = Field(..., ge=0, le=100, description="Implementation feasibility 0-100")
    priority_score: float = Field(..., ge=0, le=100, description="Overall priority (value * feasibility)")

    # Opportunity details
    target_market: Optional[str] = Field(None, description="Target market or segment")
    required_resources: List[str] = Field(default_factory=list)
    expected_benefits: List[str] = Field(default_factory=list)

    # Implementation
    recommended_actions: List[str] = Field(default_factory=list)
    time_to_execute: Optional[str] = Field(None, description="e.g., 'immediate', '3-6 months', '1 year'")

    # Success metrics
    success_metrics: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class Insight(BaseModel):
    """Generated insight with natural language explanation"""
    insight_id: str = Field(..., description="Unique insight identifier")
    insight_type: InsightType
    insight_text: str = Field(..., min_length=20, description="Natural language insight")

    # Importance
    priority: str = Field(..., pattern="^(critical|high|medium|low)$")
    relevance_score: float = Field(..., ge=0, le=100, description="Relevance to target 0-100")

    # Supporting evidence
    patterns: List[Pattern] = Field(default_factory=list)
    predictions: List[Prediction] = Field(default_factory=list)
    risks: List[Risk] = Field(default_factory=list)
    opportunities: List[Opportunity] = Field(default_factory=list)

    # Actionability
    is_actionable: bool = True
    recommended_actions: List[str] = Field(default_factory=list)

    # Metadata
    generated_date: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class InsightGeneratorOutput(BaseModel):
    """Complete output from InsightGeneratorAgent"""
    target: str = Field(..., description="Analysis target (company NIP/KRS, PKD code, etc.)")
    analysis_date: datetime = Field(default_factory=datetime.utcnow)

    # Insights
    insights: List[Insight] = Field(default_factory=list)
    total_insights: int = Field(default=0, ge=0)

    # Patterns
    patterns_detected: List[Pattern] = Field(default_factory=list)
    total_patterns: int = Field(default=0, ge=0)

    # Predictions
    predictions: List[Prediction] = Field(default_factory=list)
    total_predictions: int = Field(default=0, ge=0)

    # Risks & Opportunities
    risks_identified: List[Risk] = Field(default_factory=list)
    opportunities_identified: List[Opportunity] = Field(default_factory=list)

    # Summary scores
    overall_risk_score: float = Field(default=0.0, ge=0, le=100)
    overall_opportunity_score: float = Field(default=0.0, ge=0, le=100)
    confidence_score: float = Field(default=0.0, ge=0, le=100, description="Overall analysis confidence")

    # Recommendations
    strategic_recommendations: List[str] = Field(default_factory=list)
    priority_actions: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


# ============================================================================
# INSIGHT GENERATOR AGENT
# ============================================================================

class InsightGeneratorAgent:
    """
    Autonomous agent for pattern recognition and predictive insights.

    Capabilities:
    - Pattern detection in time-series data
    - Trend analysis and forecasting
    - Risk identification and assessment
    - Opportunity detection
    - Natural language insight generation (Claude-powered)
    - Strategic recommendations

    Week 16: Foundation implementation with core pattern detection and Claude integration.
    """

    def __init__(self):
        """Initialize the insight generator agent"""
        self.domain_knowledge = InsightGeneratorDomainKnowledge()
        self.tool_registry = get_tool_registry()
        self.claude_service = get_claude_service() if is_claude_available() else None

        logger.info("InsightGeneratorAgent initialized (Week 16 - Foundation)")

    async def execute(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> InsightGeneratorOutput:
        """
        Main execution method for insight generation.

        Args:
            query: Target for analysis (NIP, KRS, PKD code, company name)
            context: Optional context with data:
                - financial_data: List of financial statements
                - competitor_data: Competitor information
                - market_data: Market trends
                - digital_presence: Website/social media data

        Returns:
            InsightGeneratorOutput with patterns, predictions, risks, and opportunities
        """
        logger.info(f"InsightGeneratorAgent executing for target: {query}")

        context = context or {}

        # Initialize output
        output = InsightGeneratorOutput(target=query)

        # Step 1: Detect patterns in available data
        patterns = await self._detect_patterns(query, context)
        output.patterns_detected = patterns
        output.total_patterns = len(patterns)

        # Step 2: Generate predictions based on patterns
        predictions = await self._generate_predictions(patterns, context)
        output.predictions = predictions
        output.total_predictions = len(predictions)

        # Step 3: Identify risks
        risks = await self._identify_risks(patterns, predictions, context)
        output.risks_identified = risks
        if risks:
            output.overall_risk_score = sum(r.risk_score for r in risks) / len(risks)

        # Step 4: Identify opportunities
        opportunities = await self._identify_opportunities(patterns, predictions, context)
        output.opportunities_identified = opportunities
        if opportunities:
            output.overall_opportunity_score = sum(o.priority_score for o in opportunities) / len(opportunities)

        # Step 5: Generate natural language insights (Claude)
        insights = await self._generate_insights_with_llm(
            query, patterns, predictions, risks, opportunities, context
        )
        output.insights = insights
        output.total_insights = len(insights)

        # Step 6: Calculate overall confidence
        output.confidence_score = self._calculate_overall_confidence(patterns, predictions)

        # Step 7: Week 17 - Advanced Analysis
        # Anomaly detection
        if "financial_data" in context and context["financial_data"]:
            financial_data = context["financial_data"]
            if len(financial_data) >= 5 and all("revenue" in item for item in financial_data):
                revenues = [item["revenue"] for item in financial_data]
                anomaly_pattern = self._detect_anomalies(revenues, "revenue")
                if anomaly_pattern:
                    output.patterns_detected.append(anomaly_pattern)
                    output.total_patterns += 1

        # Correlation analysis
        correlation_data = {}
        if "financial_data" in context and context["financial_data"]:
            financial_data = context["financial_data"]
            if len(financial_data) >= 3:
                if all("revenue" in item for item in financial_data):
                    correlation_data["revenue"] = [item["revenue"] for item in financial_data]
                if all("profit_margin" in item for item in financial_data):
                    correlation_data["profit_margin"] = [item["profit_margin"] for item in financial_data]

        if len(correlation_data) >= 2:
            correlation_insights = self._analyze_correlations(correlation_data)
            output.insights.extend(correlation_insights)
            output.total_insights += len(correlation_insights)

        # Scenario analysis
        scenario_insights = await self._generate_scenario_analysis(patterns, predictions)
        output.insights.extend(scenario_insights)
        output.total_insights += len(scenario_insights)

        # Advanced forecasting
        if "financial_data" in context and context["financial_data"]:
            financial_data = context["financial_data"]
            if len(financial_data) >= 5 and all("revenue" in item for item in financial_data):
                revenues = [item["revenue"] for item in financial_data]
                advanced_forecast = self._advanced_forecast(revenues, "revenue", periods_ahead=3)
                if advanced_forecast:
                    output.predictions.append(advanced_forecast)
                    output.total_predictions += 1

        # Step 8: Generate strategic recommendations
        output.strategic_recommendations = self._generate_recommendations(
            patterns, predictions, risks, opportunities
        )
        output.priority_actions = self._prioritize_actions(risks, opportunities)

        logger.info(f"Insight generation complete: {output.total_insights} insights, "
                   f"{output.total_patterns} patterns, {output.total_predictions} predictions "
                   f"(Week 17 enhanced with anomaly detection, correlations, and scenarios)")

        return output

    # ========================================================================
    # PATTERN DETECTION
    # ========================================================================

    async def _detect_patterns(
        self,
        target: str,
        context: Dict[str, Any]
    ) -> List[Pattern]:
        """
        Detect patterns in available data.

        Analyzes:
        - Financial trends (revenue, profit, growth rates)
        - Market trends (market share, competitive position)
        - Operational trends (employee count, efficiency metrics)
        - Digital presence trends (SEO, social media growth)
        """
        patterns = []

        # Financial data patterns
        if "financial_data" in context:
            financial_patterns = self._detect_financial_patterns(context["financial_data"])
            patterns.extend(financial_patterns)

        # Market data patterns
        if "market_data" in context:
            market_patterns = self._detect_market_patterns(context["market_data"])
            patterns.extend(market_patterns)

        # Competitor data patterns
        if "competitor_data" in context:
            competitive_patterns = self._detect_competitive_patterns(context["competitor_data"])
            patterns.extend(competitive_patterns)

        # Digital presence patterns
        if "digital_presence" in context:
            digital_patterns = self._detect_digital_patterns(context["digital_presence"])
            patterns.extend(digital_patterns)

        return patterns

    def _detect_financial_patterns(self, financial_data: List[Dict[str, Any]]) -> List[Pattern]:
        """Detect patterns in financial data"""
        patterns = []

        if len(financial_data) < self.domain_knowledge.TREND_MIN_PERIODS:
            return patterns

        # Sort by period
        sorted_data = sorted(financial_data, key=lambda x: x.get("period", ""))

        # Revenue trend analysis
        if all("revenue" in item for item in sorted_data):
            revenues = [item["revenue"] for item in sorted_data]
            revenue_pattern = self._analyze_trend(
                revenues,
                metric_name="revenue",
                pattern_id="fin_revenue_trend",
                time_period=f"{sorted_data[0].get('period', '')} - {sorted_data[-1].get('period', '')}"
            )
            if revenue_pattern:
                patterns.append(revenue_pattern)

        # Profit margin trend
        if all("profit_margin" in item for item in sorted_data):
            margins = [item["profit_margin"] for item in sorted_data]
            margin_pattern = self._analyze_trend(
                margins,
                metric_name="profit_margin",
                pattern_id="fin_margin_trend",
                time_period=f"{sorted_data[0].get('period', '')} - {sorted_data[-1].get('period', '')}"
            )
            if margin_pattern:
                patterns.append(margin_pattern)

        return patterns

    def _analyze_trend(
        self,
        values: List[float],
        metric_name: str,
        pattern_id: str,
        time_period: str
    ) -> Optional[Pattern]:
        """
        Analyze trend in numerical values.

        Returns Pattern if significant trend detected.
        """
        if len(values) < self.domain_knowledge.TREND_MIN_PERIODS:
            return None

        # Calculate trend percentage
        initial_value = values[0]
        final_value = values[-1]

        if initial_value == 0:
            return None

        trend_pct = ((final_value - initial_value) / initial_value) * 100

        # Determine pattern type
        pattern_type = PatternType.STABLE
        if trend_pct >= self.domain_knowledge.GROWTH_THRESHOLD:
            pattern_type = PatternType.GROWTH
        elif trend_pct <= self.domain_knowledge.DECLINE_THRESHOLD:
            pattern_type = PatternType.DECLINE

        # Calculate volatility
        mean_value = sum(values) / len(values)
        variance = sum((x - mean_value) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        cv = (std_dev / mean_value * 100) if mean_value != 0 else 0

        if cv >= self.domain_knowledge.VOLATILITY_THRESHOLD:
            pattern_type = PatternType.VOLATILE

        # Calculate confidence based on data points and consistency
        confidence = min(100, 50 + (len(values) * 5) + (30 if abs(trend_pct) > 10 else 0))

        pattern = Pattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            pattern_description=f"{metric_name.replace('_', ' ').title()} shows {pattern_type.value} trend with {abs(trend_pct):.1f}% change",
            confidence_score=confidence,
            strength=min(100, abs(trend_pct) * 2),
            data_points=len(values),
            time_period=time_period,
            trend_percentage=trend_pct,
            volatility_score=cv,
            affected_metrics=[metric_name],
            contributing_factors=[
                f"Period-over-period change: {trend_pct:.1f}%",
                f"Volatility: {cv:.1f}% (coefficient of variation)"
            ]
        )

        return pattern

    def _detect_market_patterns(self, market_data: Dict[str, Any]) -> List[Pattern]:
        """Detect patterns in market data"""
        patterns = []

        # Market share trend
        if "market_share_history" in market_data:
            shares = market_data["market_share_history"]
            if len(shares) >= self.domain_knowledge.TREND_MIN_PERIODS:
                share_values = [s["share"] for s in shares]
                share_pattern = self._analyze_trend(
                    share_values,
                    metric_name="market_share",
                    pattern_id="market_share_trend",
                    time_period=f"{shares[0].get('period', '')} - {shares[-1].get('period', '')}"
                )
                if share_pattern:
                    patterns.append(share_pattern)

        return patterns

    def _detect_competitive_patterns(self, competitor_data: Dict[str, Any]) -> List[Pattern]:
        """Detect patterns in competitive landscape"""
        patterns = []

        # Competitive pressure trend
        if "competitor_count_history" in competitor_data:
            counts = competitor_data["competitor_count_history"]
            if len(counts) >= self.domain_knowledge.TREND_MIN_PERIODS:
                count_values = [c["count"] for c in counts]
                competition_pattern = self._analyze_trend(
                    count_values,
                    metric_name="competitor_count",
                    pattern_id="competition_intensity",
                    time_period=f"{counts[0].get('period', '')} - {counts[-1].get('period', '')}"
                )
                if competition_pattern:
                    patterns.append(competition_pattern)

        return patterns

    def _detect_digital_patterns(self, digital_data: Dict[str, Any]) -> List[Pattern]:
        """Detect patterns in digital presence data"""
        patterns = []

        # SEO score trend
        if "seo_history" in digital_data:
            seo_scores = digital_data["seo_history"]
            if len(seo_scores) >= self.domain_knowledge.TREND_MIN_PERIODS:
                score_values = [s["score"] for s in seo_scores]
                seo_pattern = self._analyze_trend(
                    score_values,
                    metric_name="seo_score",
                    pattern_id="digital_seo_trend",
                    time_period=f"{seo_scores[0].get('period', '')} - {seo_scores[-1].get('period', '')}"
                )
                if seo_pattern:
                    patterns.append(seo_pattern)

        return patterns

    # ========================================================================
    # PREDICTION GENERATION
    # ========================================================================

    async def _generate_predictions(
        self,
        patterns: List[Pattern],
        context: Dict[str, Any]
    ) -> List[Prediction]:
        """
        Generate predictions based on detected patterns.

        Uses pattern analysis and statistical forecasting to make predictions.
        """
        predictions = []

        for pattern in patterns:
            if pattern.pattern_type in [PatternType.GROWTH, PatternType.DECLINE]:
                # Generate trend-based prediction
                prediction = self._create_trend_prediction(pattern)
                if prediction:
                    predictions.append(prediction)

            elif pattern.pattern_type == PatternType.VOLATILE:
                # Generate volatility warning
                prediction = self._create_volatility_prediction(pattern)
                if prediction:
                    predictions.append(prediction)

        return predictions

    def _create_trend_prediction(self, pattern: Pattern) -> Optional[Prediction]:
        """Create prediction based on trend pattern"""
        if not pattern.trend_percentage:
            return None

        # Extrapolate trend
        trend_direction = "continue growing" if pattern.trend_percentage > 0 else "continue declining"
        predicted_change = pattern.trend_percentage  # Simple extrapolation

        # Determine confidence based on pattern strength and consistency
        if pattern.confidence_score >= 80:
            confidence = PredictionConfidence.VERY_HIGH
        elif pattern.confidence_score >= 65:
            confidence = PredictionConfidence.HIGH
        elif pattern.confidence_score >= 45:
            confidence = PredictionConfidence.MEDIUM
        elif pattern.confidence_score >= 25:
            confidence = PredictionConfidence.LOW
        else:
            confidence = PredictionConfidence.VERY_LOW

        # Adjust confidence based on volatility
        confidence_score = pattern.confidence_score
        if pattern.volatility_score and pattern.volatility_score > 30:
            confidence_score = max(0, confidence_score - 15)

        prediction = Prediction(
            prediction_id=f"pred_{pattern.pattern_id}",
            prediction_text=f"{pattern.affected_metrics[0].replace('_', ' ').title()} is likely to {trend_direction} by approximately {abs(predicted_change):.1f}% in the next period",
            predicted_value=f"{predicted_change:+.1f}%",
            prediction_confidence=confidence,
            confidence_score=confidence_score,
            time_horizon="short_term",
            based_on_patterns=[pattern.pattern_id],
            supporting_factors=[
                f"Historical trend: {pattern.trend_percentage:.1f}%",
                f"Pattern confidence: {pattern.confidence_score:.0f}%",
                f"Based on {pattern.data_points} data points"
            ],
            risk_factors=[
                f"Volatility: {pattern.volatility_score:.1f}%" if pattern.volatility_score else "Unknown volatility",
                "External market conditions may change",
                "Assumes continuation of current conditions"
            ],
            validation_metrics=pattern.affected_metrics
        )

        return prediction

    def _create_volatility_prediction(self, pattern: Pattern) -> Optional[Prediction]:
        """Create prediction for volatile patterns"""
        if not pattern.volatility_score:
            return None

        prediction = Prediction(
            prediction_id=f"pred_vol_{pattern.pattern_id}",
            prediction_text=f"{pattern.affected_metrics[0].replace('_', ' ').title()} is expected to remain highly variable with continued volatility",
            prediction_confidence=PredictionConfidence.MEDIUM,
            confidence_score=60.0,
            time_horizon="short_term",
            based_on_patterns=[pattern.pattern_id],
            supporting_factors=[
                f"High volatility detected: {pattern.volatility_score:.1f}%",
                f"Inconsistent pattern over {pattern.data_points} periods"
            ],
            risk_factors=[
                "Difficult to predict specific values",
                "May indicate unstable business conditions",
                "Requires monitoring and risk management"
            ],
            validation_metrics=pattern.affected_metrics
        )

        return prediction

    # ========================================================================
    # RISK & OPPORTUNITY IDENTIFICATION
    # ========================================================================

    async def _identify_risks(
        self,
        patterns: List[Pattern],
        predictions: List[Prediction],
        context: Dict[str, Any]
    ) -> List[Risk]:
        """Identify potential risks based on patterns and predictions"""
        risks = []

        # Check for decline patterns
        for pattern in patterns:
            if pattern.pattern_type == PatternType.DECLINE:
                risk = self._create_decline_risk(pattern)
                if risk:
                    risks.append(risk)

            elif pattern.pattern_type == PatternType.VOLATILE:
                risk = self._create_volatility_risk(pattern)
                if risk:
                    risks.append(risk)

        # Check for negative predictions
        for prediction in predictions:
            if "decline" in prediction.prediction_text.lower() or "decrease" in prediction.prediction_text.lower():
                risk = self._create_prediction_risk(prediction)
                if risk:
                    risks.append(risk)

        return risks

    def _create_decline_risk(self, pattern: Pattern) -> Optional[Risk]:
        """Create risk from decline pattern"""
        if not pattern.trend_percentage or pattern.trend_percentage >= 0:
            return None

        # Determine risk level based on decline severity
        decline_magnitude = abs(pattern.trend_percentage)
        if decline_magnitude >= 20:
            risk_level = RiskLevel.CRITICAL
            impact_score = 90.0
        elif decline_magnitude >= 15:
            risk_level = RiskLevel.HIGH
            impact_score = 75.0
        elif decline_magnitude >= 10:
            risk_level = RiskLevel.MEDIUM
            impact_score = 60.0
        else:
            risk_level = RiskLevel.LOW
            impact_score = 40.0

        probability_score = pattern.confidence_score

        risk = Risk(
            risk_id=f"risk_{pattern.pattern_id}",
            risk_description=f"Declining {pattern.affected_metrics[0].replace('_', ' ')} trend poses business risk",
            risk_level=risk_level,
            impact_score=impact_score,
            probability_score=probability_score,
            risk_score=(impact_score * probability_score) / 100,
            risk_category="financial" if "revenue" in pattern.affected_metrics[0] or "profit" in pattern.affected_metrics[0] else "operational",
            affected_areas=pattern.affected_metrics,
            potential_consequences=[
                f"Continued decline of {abs(pattern.trend_percentage):.1f}% per period",
                "Potential loss of market position",
                "Decreased investor confidence"
            ],
            mitigation_strategies=[
                "Investigate root causes of decline",
                "Implement corrective measures",
                "Monitor trend closely for reversal signals"
            ],
            monitoring_metrics=pattern.affected_metrics,
            time_to_impact="immediate"
        )

        return risk

    def _create_volatility_risk(self, pattern: Pattern) -> Optional[Risk]:
        """Create risk from volatile pattern"""
        if not pattern.volatility_score:
            return None

        risk = Risk(
            risk_id=f"risk_vol_{pattern.pattern_id}",
            risk_description=f"High volatility in {pattern.affected_metrics[0].replace('_', ' ')} indicates instability",
            risk_level=RiskLevel.MEDIUM,
            impact_score=65.0,
            probability_score=75.0,
            risk_score=48.75,
            risk_category="operational",
            affected_areas=pattern.affected_metrics,
            potential_consequences=[
                "Unpredictable performance",
                "Difficult planning and forecasting",
                "Potential for sudden negative changes"
            ],
            mitigation_strategies=[
                "Implement stabilization measures",
                "Diversify revenue streams",
                "Build financial reserves for volatility buffer"
            ],
            monitoring_metrics=pattern.affected_metrics,
            time_to_impact="3-6 months"
        )

        return risk

    def _create_prediction_risk(self, prediction: Prediction) -> Optional[Risk]:
        """Create risk from negative prediction"""
        risk = Risk(
            risk_id=f"risk_{prediction.prediction_id}",
            risk_description=f"Predicted negative outcome: {prediction.prediction_text}",
            risk_level=RiskLevel.MEDIUM,
            impact_score=60.0,
            probability_score=prediction.confidence_score,
            risk_score=(60.0 * prediction.confidence_score) / 100,
            risk_category="strategic",
            affected_areas=[],
            potential_consequences=["Realization of predicted negative trend"],
            mitigation_strategies=["Address underlying patterns", "Implement preventive measures"],
            monitoring_metrics=prediction.validation_metrics,
            time_to_impact=prediction.time_horizon
        )

        return risk

    async def _identify_opportunities(
        self,
        patterns: List[Pattern],
        predictions: List[Prediction],
        context: Dict[str, Any]
    ) -> List[Opportunity]:
        """Identify opportunities based on patterns and predictions"""
        opportunities = []

        # Check for growth patterns
        for pattern in patterns:
            if pattern.pattern_type == PatternType.GROWTH:
                opportunity = self._create_growth_opportunity(pattern)
                if opportunity:
                    opportunities.append(opportunity)

        # Check for positive predictions
        for prediction in predictions:
            if "grow" in prediction.prediction_text.lower() or "increase" in prediction.prediction_text.lower():
                opportunity = self._create_prediction_opportunity(prediction)
                if opportunity:
                    opportunities.append(opportunity)

        return opportunities

    def _create_growth_opportunity(self, pattern: Pattern) -> Optional[Opportunity]:
        """Create opportunity from growth pattern"""
        if not pattern.trend_percentage or pattern.trend_percentage <= 0:
            return None

        growth_magnitude = pattern.trend_percentage

        # Determine opportunity value
        if growth_magnitude >= 20:
            value_score = 90.0
        elif growth_magnitude >= 15:
            value_score = 75.0
        elif growth_magnitude >= 10:
            value_score = 65.0
        else:
            value_score = 50.0

        feasibility_score = pattern.confidence_score

        opportunity = Opportunity(
            opportunity_id=f"opp_{pattern.pattern_id}",
            opportunity_description=f"Capitalize on growing {pattern.affected_metrics[0].replace('_', ' ')} trend",
            opportunity_type=OpportunityType.REVENUE_GROWTH,
            value_score=value_score,
            feasibility_score=feasibility_score,
            priority_score=(value_score * feasibility_score) / 100,
            expected_benefits=[
                f"Potential {growth_magnitude:.1f}% growth continuation",
                "Market leadership opportunity",
                "Increased competitive advantage"
            ],
            recommended_actions=[
                "Invest in growth drivers",
                "Expand capacity to capture opportunity",
                "Accelerate initiatives supporting growth"
            ],
            time_to_execute="3-6 months",
            success_metrics=pattern.affected_metrics
        )

        return opportunity

    def _create_prediction_opportunity(self, prediction: Prediction) -> Optional[Opportunity]:
        """Create opportunity from positive prediction"""
        opportunity = Opportunity(
            opportunity_id=f"opp_{prediction.prediction_id}",
            opportunity_description=f"Leverage predicted positive trend: {prediction.prediction_text}",
            opportunity_type=OpportunityType.MARKET_EXPANSION,
            value_score=70.0,
            feasibility_score=prediction.confidence_score,
            priority_score=(70.0 * prediction.confidence_score) / 100,
            expected_benefits=["Capitalize on predicted growth"],
            recommended_actions=["Prepare for predicted scenario", "Align strategy with prediction"],
            time_to_execute=prediction.time_horizon,
            success_metrics=prediction.validation_metrics
        )

        return opportunity

    # ========================================================================
    # CLAUDE INTEGRATION - NATURAL LANGUAGE INSIGHTS
    # ========================================================================

    async def _generate_insights_with_llm(
        self,
        target: str,
        patterns: List[Pattern],
        predictions: List[Prediction],
        risks: List[Risk],
        opportunities: List[Opportunity],
        context: Dict[str, Any]
    ) -> List[Insight]:
        """
        Generate natural language insights using Claude AI.

        Falls back to rule-based insights if Claude unavailable.
        """
        if not self.claude_service or not is_claude_available():
            logger.warning("Claude unavailable, using fallback insight generation")
            return self._generate_insights_fallback(patterns, predictions, risks, opportunities)

        try:
            # Prepare context for Claude
            analysis_context = self._prepare_llm_context(target, patterns, predictions, risks, opportunities, context)

            # Call Claude with INSIGHT_GENERATION system prompt
            prompt = f"""Analyze the following business intelligence data and generate strategic insights:

Target: {target}

Patterns Detected ({len(patterns)}):
{self._format_patterns_for_llm(patterns)}

Predictions ({len(predictions)}):
{self._format_predictions_for_llm(predictions)}

Risks ({len(risks)}):
{self._format_risks_for_llm(risks)}

Opportunities ({len(opportunities)}):
{self._format_opportunities_for_llm(opportunities)}

Generate 3-5 strategic insights in JSON array format:
[
  {{
    "insight_type": "trend|prediction|risk|opportunity|strategic",
    "priority": "critical|high|medium|low",
    "insight_text": "Natural language insight (2-3 sentences)",
    "is_actionable": true|false,
    "recommended_actions": ["action 1", "action 2"]
  }}
]

Focus on:
1. Most important patterns and what they mean
2. Critical risks requiring immediate attention
3. High-value opportunities to pursue
4. Strategic recommendations based on the analysis
5. Actionable next steps
"""

            response = await self.claude_service.create_message(
                messages=[{"role": "user", "content": prompt}],
                system_prompt_type=SystemPromptType.MARKET_INTELLIGENCE,
                model=ClaudeModel.SONNET,
                max_tokens=2000
            )

            # Parse Claude response
            insights = self._parse_llm_insights(response, patterns, predictions, risks, opportunities)

            if insights:
                logger.info(f"Generated {len(insights)} insights with Claude AI")
                return insights
            else:
                logger.warning("Failed to parse Claude response, using fallback")
                return self._generate_insights_fallback(patterns, predictions, risks, opportunities)

        except Exception as e:
            logger.error(f"Error generating insights with Claude: {str(e)}")
            return self._generate_insights_fallback(patterns, predictions, risks, opportunities)

    def _prepare_llm_context(
        self,
        target: str,
        patterns: List[Pattern],
        predictions: List[Prediction],
        risks: List[Risk],
        opportunities: List[Opportunity],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare structured context for LLM"""
        return {
            "target": target,
            "patterns_count": len(patterns),
            "predictions_count": len(predictions),
            "risks_count": len(risks),
            "opportunities_count": len(opportunities),
            "has_financial_data": "financial_data" in context,
            "has_market_data": "market_data" in context,
            "has_competitor_data": "competitor_data" in context
        }

    def _format_patterns_for_llm(self, patterns: List[Pattern]) -> str:
        """Format patterns for LLM prompt"""
        if not patterns:
            return "No patterns detected"

        formatted = []
        for p in patterns[:5]:  # Limit to top 5
            formatted.append(f"- {p.pattern_description} (confidence: {p.confidence_score:.0f}%)")

        return "\n".join(formatted)

    def _format_predictions_for_llm(self, predictions: List[Prediction]) -> str:
        """Format predictions for LLM prompt"""
        if not predictions:
            return "No predictions generated"

        formatted = []
        for p in predictions[:5]:
            formatted.append(f"- {p.prediction_text} (confidence: {p.confidence_score:.0f}%)")

        return "\n".join(formatted)

    def _format_risks_for_llm(self, risks: List[Risk]) -> str:
        """Format risks for LLM prompt"""
        if not risks:
            return "No risks identified"

        formatted = []
        for r in sorted(risks, key=lambda x: x.risk_score, reverse=True)[:5]:
            formatted.append(f"- [{r.risk_level.value.upper()}] {r.risk_description} (score: {r.risk_score:.1f})")

        return "\n".join(formatted)

    def _format_opportunities_for_llm(self, opportunities: List[Opportunity]) -> str:
        """Format opportunities for LLM prompt"""
        if not opportunities:
            return "No opportunities identified"

        formatted = []
        for o in sorted(opportunities, key=lambda x: x.priority_score, reverse=True)[:5]:
            formatted.append(f"- {o.opportunity_description} (priority: {o.priority_score:.1f})")

        return "\n".join(formatted)

    def _parse_llm_insights(
        self,
        llm_response: str,
        patterns: List[Pattern],
        predictions: List[Prediction],
        risks: List[Risk],
        opportunities: List[Opportunity]
    ) -> List[Insight]:
        """Parse LLM response into Insight objects"""
        insights = []

        try:
            # Extract JSON from response
            json_match = re.search(r'\[[\s\S]*\]', llm_response)
            if not json_match:
                return []

            insights_data = json.loads(json_match.group(0))

            for idx, item in enumerate(insights_data):
                insight = Insight(
                    insight_id=f"insight_llm_{idx+1}",
                    insight_type=InsightType(item.get("insight_type", "strategic")),
                    insight_text=item["insight_text"],
                    priority=item.get("priority", "medium"),
                    relevance_score=85.0,  # High relevance for Claude-generated insights
                    is_actionable=item.get("is_actionable", True),
                    recommended_actions=item.get("recommended_actions", []),
                    patterns=patterns[:3],  # Link top patterns
                    predictions=predictions[:2],
                    risks=risks[:2],
                    opportunities=opportunities[:2]
                )
                insights.append(insight)

            return insights

        except Exception as e:
            logger.error(f"Failed to parse LLM insights: {str(e)}")
            return []

    def _generate_insights_fallback(
        self,
        patterns: List[Pattern],
        predictions: List[Prediction],
        risks: List[Risk],
        opportunities: List[Opportunity]
    ) -> List[Insight]:
        """Generate rule-based insights when Claude unavailable"""
        insights = []

        # Insight from top pattern
        if patterns:
            top_pattern = max(patterns, key=lambda p: p.confidence_score)
            insight = Insight(
                insight_id="insight_pattern_1",
                insight_type=InsightType.TREND,
                insight_text=f"{top_pattern.pattern_description}. This pattern is based on {top_pattern.data_points} data points with {top_pattern.confidence_score:.0f}% confidence.",
                priority="high" if top_pattern.confidence_score >= 75 else "medium",
                relevance_score=top_pattern.confidence_score,
                patterns=[top_pattern],
                is_actionable=True,
                recommended_actions=["Monitor this trend closely", "Investigate contributing factors"]
            )
            insights.append(insight)

        # Insight from top risk
        if risks:
            top_risk = max(risks, key=lambda r: r.risk_score)
            insight = Insight(
                insight_id="insight_risk_1",
                insight_type=InsightType.RISK,
                insight_text=f"{top_risk.risk_description}. Risk level: {top_risk.risk_level.value}. Immediate attention required to mitigate potential impact.",
                priority="critical" if top_risk.risk_level == RiskLevel.CRITICAL else "high",
                relevance_score=top_risk.impact_score,
                risks=[top_risk],
                is_actionable=True,
                recommended_actions=top_risk.mitigation_strategies
            )
            insights.append(insight)

        # Insight from top opportunity
        if opportunities:
            top_opp = max(opportunities, key=lambda o: o.priority_score)
            insight = Insight(
                insight_id="insight_opp_1",
                insight_type=InsightType.OPPORTUNITY,
                insight_text=f"{top_opp.opportunity_description}. Priority score: {top_opp.priority_score:.1f}. High potential value with feasible implementation.",
                priority="high",
                relevance_score=top_opp.value_score,
                opportunities=[top_opp],
                is_actionable=True,
                recommended_actions=top_opp.recommended_actions
            )
            insights.append(insight)

        return insights

    # ========================================================================
    # SUMMARY METHODS
    # ========================================================================

    def _calculate_overall_confidence(
        self,
        patterns: List[Pattern],
        predictions: List[Prediction]
    ) -> float:
        """Calculate overall analysis confidence score"""
        if not patterns and not predictions:
            return 0.0

        # Weighted average of pattern and prediction confidence
        pattern_conf = sum(p.confidence_score for p in patterns) / len(patterns) if patterns else 0
        pred_conf = sum(p.confidence_score for p in predictions) / len(predictions) if predictions else 0

        # Weight patterns higher (70%) than predictions (30%)
        overall = (pattern_conf * 0.7 + pred_conf * 0.3)

        return round(overall, 2)

    def _generate_recommendations(
        self,
        patterns: List[Pattern],
        predictions: List[Prediction],
        risks: List[Risk],
        opportunities: List[Opportunity]
    ) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []

        # Top 3 patterns
        top_patterns = sorted(patterns, key=lambda p: p.confidence_score, reverse=True)[:3]
        for pattern in top_patterns:
            recommendations.append(f"Monitor {pattern.affected_metrics[0].replace('_', ' ')} trend ({pattern.pattern_type})")

        # Top 3 risks
        top_risks = sorted(risks, key=lambda r: r.risk_score, reverse=True)[:3]
        for risk in top_risks:
            if risk.mitigation_strategies:
                recommendations.append(risk.mitigation_strategies[0])

        # Top 3 opportunities
        top_opps = sorted(opportunities, key=lambda o: o.priority_score, reverse=True)[:3]
        for opp in top_opps:
            if opp.recommended_actions:
                recommendations.append(opp.recommended_actions[0])

        return recommendations[:10]  # Limit to top 10

    def _prioritize_actions(
        self,
        risks: List[Risk],
        opportunities: List[Opportunity]
    ) -> List[str]:
        """Prioritize actions based on risks and opportunities"""
        actions = []

        # Critical risks first
        critical_risks = [r for r in risks if r.risk_level == RiskLevel.CRITICAL]
        for risk in critical_risks:
            if risk.mitigation_strategies:
                actions.append(f"URGENT: {risk.mitigation_strategies[0]}")

        # High-value opportunities
        top_opps = sorted(opportunities, key=lambda o: o.priority_score, reverse=True)[:3]
        for opp in top_opps:
            if opp.recommended_actions:
                actions.append(f"OPPORTUNITY: {opp.recommended_actions[0]}")

        # High risks
        high_risks = [r for r in risks if r.risk_level == RiskLevel.HIGH]
        for risk in high_risks[:2]:
            if risk.mitigation_strategies:
                actions.append(f"PRIORITY: {risk.mitigation_strategies[0]}")

        return actions[:8]  # Top 8 priority actions

    # ========================================================================
    # WEEK 17: ADVANCED ANALYSIS METHODS
    # ========================================================================

    def _detect_anomalies(
        self,
        values: List[float],
        metric_name: str
    ) -> Optional[Pattern]:
        """
        Detect anomalies in data using statistical methods (Week 17).

        Uses Z-score method to identify outliers.

        Args:
            values: List of numerical values
            metric_name: Name of the metric being analyzed

        Returns:
            Pattern if anomalies detected, None otherwise
        """
        if len(values) < 5:  # Need enough data points
            return None

        # Calculate mean and standard deviation
        mean_value = sum(values) / len(values)
        variance = sum((x - mean_value) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5

        if std_dev == 0:
            return None  # No variation

        # Calculate Z-scores
        z_scores = [(x - mean_value) / std_dev for x in values]

        # Identify anomalies (|Z| > 2.5)
        anomalies = [(i, val, z) for i, (val, z) in enumerate(zip(values, z_scores)) if abs(z) > 2.5]

        if not anomalies:
            return None

        # Create anomaly pattern
        anomaly_count = len(anomalies)
        anomaly_indices = [a[0] for a in anomalies]
        anomaly_values = [a[1] for a in anomalies]

        pattern = Pattern(
            pattern_id=f"anomaly_{metric_name}",
            pattern_type=PatternType.VOLATILE,
            pattern_description=f"Detected {anomaly_count} anomalies in {metric_name} (outliers beyond 2.5 standard deviations)",
            confidence_score=min(100, 60 + anomaly_count * 5),
            strength=min(100, max(abs(z) for _, _, z in anomalies) * 10),
            data_points=len(values),
            time_period="analysis_period",
            volatility_score=std_dev / mean_value * 100 if mean_value != 0 else 0,
            affected_metrics=[metric_name],
            contributing_factors=[
                f"{anomaly_count} outlier values detected",
                f"Values at positions: {', '.join(map(str, anomaly_indices[:5]))}",
                f"Standard deviation: {std_dev:.2f}"
            ]
        )

        return pattern

    def _analyze_correlations(
        self,
        data: Dict[str, List[float]]
    ) -> List[Insight]:
        """
        Analyze correlations between different metrics (Week 17).

        Uses Pearson correlation coefficient.

        Args:
            data: Dictionary mapping metric names to value lists

        Returns:
            List of correlation insights
        """
        insights = []

        if len(data) < 2:
            return insights

        # Get all metric pairs
        metrics = list(data.keys())

        for i in range(len(metrics)):
            for j in range(i + 1, len(metrics)):
                metric1 = metrics[i]
                metric2 = metrics[j]

                values1 = data[metric1]
                values2 = data[metric2]

                # Need same length and enough points
                if len(values1) != len(values2) or len(values1) < 3:
                    continue

                # Calculate Pearson correlation
                corr = self._calculate_correlation(values1, values2)

                if abs(corr) > 0.6:  # Significant correlation
                    correlation_strength = "strong" if abs(corr) > 0.8 else "moderate"
                    correlation_direction = "positive" if corr > 0 else "negative"

                    insight = Insight(
                        insight_id=f"correlation_{metric1}_{metric2}",
                        insight_type=InsightType.CORRELATION,
                        insight_text=f"Found {correlation_strength} {correlation_direction} correlation ({corr:.2f}) between {metric1.replace('_', ' ')} and {metric2.replace('_', ' ')}. Changes in one metric are associated with changes in the other.",
                        priority="medium" if abs(corr) > 0.8 else "low",
                        relevance_score=abs(corr) * 100,
                        is_actionable=True,
                        recommended_actions=[
                            f"Monitor both {metric1} and {metric2} together",
                            f"Consider causal relationship between metrics",
                            "Use correlation for predictive modeling"
                        ]
                    )
                    insights.append(insight)

        return insights

    def _calculate_correlation(
        self,
        x: List[float],
        y: List[float]
    ) -> float:
        """
        Calculate Pearson correlation coefficient.

        Args:
            x: First variable values
            y: Second variable values

        Returns:
            Correlation coefficient (-1 to 1)
        """
        n = len(x)
        if n == 0:
            return 0.0

        # Calculate means
        mean_x = sum(x) / n
        mean_y = sum(y) / n

        # Calculate covariance and standard deviations
        cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / n
        std_x = (sum((xi - mean_x) ** 2 for xi in x) / n) ** 0.5
        std_y = (sum((yi - mean_y) ** 2 for yi in y) / n) ** 0.5

        if std_x == 0 or std_y == 0:
            return 0.0

        return cov / (std_x * std_y)

    async def _generate_scenario_analysis(
        self,
        patterns: List[Pattern],
        predictions: List[Prediction]
    ) -> List[Insight]:
        """
        Generate scenario analysis: best case, worst case, most likely (Week 17).

        Args:
            patterns: Detected patterns
            predictions: Generated predictions

        Returns:
            List of scenario insights
        """
        scenarios = []

        # Best case scenario
        positive_patterns = [p for p in patterns if p.pattern_type == PatternType.GROWTH]
        positive_predictions = [p for p in predictions if "grow" in p.prediction_text.lower()]

        if positive_patterns or positive_predictions:
            best_case_score = (
                sum(p.confidence_score for p in positive_patterns[:3]) / max(len(positive_patterns[:3]), 1) * 0.6 +
                sum(p.confidence_score for p in positive_predictions[:2]) / max(len(positive_predictions[:2]), 1) * 0.4
            ) if positive_patterns or positive_predictions else 0

            best_case = Insight(
                insight_id="scenario_best_case",
                insight_type=InsightType.STRATEGIC,
                insight_text=f"BEST CASE SCENARIO: If positive trends continue and growth predictions materialize, the organization could see significant improvement across {len(positive_patterns)} key metrics. This scenario assumes favorable market conditions and successful execution of growth initiatives.",
                priority="medium",
                relevance_score=best_case_score,
                patterns=positive_patterns[:3],
                predictions=positive_predictions[:2],
                is_actionable=True,
                recommended_actions=[
                    "Capitalize on growth opportunities",
                    "Accelerate expansion plans",
                    "Invest in scaling capabilities"
                ]
            )
            scenarios.append(best_case)

        # Worst case scenario
        negative_patterns = [p for p in patterns if p.pattern_type == PatternType.DECLINE]
        negative_predictions = [p for p in predictions if "decline" in p.prediction_text.lower()]

        if negative_patterns or negative_predictions:
            worst_case_score = (
                sum(p.confidence_score for p in negative_patterns[:3]) / max(len(negative_patterns[:3]), 1) * 0.6 +
                sum(p.confidence_score for p in negative_predictions[:2]) / max(len(negative_predictions[:2]), 1) * 0.4
            ) if negative_patterns or negative_predictions else 0

            worst_case = Insight(
                insight_id="scenario_worst_case",
                insight_type=InsightType.RISK,
                insight_text=f"WORST CASE SCENARIO: If negative trends accelerate and predicted declines materialize, the organization could face challenges across {len(negative_patterns)} key areas. This scenario requires contingency planning and risk mitigation strategies.",
                priority="high",
                relevance_score=worst_case_score,
                patterns=negative_patterns[:3],
                predictions=negative_predictions[:2],
                is_actionable=True,
                recommended_actions=[
                    "Develop contingency plans",
                    "Implement risk mitigation strategies",
                    "Build financial reserves",
                    "Prepare corrective actions"
                ]
            )
            scenarios.append(worst_case)

        # Most likely scenario
        all_patterns_avg_confidence = sum(p.confidence_score for p in patterns) / len(patterns) if patterns else 0
        all_predictions_avg_confidence = sum(p.confidence_score for p in predictions) / len(predictions) if predictions else 0

        if patterns or predictions:
            most_likely = Insight(
                insight_id="scenario_most_likely",
                insight_type=InsightType.STRATEGIC,
                insight_text=f"MOST LIKELY SCENARIO: Based on current trends and evidence, expect moderate changes with {len(patterns)} patterns continuing and {len(predictions)} predictions partially materializing. This balanced scenario assumes stable market conditions with some variability.",
                priority="high",
                relevance_score=(all_patterns_avg_confidence + all_predictions_avg_confidence) / 2,
                patterns=patterns[:5],
                predictions=predictions[:3],
                is_actionable=True,
                recommended_actions=[
                    "Balance growth and risk management",
                    "Monitor key indicators closely",
                    "Stay flexible and adaptive",
                    "Execute strategic plan with contingencies"
                ]
            )
            scenarios.append(most_likely)

        return scenarios

    def _advanced_forecast(
        self,
        values: List[float],
        metric_name: str,
        periods_ahead: int = 3
    ) -> Optional[Prediction]:
        """
        Generate advanced forecast using exponential smoothing (Week 17).

        Args:
            values: Historical values
            metric_name: Name of metric
            periods_ahead: Number of periods to forecast

        Returns:
            Prediction with forecast
        """
        if len(values) < 5:
            return None

        # Simple exponential smoothing with alpha = 0.3
        alpha = 0.3
        smoothed = [values[0]]

        for i in range(1, len(values)):
            smoothed_value = alpha * values[i] + (1 - alpha) * smoothed[i-1]
            smoothed.append(smoothed_value)

        # Forecast next periods
        forecast_value = smoothed[-1]

        # Calculate trend from last few points
        if len(values) >= 3:
            recent_trend = (values[-1] - values[-3]) / 2
        else:
            recent_trend = 0

        # Adjust forecast with trend
        forecast_value = forecast_value + (recent_trend * periods_ahead)

        # Calculate percentage change
        pct_change = ((forecast_value - values[-1]) / values[-1] * 100) if values[-1] != 0 else 0

        # Determine confidence based on smoothness
        variance = sum((values[i] - smoothed[i]) ** 2 for i in range(len(values))) / len(values)
        smoothness_score = max(0, 100 - (variance ** 0.5 / (sum(values) / len(values)) * 100)) if sum(values) != 0 else 50

        prediction = Prediction(
            prediction_id=f"forecast_{metric_name}_{periods_ahead}p",
            prediction_text=f"Advanced forecast for {metric_name.replace('_', ' ')}: predicted {pct_change:+.1f}% change over next {periods_ahead} periods using exponential smoothing",
            predicted_value=f"{forecast_value:.2f} ({pct_change:+.1f}%)",
            prediction_confidence=PredictionConfidence.MEDIUM if smoothness_score > 60 else PredictionConfidence.LOW,
            confidence_score=smoothness_score,
            time_horizon="short_term" if periods_ahead <= 3 else "medium_term",
            supporting_factors=[
                f"Based on exponential smoothing of {len(values)} historical values",
                f"Smoothness score: {smoothness_score:.1f}%",
                f"Recent trend: {recent_trend:+.2f} per period"
            ],
            risk_factors=[
                "Assumes trend continuation",
                "External factors may change",
                f"Forecast accuracy decreases with longer horizons"
            ],
            validation_metrics=[metric_name]
        )

        return prediction
