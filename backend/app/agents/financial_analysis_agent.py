"""
Financial Analysis Agent

Autonomous agent for financial statement analysis and ratio calculation.
Integrates KRS financial data for comprehensive financial health assessment.

Week 4 Implementation: Foundation agent for financial intelligence.

Use case: "Analyze financial health of company with KRS 0000123456"
         "Calculate financial ratios for company with NIP 1234567890"
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.services.agent_tools import ToolRegistry, get_tool_registry

# Import KRS client for financial data
try:
    from app.integrations.krs_client import KRSClient
    KRS_AVAILABLE = True
except ImportError:
    KRS_AVAILABLE = False

# Import GUS client for industry benchmarking (Week 5)
try:
    from app.integrations.gus_client import GUSClient
    GUS_AVAILABLE = True
except ImportError:
    GUS_AVAILABLE = False

logger = logging.getLogger(__name__)


# ============================================================================
# OUTPUT SCHEMA - PYDANTIC MODELS
# ============================================================================

class FinancialStatement(BaseModel):
    """Single financial statement for a specific period (Week 5 updated for Z-score)"""
    period: str = Field(..., description="Financial period (e.g., '2023', '2023-Q1')")
    period_type: str = Field(..., pattern="^(annual|quarterly)$")

    # Balance Sheet
    total_assets: Optional[float] = Field(None, description="Total assets in PLN")
    current_assets: Optional[float] = Field(None, description="Current assets in PLN")
    fixed_assets: Optional[float] = Field(None, description="Fixed assets in PLN")
    total_liabilities: Optional[float] = Field(None, description="Total liabilities in PLN")
    current_liabilities: Optional[float] = Field(None, description="Current liabilities in PLN")
    long_term_liabilities: Optional[float] = Field(None, description="Long-term liabilities in PLN")
    equity: Optional[float] = Field(None, description="Shareholders' equity in PLN")
    retained_earnings: Optional[float] = Field(None, description="Retained earnings in PLN (for Z-score)")

    # Income Statement
    revenue: Optional[float] = Field(None, description="Total revenue in PLN")
    operating_profit: Optional[float] = Field(None, description="Operating profit in PLN")
    ebit: Optional[float] = Field(None, description="EBIT (Earnings Before Interest and Tax) in PLN (for Z-score)")
    net_profit: Optional[float] = Field(None, description="Net profit in PLN")
    cost_of_sales: Optional[float] = Field(None, description="Cost of goods sold in PLN")
    operating_expenses: Optional[float] = Field(None, description="Operating expenses in PLN")

    # Additional fields (Week 5)
    employee_count: Optional[int] = Field(None, description="Number of employees (for benchmarking)")

    # Cash Flow (if available)
    operating_cash_flow: Optional[float] = Field(None, description="Operating cash flow in PLN")
    investing_cash_flow: Optional[float] = Field(None, description="Investing cash flow in PLN")
    financing_cash_flow: Optional[float] = Field(None, description="Financing cash flow in PLN")

    class Config:
        json_schema_extra = {
            "example": {
                "period": "2023",
                "period_type": "annual",
                "total_assets": 5000000.0,
                "current_assets": 2000000.0,
                "revenue": 10000000.0,
                "net_profit": 500000.0
            }
        }


class LiquidityRatios(BaseModel):
    """Liquidity ratios - ability to meet short-term obligations"""
    current_ratio: Optional[float] = Field(None, description="Current Assets / Current Liabilities")
    quick_ratio: Optional[float] = Field(None, description="(Current Assets - Inventory) / Current Liabilities")
    cash_ratio: Optional[float] = Field(None, description="Cash / Current Liabilities")

    # Interpretation thresholds
    current_ratio_status: Optional[str] = Field(None, description="healthy|warning|critical")
    quick_ratio_status: Optional[str] = Field(None, description="healthy|warning|critical")


class ProfitabilityRatios(BaseModel):
    """Profitability ratios - ability to generate profit"""
    gross_margin: Optional[float] = Field(None, description="(Revenue - COGS) / Revenue * 100")
    operating_margin: Optional[float] = Field(None, description="Operating Profit / Revenue * 100")
    net_margin: Optional[float] = Field(None, description="Net Profit / Revenue * 100")
    return_on_assets: Optional[float] = Field(None, description="Net Profit / Total Assets * 100")
    return_on_equity: Optional[float] = Field(None, description="Net Profit / Equity * 100")

    # Interpretation
    profitability_status: Optional[str] = Field(None, description="excellent|good|average|poor")


class LeverageRatios(BaseModel):
    """Leverage ratios - debt and financial risk"""
    debt_to_equity: Optional[float] = Field(None, description="Total Liabilities / Equity")
    debt_to_assets: Optional[float] = Field(None, description="Total Liabilities / Total Assets")
    equity_ratio: Optional[float] = Field(None, description="Equity / Total Assets")
    interest_coverage: Optional[float] = Field(None, description="EBIT / Interest Expense")

    # Interpretation
    leverage_status: Optional[str] = Field(None, description="conservative|moderate|aggressive|overleveraged")


class EfficiencyRatios(BaseModel):
    """Efficiency ratios - asset utilization"""
    asset_turnover: Optional[float] = Field(None, description="Revenue / Total Assets")
    fixed_asset_turnover: Optional[float] = Field(None, description="Revenue / Fixed Assets")
    equity_turnover: Optional[float] = Field(None, description="Revenue / Equity")

    # Interpretation
    efficiency_status: Optional[str] = Field(None, description="excellent|good|average|poor")


class CashFlowRatios(BaseModel):
    """Cash flow ratios - cash generation and management (Week 5)"""
    operating_cash_flow_ratio: Optional[float] = Field(None, description="Operating CF / Current Liabilities")
    free_cash_flow: Optional[float] = Field(None, description="Operating CF - CapEx")
    cash_flow_margin: Optional[float] = Field(None, description="Operating CF / Revenue * 100")
    cash_flow_to_debt: Optional[float] = Field(None, description="Operating CF / Total Debt")
    cash_conversion_cycle: Optional[float] = Field(None, description="Days (DSO + DIO - DPO)")

    # Interpretation
    cash_flow_status: Optional[str] = Field(None, description="excellent|good|average|poor")


class RatioAnalysis(BaseModel):
    """Comprehensive ratio analysis"""
    period: str = Field(..., description="Period for this ratio analysis")

    liquidity: Optional[LiquidityRatios] = None
    profitability: Optional[ProfitabilityRatios] = None
    leverage: Optional[LeverageRatios] = None
    efficiency: Optional[EfficiencyRatios] = None
    cash_flow: Optional[CashFlowRatios] = None  # Week 5 addition

    overall_score: float = Field(..., ge=0, le=100, description="Overall financial health score")

    class Config:
        json_schema_extra = {
            "example": {
                "period": "2023",
                "overall_score": 75.0,
                "liquidity": {
                    "current_ratio": 2.5,
                    "current_ratio_status": "healthy"
                }
            }
        }


class TrendPoint(BaseModel):
    """Single data point in a trend"""
    period: str
    value: float
    change_percentage: Optional[float] = Field(None, description="% change from previous period")


class TrendAnalysis(BaseModel):
    """Trend analysis for key metrics (Week 5 updated with QoQ and seasonality)"""
    metric_name: str = Field(..., description="Name of the metric being analyzed")
    periods: List[TrendPoint] = Field(default_factory=list)

    # Trend characteristics
    trend_direction: str = Field(..., pattern="^(increasing|decreasing|stable|volatile)$")
    avg_growth_rate: Optional[float] = Field(None, description="Average YoY growth rate (%)")
    volatility: Optional[float] = Field(None, description="Standard deviation of changes")

    # Advanced trend analysis (Week 5)
    qoq_growth_rate: Optional[float] = Field(None, description="Quarter-over-Quarter growth rate (%)")
    seasonality_detected: Optional[bool] = Field(None, description="Whether seasonal patterns detected")
    seasonality_strength: Optional[float] = Field(None, description="Seasonality strength score (0-100)")

    # Interpretation
    trend_status: str = Field(..., pattern="^(positive|neutral|negative|concerning)$")

    class Config:
        json_schema_extra = {
            "example": {
                "metric_name": "revenue",
                "trend_direction": "increasing",
                "avg_growth_rate": 15.5,
                "qoq_growth_rate": 3.2,
                "seasonality_detected": True,
                "trend_status": "positive",
                "periods": [
                    {"period": "2021", "value": 8000000.0},
                    {"period": "2022", "value": 9200000.0, "change_percentage": 15.0},
                    {"period": "2023", "value": 10500000.0, "change_percentage": 14.1}
                ]
            }
        }


class FinancialHealthScore(BaseModel):
    """Overall financial health assessment (Week 5 updated with Altman Z-score)"""
    overall_score: float = Field(..., ge=0, le=100)

    # Component scores
    liquidity_score: float = Field(..., ge=0, le=100)
    profitability_score: float = Field(..., ge=0, le=100)
    leverage_score: float = Field(..., ge=0, le=100)
    efficiency_score: float = Field(..., ge=0, le=100)
    trend_score: float = Field(..., ge=0, le=100)

    # Advanced scoring (Week 5)
    altman_z_score: Optional[float] = Field(None, description="Altman Z-Score for bankruptcy prediction")
    bankruptcy_risk: Optional[str] = Field(
        None, 
        description="safe|grey_zone|distress (based on Z-score)"
    )

    # Risk assessment
    risk_level: str = Field(..., pattern="^(low|moderate|high|critical)$")

    # Key strengths and weaknesses
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "overall_score": 75.0,
                "liquidity_score": 80.0,
                "profitability_score": 70.0,
                "altman_z_score": 2.8,
                "bankruptcy_risk": "safe",
                "risk_level": "moderate",
                "strengths": ["Strong liquidity position", "Consistent revenue growth"],
                "weaknesses": ["High debt levels", "Declining profit margins"]
            }
        }



class IndustryBenchmark(BaseModel):
    """Industry benchmarking data (Week 5)"""
    pkd_code: Optional[str] = Field(None, description="PKD industry code")
    industry_name: Optional[str] = Field(None, description="Industry sector name")
    year: Optional[int] = Field(None, description="Benchmark year")
    
    # Company vs Industry Comparison
    revenue_percentile: Optional[float] = Field(None, description="Revenue percentile ranking (0-100)")
    employee_percentile: Optional[float] = Field(None, description="Employee count percentile (0-100)")
    profit_margin_vs_avg: Optional[float] = Field(None, description="Profit margin vs industry average (percentage points)")
    
    # Industry Averages
    industry_avg_revenue: Optional[float] = Field(None, description="Industry average revenue")
    industry_avg_employees: Optional[int] = Field(None, description="Industry average employee count")
    industry_avg_profit_margin: Optional[float] = Field(None, description="Industry average profit margin %")
    industry_growth_rate: Optional[float] = Field(None, description="Industry growth rate %")
    
    # Performance Assessment
    competitive_position: Optional[str] = Field(
        None, 
        description="above_average|average|below_average"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "pkd_code": "62.01.Z",
                "industry_name": "Software development",
                "revenue_percentile": 75.0,
                "competitive_position": "above_average"
            }
        }

class FinancialAnalysisOutput(BaseModel):
    """Structured output for FinancialAnalysisAgent (Week 5 updated with benchmarking)"""
    agent_type: str = "financial_analysis"
    target: str = Field(..., description="Target identifier (KRS, NIP, company name)")

    # Core financial data
    company_name: Optional[str] = None
    nip_number: Optional[str] = None
    krs_number: Optional[str] = None

    # Financial statements (multi-period)
    financial_statements: List[FinancialStatement] = Field(default_factory=list)

    # Analysis results
    ratio_analysis: List[RatioAnalysis] = Field(default_factory=list)
    trend_analysis: List[TrendAnalysis] = Field(default_factory=list)
    health_score: Optional[FinancialHealthScore] = None
    industry_benchmark: Optional[IndustryBenchmark] = None  # Week 5 addition

    # Agent metadata
    confidence_score: float = Field(..., ge=0, le=100)
    data_sources: List[str] = Field(default_factory=list)
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    periods_analyzed: int = Field(0, description="Number of financial periods analyzed")

    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "financial_analysis",
                "target": "KRS 0000123456",
                "company_name": "Example Sp. z o.o.",
                "confidence_score": 85.0,
                "periods_analyzed": 3,
                "health_score": {
                    "overall_score": 75.0,
                    "risk_level": "moderate"
                }
            }
        }


# ============================================================================
# AGENT CLASS
# ============================================================================

class FinancialAnalysisAgent:
    """
    Autonomous Financial Analysis Agent

    Capabilities:
    - Financial statement parsing from KRS data
    - Ratio calculation (liquidity, profitability, leverage, efficiency)
    - Trend analysis across multiple periods
    - Financial health scoring (0-100)
    - Risk assessment and recommendations

    Data Sources:
    - KRS (Court Registration) - financial reports
    - GUS (Statistical Office) - industry benchmarks (future)
    """

    def __init__(self, tool_registry: Optional[ToolRegistry] = None):
        """
        Initialize Financial Analysis Agent

        Args:
            tool_registry: Optional tool registry for external integrations
        """
        self.tool_registry = tool_registry or get_tool_registry()
        self.logger = logging.getLogger(__name__)

    async def execute(self, target: str) -> FinancialAnalysisOutput:
        """
        Execute financial analysis for target company (Week 5 updated with benchmarking)

        Args:
            target: Company identifier (KRS, NIP, or company name)

        Returns:
            FinancialAnalysisOutput with comprehensive financial analysis
        """
        self.logger.info(f"Starting financial analysis for target: {target}")

        try:
            # Step 1: Fetch financial statements
            statements = await self._fetch_financial_statements(target)

            # Step 2: Calculate ratios for each period
            ratio_analyses = self._calculate_ratios(statements)

            # Step 3: Perform trend analysis
            trends = self._analyze_trends(statements, ratio_analyses)

            # Step 4: Calculate financial health score (Week 5 updated with Z-score)
            health_score = self._calculate_health_score(ratio_analyses, trends, statements)

            # Step 5: Calculate industry benchmarks (Week 5)
            industry_benchmark = await self._calculate_industry_benchmarks(
                target, statements, ratio_analyses
            )

            # Step 6: Determine confidence score
            confidence = self._calculate_confidence(statements, ratio_analyses)

            # Build data sources list
            data_sources = ["KRS"]
            if industry_benchmark:
                data_sources.append("GUS")

            # Build output
            output = FinancialAnalysisOutput(
                target=target,
                financial_statements=statements,
                ratio_analysis=ratio_analyses,
                trend_analysis=trends,
                health_score=health_score,
                industry_benchmark=industry_benchmark,  # Week 5 addition
                confidence_score=confidence,
                data_sources=data_sources,
                periods_analyzed=len(statements)
            )

            self.logger.info(f"Financial analysis complete. Confidence: {confidence:.1f}%")
            return output

        except Exception as e:
            self.logger.error(f"Error in financial analysis: {e}", exc_info=True)

            # Return error output
            return FinancialAnalysisOutput(
                target=target,
                confidence_score=0.0,
                errors=[f"Financial analysis failed: {str(e)}"]
            )

    async def _fetch_financial_statements(self, target: str) -> List[FinancialStatement]:
        """
        Fetch financial statements from KRS

        Args:
            target: Company identifier (KRS number, NIP, or company name)

        Returns:
            List of financial statements (multi-period, up to 3 years)
        """
        if not KRS_AVAILABLE:
            self.logger.warning("KRS client not available")
            return []

        try:
            # Extract KRS number from target
            krs_number = self._extract_krs_number(target)
            if not krs_number:
                self.logger.warning(f"Could not extract KRS number from target: {target}")
                return []

            # Fetch financial data from KRS (3 years)
            krs_client = KRSClient()
            try:
                financial_data = await krs_client.get_financial_data(krs_number, years=3)
            finally:
                await krs_client.close()

            if not financial_data:
                self.logger.info(f"No financial data available for KRS: {krs_number}")
                return []

            # Convert KRS data to FinancialStatement objects
            statements = []
            for krs_report in financial_data:
                statement = self._convert_krs_to_statement(krs_report)
                if statement:
                    statements.append(statement)

            self.logger.info(f"Fetched {len(statements)} financial statements for KRS: {krs_number}")
            return statements

        except Exception as e:
            self.logger.error(f"Error fetching financial statements: {str(e)}", exc_info=True)
            return []

    def _extract_krs_number(self, target: str) -> Optional[str]:
        """
        Extract KRS number from target string.

        Args:
            target: Target string (may contain "KRS 0000123456" or just "0000123456")

        Returns:
            KRS number or None
        """
        import re

        # Try to find KRS pattern in string
        # Match patterns like "KRS 0000123456", "KRS: 0000123456", or just "0000123456"
        patterns = [
            r'KRS[\s:]*(\d{5,10})',  # "KRS 0000123456" or "KRS: 0000123456"
            r'^(\d{10})$',  # Just "0000123456"
        ]

        for pattern in patterns:
            match = re.search(pattern, target, re.IGNORECASE)
            if match:
                return match.group(1).zfill(10)  # Pad to 10 digits

        return None

    def _convert_krs_to_statement(self, krs_data: Dict[str, Any]) -> Optional[FinancialStatement]:
        """
        Convert KRS financial data to FinancialStatement object.

        Args:
            krs_data: Financial data from KRS API

        Returns:
            FinancialStatement object or None
        """
        try:
            balance_sheet = krs_data.get("balance_sheet", {})
            income_statement = krs_data.get("income_statement", {})
            cash_flow = krs_data.get("cash_flow", {})

            statement = FinancialStatement(
                period=krs_data.get("period", "unknown"),
                period_type=krs_data.get("period_type", "annual"),

                # Balance Sheet
                total_assets=balance_sheet.get("total_assets"),
                current_assets=balance_sheet.get("current_assets"),
                fixed_assets=balance_sheet.get("fixed_assets"),
                total_liabilities=balance_sheet.get("total_liabilities"),
                current_liabilities=balance_sheet.get("current_liabilities"),
                long_term_liabilities=balance_sheet.get("long_term_liabilities"),
                equity=balance_sheet.get("equity"),

                # Income Statement
                revenue=income_statement.get("revenue"),
                operating_profit=income_statement.get("operating_profit"),
                net_profit=income_statement.get("net_profit"),
                cost_of_sales=income_statement.get("cost_of_sales"),
                operating_expenses=income_statement.get("operating_expenses"),

                # Cash Flow
                operating_cash_flow=cash_flow.get("operating_cash_flow"),
                investing_cash_flow=cash_flow.get("investing_cash_flow"),
                financing_cash_flow=cash_flow.get("financing_cash_flow")
            )

            return statement

        except Exception as e:
            self.logger.error(f"Error converting KRS data to statement: {str(e)}")
            return None

    def _calculate_ratios(self, statements: List[FinancialStatement]) -> List[RatioAnalysis]:
        """
        Calculate financial ratios for each period

        Args:
            statements: List of financial statements

        Returns:
            List of ratio analyses, one per period
        """
        ratio_analyses = []

        for statement in statements:
            # Liquidity ratios
            liquidity = self._calculate_liquidity_ratios(statement)

            # Profitability ratios
            profitability = self._calculate_profitability_ratios(statement)

            # Leverage ratios
            leverage = self._calculate_leverage_ratios(statement)

            # Efficiency ratios
            efficiency = self._calculate_efficiency_ratios(statement)

            # Cash flow ratios (Week 5)
            cash_flow = self._calculate_cash_flow_ratios(statement)

            # Overall score for this period
            overall_score = self._calculate_period_score(
                liquidity, profitability, leverage, efficiency, cash_flow
            )

            ratio_analysis = RatioAnalysis(
                period=statement.period,
                liquidity=liquidity,
                profitability=profitability,
                leverage=leverage,
                efficiency=efficiency,
                cash_flow=cash_flow,
                overall_score=overall_score
            )

            ratio_analyses.append(ratio_analysis)

        return ratio_analyses

    def _calculate_liquidity_ratios(self, statement: FinancialStatement) -> Optional[LiquidityRatios]:
        """Calculate liquidity ratios from financial statement"""
        if not statement.current_assets or not statement.current_liabilities:
            return None

        # Current Ratio = Current Assets / Current Liabilities
        current_ratio = statement.current_assets / statement.current_liabilities if statement.current_liabilities > 0 else None

        # Quick Ratio = (Current Assets - Inventory) / Current Liabilities
        # Note: For now, assuming inventory is 30% of current assets (will be refined)
        quick_assets = statement.current_assets * 0.7  # Approximation
        quick_ratio = quick_assets / statement.current_liabilities if statement.current_liabilities > 0 else None

        # Cash Ratio - placeholder (requires cash data from KRS)
        cash_ratio = None

        # Determine status
        current_ratio_status = self._assess_current_ratio(current_ratio)
        quick_ratio_status = self._assess_quick_ratio(quick_ratio)

        return LiquidityRatios(
            current_ratio=round(current_ratio, 2) if current_ratio else None,
            quick_ratio=round(quick_ratio, 2) if quick_ratio else None,
            cash_ratio=cash_ratio,
            current_ratio_status=current_ratio_status,
            quick_ratio_status=quick_ratio_status
        )

    def _calculate_profitability_ratios(self, statement: FinancialStatement) -> Optional[ProfitabilityRatios]:
        """Calculate profitability ratios from financial statement"""
        if not statement.revenue:
            return None

        # Gross Margin = (Revenue - COGS) / Revenue * 100
        gross_margin = None
        if statement.cost_of_sales:
            gross_margin = ((statement.revenue - statement.cost_of_sales) / statement.revenue * 100)

        # Operating Margin = Operating Profit / Revenue * 100
        operating_margin = None
        if statement.operating_profit:
            operating_margin = (statement.operating_profit / statement.revenue * 100)

        # Net Margin = Net Profit / Revenue * 100
        net_margin = None
        if statement.net_profit:
            net_margin = (statement.net_profit / statement.revenue * 100)

        # ROA = Net Profit / Total Assets * 100
        roa = None
        if statement.net_profit and statement.total_assets and statement.total_assets > 0:
            roa = (statement.net_profit / statement.total_assets * 100)

        # ROE = Net Profit / Equity * 100
        roe = None
        if statement.net_profit and statement.equity and statement.equity > 0:
            roe = (statement.net_profit / statement.equity * 100)

        # Determine overall profitability status
        profitability_status = self._assess_profitability(net_margin, roa, roe)

        return ProfitabilityRatios(
            gross_margin=round(gross_margin, 2) if gross_margin else None,
            operating_margin=round(operating_margin, 2) if operating_margin else None,
            net_margin=round(net_margin, 2) if net_margin else None,
            return_on_assets=round(roa, 2) if roa else None,
            return_on_equity=round(roe, 2) if roe else None,
            profitability_status=profitability_status
        )

    def _calculate_leverage_ratios(self, statement: FinancialStatement) -> Optional[LeverageRatios]:
        """Calculate leverage ratios from financial statement"""
        if not statement.total_liabilities or not statement.equity:
            return None

        # Debt-to-Equity = Total Liabilities / Equity
        debt_to_equity = None
        if statement.equity > 0:
            debt_to_equity = statement.total_liabilities / statement.equity

        # Debt-to-Assets = Total Liabilities / Total Assets
        debt_to_assets = None
        if statement.total_assets and statement.total_assets > 0:
            debt_to_assets = statement.total_liabilities / statement.total_assets

        # Equity Ratio = Equity / Total Assets
        equity_ratio = None
        if statement.total_assets and statement.total_assets > 0:
            equity_ratio = statement.equity / statement.total_assets

        # Interest Coverage - placeholder (requires interest expense data)
        interest_coverage = None

        # Determine leverage status
        leverage_status = self._assess_leverage(debt_to_equity, debt_to_assets)

        return LeverageRatios(
            debt_to_equity=round(debt_to_equity, 2) if debt_to_equity else None,
            debt_to_assets=round(debt_to_assets, 2) if debt_to_assets else None,
            equity_ratio=round(equity_ratio, 2) if equity_ratio else None,
            interest_coverage=interest_coverage,
            leverage_status=leverage_status
        )

    def _calculate_efficiency_ratios(self, statement: FinancialStatement) -> Optional[EfficiencyRatios]:
        """Calculate efficiency ratios from financial statement"""
        if not statement.revenue:
            return None

        # Asset Turnover = Revenue / Total Assets
        asset_turnover = None
        if statement.total_assets and statement.total_assets > 0:
            asset_turnover = statement.revenue / statement.total_assets

        # Fixed Asset Turnover = Revenue / Fixed Assets
        fixed_asset_turnover = None
        if statement.fixed_assets and statement.fixed_assets > 0:
            fixed_asset_turnover = statement.revenue / statement.fixed_assets

        # Equity Turnover = Revenue / Equity
        equity_turnover = None
        if statement.equity and statement.equity > 0:
            equity_turnover = statement.revenue / statement.equity

        # Determine efficiency status
        efficiency_status = self._assess_efficiency(asset_turnover)

        return EfficiencyRatios(
            asset_turnover=round(asset_turnover, 2) if asset_turnover else None,
            fixed_asset_turnover=round(fixed_asset_turnover, 2) if fixed_asset_turnover else None,
            equity_turnover=round(equity_turnover, 2) if equity_turnover else None,
            efficiency_status=efficiency_status
        )

    def _calculate_cash_flow_ratios(self, statement: FinancialStatement) -> Optional[CashFlowRatios]:
        """
        Calculate cash flow ratios from financial statement (Week 5)

        Args:
            statement: Financial statement with cash flow data

        Returns:
            Cash flow ratios or None if data missing
        """
        if not statement.operating_cash_flow:
            return None

        # Operating Cash Flow Ratio = Operating CF / Current Liabilities
        ocf_ratio = None
        if statement.current_liabilities and statement.current_liabilities > 0:
            ocf_ratio = statement.operating_cash_flow / statement.current_liabilities

        # Free Cash Flow = Operating CF - CapEx
        # Note: CapEx approximated as investing cash flow (negative)
        free_cf = None
        if statement.investing_cash_flow is not None:
            # Investing CF is usually negative for CapEx
            # Free CF = Operating CF - CapEx = Operating CF - abs(Investing CF)
            free_cf = statement.operating_cash_flow - abs(statement.investing_cash_flow)

        # Cash Flow Margin = Operating CF / Revenue * 100
        cf_margin = None
        if statement.revenue and statement.revenue > 0:
            cf_margin = (statement.operating_cash_flow / statement.revenue) * 100

        # Cash Flow to Debt = Operating CF / Total Debt
        cf_to_debt = None
        if statement.total_liabilities and statement.total_liabilities > 0:
            cf_to_debt = statement.operating_cash_flow / statement.total_liabilities

        # Cash Conversion Cycle (placeholder - requires detailed data)
        cash_conversion_cycle = None

        # Assess cash flow health
        cf_status = self._assess_cash_flow(ocf_ratio, cf_margin, cf_to_debt)

        return CashFlowRatios(
            operating_cash_flow_ratio=round(ocf_ratio, 2) if ocf_ratio else None,
            free_cash_flow=round(free_cf, 2) if free_cf else None,
            cash_flow_margin=round(cf_margin, 2) if cf_margin else None,
            cash_flow_to_debt=round(cf_to_debt, 2) if cf_to_debt else None,
            cash_conversion_cycle=cash_conversion_cycle,
            cash_flow_status=cf_status
        )

    def _calculate_period_score(
        self,
        liquidity: Optional[LiquidityRatios],
        profitability: Optional[ProfitabilityRatios],
        leverage: Optional[LeverageRatios],
        efficiency: Optional[EfficiencyRatios],
        cash_flow: Optional[CashFlowRatios] = None
    ) -> float:
        """
        Calculate overall score for a single period

        Weighted scoring (Week 5 updated):
        - Profitability: 30%
        - Leverage: 20%
        - Liquidity: 20%
        - Cash Flow: 20% (Week 5 addition)
        - Efficiency: 10%
        """
        total_score = 0.0
        total_weight = 0.0

        # Profitability score (30%)
        if profitability:
            profitability_score = self._score_profitability(profitability)
            total_score += profitability_score * 0.30
            total_weight += 0.30

        # Leverage score (20%)
        if leverage:
            leverage_score = self._score_leverage(leverage)
            total_score += leverage_score * 0.20
            total_weight += 0.20

        # Liquidity score (20%)
        if liquidity and liquidity.current_ratio:
            liquidity_score = self._score_liquidity(liquidity)
            total_score += liquidity_score * 0.20
            total_weight += 0.20

        # Cash Flow score (20%) - Week 5
        if cash_flow and cash_flow.operating_cash_flow_ratio:
            cf_score = self._score_cash_flow(cash_flow)
            total_score += cf_score * 0.20
            total_weight += 0.20

        # Efficiency score (10%)
        if efficiency and efficiency.asset_turnover:
            efficiency_score = self._score_efficiency(efficiency)
            total_score += efficiency_score * 0.10
            total_weight += 0.10

        # Normalize if not all components available
        if total_weight > 0:
            return round(total_score / total_weight, 1)
        return 0.0

    def _analyze_trends(
        self,
        statements: List[FinancialStatement],
        ratio_analyses: List[RatioAnalysis]
    ) -> List[TrendAnalysis]:
        """
        Analyze trends across multiple periods (Week 5 updated with QoQ and seasonality)

        Key metrics:
        - Revenue growth (YoY, QoQ)
        - Profit margin trend
        - Liquidity trend
        - Leverage trend
        - Seasonality detection
        """
        trends = []

        if len(statements) < 2:
            return trends  # Need at least 2 periods for trend analysis

        # Revenue trend
        revenue_trend = self._create_trend_analysis(
            metric_name="revenue",
            data_points=[(s.period, s.revenue) for s in statements if s.revenue],
            period_types=[s.period_type for s in statements if s.revenue]
        )
        if revenue_trend:
            trends.append(revenue_trend)

        # Net profit trend
        profit_trend = self._create_trend_analysis(
            metric_name="net_profit",
            data_points=[(s.period, s.net_profit) for s in statements if s.net_profit],
            period_types=[s.period_type for s in statements if s.net_profit]
        )
        if profit_trend:
            trends.append(profit_trend)

        # Current ratio trend
        current_ratio_trend = self._create_trend_analysis(
            metric_name="current_ratio",
            data_points=[
                (ra.period, ra.liquidity.current_ratio)
                for ra in ratio_analyses
                if ra.liquidity and ra.liquidity.current_ratio
            ],
            period_types=[
                ra.period.split('-')[0] if '-' in ra.period else "annual"
                for ra in ratio_analyses
                if ra.liquidity and ra.liquidity.current_ratio
            ]
        )
        if current_ratio_trend:
            trends.append(current_ratio_trend)

        return trends

    def _create_trend_analysis(
        self,
        metric_name: str,
        data_points: List[tuple],
        period_types: Optional[List[str]] = None
    ) -> Optional[TrendAnalysis]:
        """
        Create trend analysis from data points (Week 5 updated with QoQ and seasonality)
        
        Args:
            metric_name: Name of metric
            data_points: List of (period, value) tuples
            period_types: List of period types ("annual" or "quarterly")
        """
        if len(data_points) < 2:
            return None

        # Sort by period
        sorted_points = sorted(data_points, key=lambda x: x[0])

        # Create trend points with change percentages
        trend_points = []
        previous_value = None

        for period, value in sorted_points:
            change_pct = None
            if previous_value is not None and previous_value != 0:
                change_pct = ((value - previous_value) / previous_value) * 100

            trend_points.append(TrendPoint(
                period=period,
                value=round(value, 2),
                change_percentage=round(change_pct, 2) if change_pct else None
            ))
            previous_value = value

        # Calculate average YoY growth rate
        changes = [tp.change_percentage for tp in trend_points if tp.change_percentage is not None]
        avg_growth_rate = sum(changes) / len(changes) if changes else 0.0

        # Calculate QoQ growth rate if quarterly data available (Week 5)
        qoq_growth = None
        has_quarterly = period_types and any(pt == "quarterly" for pt in period_types)
        if has_quarterly and len(trend_points) >= 2:
            qoq_growth = self._calculate_qoq_growth(trend_points)

        # Detect seasonality if enough data points (Week 5)
        seasonality_detected = None
        seasonality_strength = None
        if len(data_points) >= 4:  # Need at least 4 periods for seasonality
            seasonality_detected, seasonality_strength = self._detect_seasonality(
                [value for _, value in sorted_points]
            )

        # Determine trend direction
        if avg_growth_rate > 5:
            trend_direction = "increasing"
        elif avg_growth_rate < -5:
            trend_direction = "decreasing"
        elif abs(avg_growth_rate) <= 5:
            trend_direction = "stable"
        else:
            trend_direction = "volatile"

        # Determine trend status
        if metric_name in ["revenue", "net_profit"] and avg_growth_rate > 0:
            trend_status = "positive"
        elif metric_name in ["revenue", "net_profit"] and avg_growth_rate < -10:
            trend_status = "concerning"
        else:
            trend_status = "neutral"

        return TrendAnalysis(
            metric_name=metric_name,
            periods=trend_points,
            trend_direction=trend_direction,
            avg_growth_rate=round(avg_growth_rate, 2),
            qoq_growth_rate=round(qoq_growth, 2) if qoq_growth else None,
            seasonality_detected=seasonality_detected,
            seasonality_strength=round(seasonality_strength, 2) if seasonality_strength else None,
            trend_status=trend_status
        )

    def _calculate_qoq_growth(self, trend_points: List[TrendPoint]) -> Optional[float]:
        """
        Calculate Quarter-over-Quarter growth rate (Week 5).
        
        Uses the last two consecutive periods for QoQ calculation.
        
        Args:
            trend_points: List of trend points
            
        Returns:
            QoQ growth rate (%) or None
        """
        if len(trend_points) < 2:
            return None
        
        # Get last two periods
        latest = trend_points[-1]
        previous = trend_points[-2]
        
        if previous.value and previous.value != 0:
            qoq = ((latest.value - previous.value) / previous.value) * 100
            return qoq
        
        return None
    
    def _detect_seasonality(self, values: List[float]) -> tuple[bool, Optional[float]]:
        """
        Detect seasonal patterns in data (Week 5).
        
        Simple seasonality detection using coefficient of variation and
        autocorrelation-like pattern matching.
        
        Args:
            values: List of metric values
            
        Returns:
            Tuple of (seasonality_detected: bool, strength: float 0-100)
        """
        if len(values) < 4:
            return False, None
        
        import statistics
        
        # Calculate coefficient of variation
        mean = statistics.mean(values)
        if mean == 0:
            return False, None
        
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        coef_variation = (stdev / mean) * 100
        
        # Check for repeating patterns
        # Simple approach: check if values at similar positions (e.g., Q1, Q2, Q3, Q4) are similar
        pattern_strength = 0.0
        
        if len(values) >= 8:  # At least 2 years of quarterly data
            # Compare Q1 with Q1, Q2 with Q2, etc.
            quarters = 4
            quarter_groups = [[] for _ in range(quarters)]
            
            for i, val in enumerate(values):
                quarter_idx = i % quarters
                quarter_groups[quarter_idx].append(val)
            
            # Check variance within each quarter group
            within_quarter_variations = []
            for group in quarter_groups:
                if len(group) >= 2:
                    group_mean = statistics.mean(group)
                    if group_mean != 0:
                        group_stdev = statistics.stdev(group)
                        within_quarter_variations.append((group_stdev / group_mean) * 100)
            
            if within_quarter_variations:
                avg_within_variation = statistics.mean(within_quarter_variations)
                
                # If within-quarter variation is low compared to overall variation,
                # suggests seasonality
                if coef_variation > 0 and avg_within_variation < coef_variation * 0.5:
                    pattern_strength = min(100, (coef_variation - avg_within_variation) * 2)
        
        # Simpler check for fewer data points
        else:
            # Look for alternating high/low patterns
            if len(values) >= 4:
                ups = 0
                downs = 0
                for i in range(1, len(values)):
                    if values[i] > values[i-1]:
                        ups += 1
                    elif values[i] < values[i-1]:
                        downs += 1
                
                # Balanced ups and downs suggest cyclical pattern
                if ups > 0 and downs > 0:
                    balance = min(ups, downs) / max(ups, downs)
                    if balance > 0.6:  # Fairly balanced
                        pattern_strength = balance * 50
        
        # Seasonality detected if:
        # 1. Coefficient of variation is significant (>10%)
        # 2. Pattern strength is detected
        seasonality_detected = coef_variation > 10 and pattern_strength > 20
        
        return seasonality_detected, pattern_strength if seasonality_detected else None

    # ========================================================================
    # ALTMAN Z-SCORE (Week 5)
    # ========================================================================

    def _calculate_altman_z_score(
        self,
        statement: FinancialStatement
    ) -> tuple[Optional[float], Optional[str]]:
        """
        Calculate Altman Z-Score for bankruptcy prediction (Week 5).
        
        Altman Z-Score formula (for private companies):
        Z = 0.717*X1 + 0.847*X2 + 3.107*X3 + 0.420*X4 + 0.998*X5
        
        Where:
        X1 = Working Capital / Total Assets
        X2 = Retained Earnings / Total Assets
        X3 = EBIT / Total Assets
        X4 = Book Value of Equity / Total Liabilities
        X5 = Sales / Total Assets
        
        Interpretation:
        Z > 2.9: Safe zone (low bankruptcy risk)
        1.23 < Z < 2.9: Grey zone (moderate risk)
        Z < 1.23: Distress zone (high bankruptcy risk)
        
        Args:
            statement: Financial statement data
            
        Returns:
            Tuple of (z_score, bankruptcy_risk)
        """
        if not statement.total_assets or statement.total_assets == 0:
            return None, None
        
        # X1 = Working Capital / Total Assets
        x1 = 0.0
        if statement.current_assets and statement.current_liabilities:
            working_capital = statement.current_assets - statement.current_liabilities
            x1 = working_capital / statement.total_assets
        
        # X2 = Retained Earnings / Total Assets
        # Approximation: use equity if retained earnings not available
        x2 = 0.0
        if statement.retained_earnings:
            x2 = statement.retained_earnings / statement.total_assets
        elif statement.equity:
            x2 = (statement.equity * 0.5) / statement.total_assets  # Conservative estimate
        
        # X3 = EBIT / Total Assets
        x3 = 0.0
        if statement.ebit:
            x3 = statement.ebit / statement.total_assets
        elif statement.operating_profit:
            x3 = statement.operating_profit / statement.total_assets
        
        # X4 = Book Value of Equity / Total Liabilities
        x4 = 0.0
        if statement.equity and statement.total_liabilities and statement.total_liabilities > 0:
            x4 = statement.equity / statement.total_liabilities
        
        # X5 = Sales / Total Assets
        x5 = 0.0
        if statement.revenue:
            x5 = statement.revenue / statement.total_assets
        
        # Calculate Z-Score (private company model)
        z_score = (
            0.717 * x1 +
            0.847 * x2 +
            3.107 * x3 +
            0.420 * x4 +
            0.998 * x5
        )
        
        # Determine bankruptcy risk
        if z_score > 2.9:
            bankruptcy_risk = "safe"
        elif z_score > 1.23:
            bankruptcy_risk = "grey_zone"
        else:
            bankruptcy_risk = "distress"
        
        return round(z_score, 2), bankruptcy_risk

    def _calculate_health_score(
        self,
        ratio_analyses: List[RatioAnalysis],
        trends: List[TrendAnalysis],
        statements: Optional[List[FinancialStatement]] = None
    ) -> FinancialHealthScore:
        """
        Calculate overall financial health score (Week 5 updated with Altman Z-score)
        
        Args:
            ratio_analyses: List of ratio analyses
            trends: List of trend analyses
            statements: Optional list of financial statements (for Z-score calculation)
        """
        if not ratio_analyses:
            return FinancialHealthScore(
                overall_score=0.0,
                liquidity_score=0.0,
                profitability_score=0.0,
                leverage_score=0.0,
                efficiency_score=0.0,
                trend_score=0.0,
                risk_level="critical"
            )

        # Use most recent period for component scores
        latest_ratios = ratio_analyses[-1]

        # Component scores
        liquidity_score = self._score_liquidity(latest_ratios.liquidity) if latest_ratios.liquidity else 50.0
        profitability_score = self._score_profitability(latest_ratios.profitability) if latest_ratios.profitability else 50.0
        leverage_score = self._score_leverage(latest_ratios.leverage) if latest_ratios.leverage else 50.0
        efficiency_score = self._score_efficiency(latest_ratios.efficiency) if latest_ratios.efficiency else 50.0
        cash_flow_score = self._score_cash_flow(latest_ratios.cash_flow) if latest_ratios.cash_flow else 50.0  # Week 5
        trend_score = self._score_trends(trends)

        # Calculate Altman Z-Score (Week 5)
        altman_z_score = None
        bankruptcy_risk = None
        if statements and len(statements) > 0:
            latest_statement = statements[-1]
            altman_z_score, bankruptcy_risk = self._calculate_altman_z_score(latest_statement)

        # Overall score (weighted average) - Week 5 updated weights
        overall_score = (
            profitability_score * 0.25 +
            leverage_score * 0.20 +
            liquidity_score * 0.15 +
            cash_flow_score * 0.20 +  # Week 5 addition
            efficiency_score * 0.10 +
            trend_score * 0.10
        )

        # Risk level (consider Z-score in risk assessment - Week 5)
        if bankruptcy_risk == "distress":
            risk_level = "critical"
        elif bankruptcy_risk == "grey_zone" and overall_score < 60:
            risk_level = "high"
        elif overall_score >= 75:
            risk_level = "low"
        elif overall_score >= 60:
            risk_level = "moderate"
        elif overall_score >= 40:
            risk_level = "high"
        else:
            risk_level = "critical"

        # Identify strengths and weaknesses (Week 5 updated with cash flow)
        strengths, weaknesses = self._identify_strengths_weaknesses(
            liquidity_score, profitability_score, leverage_score, efficiency_score, cash_flow_score, trend_score
        )

        # Add Z-score to strengths/weaknesses (Week 5)
        if altman_z_score:
            if bankruptcy_risk == "safe":
                strengths.append(f"Strong Altman Z-Score ({altman_z_score}) - low bankruptcy risk")
            elif bankruptcy_risk == "distress":
                weaknesses.append(f"Concerning Altman Z-Score ({altman_z_score}) - high bankruptcy risk")

        # Generate recommendations
        recommendations = self._generate_recommendations(weaknesses, latest_ratios)

        return FinancialHealthScore(
            overall_score=round(overall_score, 1),
            liquidity_score=round(liquidity_score, 1),
            profitability_score=round(profitability_score, 1),
            leverage_score=round(leverage_score, 1),
            efficiency_score=round(efficiency_score, 1),
            trend_score=round(trend_score, 1),
            altman_z_score=altman_z_score,  # Week 5
            bankruptcy_risk=bankruptcy_risk,  # Week 5
            risk_level=risk_level,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )

    def _calculate_confidence(
        self,
        statements: List[FinancialStatement],
        ratio_analyses: List[RatioAnalysis]
    ) -> float:
        """
        Calculate confidence score based on data completeness

        Factors:
        - Number of periods analyzed
        - Completeness of financial data
        - Availability of ratio calculations
        """
        if not statements:
            return 0.0

        confidence = 0.0

        # Factor 1: Number of periods (up to 30 points)
        num_periods = len(statements)
        confidence += min(num_periods * 10, 30)

        # Factor 2: Data completeness (up to 40 points)
        completeness_scores = []
        for stmt in statements:
            fields_available = sum([
                1 for field in [stmt.revenue, stmt.net_profit, stmt.total_assets, stmt.equity]
                if field is not None
            ])
            completeness_scores.append(fields_available / 4 * 100)

        if completeness_scores:
            confidence += (sum(completeness_scores) / len(completeness_scores)) * 0.4

        # Factor 3: Ratio calculations (up to 30 points)
        if ratio_analyses:
            ratios_calculated = sum([
                1 for ra in ratio_analyses
                if ra.liquidity and ra.profitability and ra.leverage
            ])
            confidence += (ratios_calculated / len(ratio_analyses)) * 30

        return min(round(confidence, 1), 100.0)

    # ============================================================================
    # HELPER METHODS - ASSESSMENT & SCORING
    # ============================================================================

    def _assess_current_ratio(self, current_ratio: Optional[float]) -> str:
        """Assess current ratio health"""
        if not current_ratio:
            return "unknown"
        if current_ratio >= 2.0:
            return "healthy"
        elif current_ratio >= 1.0:
            return "warning"
        else:
            return "critical"

    def _assess_quick_ratio(self, quick_ratio: Optional[float]) -> str:
        """Assess quick ratio health"""
        if not quick_ratio:
            return "unknown"
        if quick_ratio >= 1.0:
            return "healthy"
        elif quick_ratio >= 0.75:
            return "warning"
        else:
            return "critical"

    def _assess_profitability(
        self,
        net_margin: Optional[float],
        roa: Optional[float],
        roe: Optional[float]
    ) -> str:
        """Assess overall profitability"""
        scores = []

        if net_margin is not None:
            if net_margin >= 15:
                scores.append(4)
            elif net_margin >= 10:
                scores.append(3)
            elif net_margin >= 5:
                scores.append(2)
            else:
                scores.append(1)

        if roa is not None:
            if roa >= 10:
                scores.append(4)
            elif roa >= 5:
                scores.append(3)
            elif roa >= 2:
                scores.append(2)
            else:
                scores.append(1)

        if scores:
            avg = sum(scores) / len(scores)
            if avg >= 3.5:
                return "excellent"
            elif avg >= 2.5:
                return "good"
            elif avg >= 1.5:
                return "average"
            else:
                return "poor"

        return "unknown"

    def _assess_leverage(
        self,
        debt_to_equity: Optional[float],
        debt_to_assets: Optional[float]
    ) -> str:
        """Assess leverage/debt levels"""
        if debt_to_equity is None:
            return "unknown"

        if debt_to_equity <= 0.5:
            return "conservative"
        elif debt_to_equity <= 1.0:
            return "moderate"
        elif debt_to_equity <= 2.0:
            return "aggressive"
        else:
            return "overleveraged"

    def _assess_efficiency(self, asset_turnover: Optional[float]) -> str:
        """Assess asset efficiency"""
        if not asset_turnover:
            return "unknown"

        if asset_turnover >= 2.0:
            return "excellent"
        elif asset_turnover >= 1.0:
            return "good"
        elif asset_turnover >= 0.5:
            return "average"
        else:
            return "poor"

    def _assess_cash_flow(
        self,
        ocf_ratio: Optional[float],
        cf_margin: Optional[float],
        cf_to_debt: Optional[float]
    ) -> str:
        """
        Assess cash flow health (Week 5)

        Args:
            ocf_ratio: Operating CF / Current Liabilities
            cf_margin: Operating CF / Revenue * 100
            cf_to_debt: Operating CF / Total Debt

        Returns:
            Status: excellent|good|average|poor
        """
        scores = []

        # OCF Ratio assessment
        if ocf_ratio is not None:
            if ocf_ratio >= 0.5:
                scores.append(4)  # Excellent
            elif ocf_ratio >= 0.3:
                scores.append(3)  # Good
            elif ocf_ratio >= 0.1:
                scores.append(2)  # Average
            else:
                scores.append(1)  # Poor

        # CF Margin assessment
        if cf_margin is not None:
            if cf_margin >= 15:
                scores.append(4)
            elif cf_margin >= 10:
                scores.append(3)
            elif cf_margin >= 5:
                scores.append(2)
            else:
                scores.append(1)

        # CF to Debt assessment
        if cf_to_debt is not None:
            if cf_to_debt >= 0.25:
                scores.append(4)
            elif cf_to_debt >= 0.15:
                scores.append(3)
            elif cf_to_debt >= 0.05:
                scores.append(2)
            else:
                scores.append(1)

        if scores:
            avg = sum(scores) / len(scores)
            if avg >= 3.5:
                return "excellent"
            elif avg >= 2.5:
                return "good"
            elif avg >= 1.5:
                return "average"
            else:
                return "poor"

        return "unknown"

    def _score_liquidity(self, liquidity: Optional[LiquidityRatios]) -> float:
        """Score liquidity component (0-100)"""
        if not liquidity or not liquidity.current_ratio:
            return 50.0

        # Current ratio scoring
        if liquidity.current_ratio >= 2.0:
            score = 100.0
        elif liquidity.current_ratio >= 1.5:
            score = 80.0
        elif liquidity.current_ratio >= 1.0:
            score = 60.0
        else:
            score = 30.0

        return score

    def _score_profitability(self, profitability: Optional[ProfitabilityRatios]) -> float:
        """Score profitability component (0-100)"""
        if not profitability:
            return 50.0

        scores = []

        # Net margin
        if profitability.net_margin is not None:
            if profitability.net_margin >= 15:
                scores.append(100)
            elif profitability.net_margin >= 10:
                scores.append(80)
            elif profitability.net_margin >= 5:
                scores.append(60)
            elif profitability.net_margin >= 0:
                scores.append(40)
            else:
                scores.append(20)

        # ROA
        if profitability.return_on_assets is not None:
            if profitability.return_on_assets >= 10:
                scores.append(100)
            elif profitability.return_on_assets >= 5:
                scores.append(75)
            elif profitability.return_on_assets >= 2:
                scores.append(50)
            else:
                scores.append(30)

        return sum(scores) / len(scores) if scores else 50.0

    def _score_leverage(self, leverage: Optional[LeverageRatios]) -> float:
        """Score leverage component (0-100) - lower debt = higher score"""
        if not leverage or not leverage.debt_to_equity:
            return 50.0

        # Debt-to-equity scoring (inverted - lower is better)
        if leverage.debt_to_equity <= 0.5:
            score = 100.0
        elif leverage.debt_to_equity <= 1.0:
            score = 75.0
        elif leverage.debt_to_equity <= 2.0:
            score = 50.0
        else:
            score = 25.0

        return score

    def _score_efficiency(self, efficiency: Optional[EfficiencyRatios]) -> float:
        """Score efficiency component (0-100)"""
        if not efficiency or not efficiency.asset_turnover:
            return 50.0

        if efficiency.asset_turnover >= 2.0:
            score = 100.0
        elif efficiency.asset_turnover >= 1.0:
            score = 75.0
        elif efficiency.asset_turnover >= 0.5:
            score = 50.0
        else:
            score = 30.0

        return score

    def _score_cash_flow(self, cash_flow: Optional[CashFlowRatios]) -> float:
        """
        Score cash flow component (0-100) - Week 5

        Args:
            cash_flow: Cash flow ratios

        Returns:
            Score from 0-100
        """
        if not cash_flow:
            return 50.0

        scores = []

        # OCF Ratio scoring
        if cash_flow.operating_cash_flow_ratio is not None:
            ocf_ratio = cash_flow.operating_cash_flow_ratio
            if ocf_ratio >= 0.5:
                scores.append(100)
            elif ocf_ratio >= 0.3:
                scores.append(75)
            elif ocf_ratio >= 0.1:
                scores.append(50)
            else:
                scores.append(25)

        # CF Margin scoring
        if cash_flow.cash_flow_margin is not None:
            cf_margin = cash_flow.cash_flow_margin
            if cf_margin >= 15:
                scores.append(100)
            elif cf_margin >= 10:
                scores.append(75)
            elif cf_margin >= 5:
                scores.append(50)
            else:
                scores.append(30)

        # CF to Debt scoring
        if cash_flow.cash_flow_to_debt is not None:
            cf_to_debt = cash_flow.cash_flow_to_debt
            if cf_to_debt >= 0.25:
                scores.append(100)
            elif cf_to_debt >= 0.15:
                scores.append(75)
            elif cf_to_debt >= 0.05:
                scores.append(50)
            else:
                scores.append(25)

        return sum(scores) / len(scores) if scores else 50.0

    # ========================================================================
    # INDUSTRY BENCHMARKING (Week 5)
    # ========================================================================

    async def _calculate_industry_benchmarks(
        self,
        target: str,
        statements: List[FinancialStatement],
        ratios: List[RatioAnalysis]
    ) -> Optional[IndustryBenchmark]:
        """
        Calculate industry benchmarks using GUS statistics (Week 5).
        
        Args:
            target: Target identifier (for logging)
            statements: Financial statements
            ratios: Ratio analysis results
            
        Returns:
            IndustryBenchmark or None if data unavailable
        """
        if not GUS_AVAILABLE:
            logger.warning("GUS client not available for industry benchmarking")
            return None
        
        if not statements or not ratios:
            logger.warning("No financial data available for benchmarking")
            return None
        
        # Get company PKD code from GUS
        pkd_code = await self._get_company_pkd_code(target)
        if not pkd_code:
            logger.warning(f"PKD code not found for {target}")
            return None
        
        # Fetch industry statistics from GUS
        gus_client = GUSClient()
        try:
            industry_stats = await gus_client.get_industry_statistics(pkd_code=pkd_code)
        finally:
            await gus_client.close()
        
        if not industry_stats:
            logger.warning(f"Industry statistics not available for PKD {pkd_code}")
            return None
        
        # Get latest financial data
        latest_statement = statements[-1]
        latest_ratios = ratios[-1]
        
        # Calculate percentile rankings
        revenue_percentile = self._calculate_percentile(
            latest_statement.revenue,
            industry_stats.get("avg_revenue")
        )
        
        employee_percentile = self._calculate_percentile(
            latest_statement.employee_count,
            industry_stats.get("avg_employees")
        )
        
        # Compare profit margin vs industry average
        company_profit_margin = None
        if latest_ratios.profitability and latest_ratios.profitability.net_profit_margin:
            company_profit_margin = latest_ratios.profitability.net_profit_margin
        
        profit_margin_diff = None
        if company_profit_margin and industry_stats.get("avg_profit_margin"):
            profit_margin_diff = company_profit_margin - industry_stats["avg_profit_margin"]
        
        # Assess competitive position
        competitive_position = self._assess_competitive_position(
            revenue_percentile,
            employee_percentile,
            profit_margin_diff
        )
        
        return IndustryBenchmark(
            pkd_code=pkd_code,
            industry_name=industry_stats.get("industry_name"),
            year=industry_stats.get("year"),
            revenue_percentile=revenue_percentile,
            employee_percentile=employee_percentile,
            profit_margin_vs_avg=round(profit_margin_diff, 2) if profit_margin_diff else None,
            industry_avg_revenue=industry_stats.get("avg_revenue"),
            industry_avg_employees=industry_stats.get("avg_employees"),
            industry_avg_profit_margin=industry_stats.get("avg_profit_margin"),
            industry_growth_rate=industry_stats.get("growth_rate"),
            competitive_position=competitive_position
        )
    
    async def _get_company_pkd_code(self, target: str) -> Optional[str]:
        """
        Get PKD code for company from GUS.
        
        Args:
            target: NIP, REGON, or KRS number
            
        Returns:
            PKD code or None
        """
        if not GUS_AVAILABLE:
            return None
        
        # Extract NIP if available
        nip = self._extract_nip(target)
        
        gus_client = GUSClient()
        try:
            company_data = await gus_client.get_company_data(nip=nip)
            if company_data:
                return company_data.get("pkd_code")
        except Exception as e:
            logger.error(f"Error fetching PKD code: {e}")
        finally:
            await gus_client.close()
        
        return None
    
    def _extract_nip(self, target: str) -> Optional[str]:
        """
        Extract NIP number from target string.
        
        Args:
            target: Target identifier
            
        Returns:
            10-digit NIP or None
        """
        import re
        
        # Patterns for NIP extraction
        patterns = [
            r'NIP[\s:]*(\d{10})',
            r'^(\d{10})$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, target, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _calculate_percentile(
        self,
        company_value: Optional[float],
        industry_avg: Optional[float]
    ) -> Optional[float]:
        """
        Calculate percentile ranking (0-100).
        
        Simplified percentile: if company > avg, percentile > 50
        
        Args:
            company_value: Company metric value
            industry_avg: Industry average value
            
        Returns:
            Percentile (0-100) or None
        """
        if company_value is None or industry_avg is None or industry_avg == 0:
            return None
        
        # Simplified percentile calculation
        # If company_value > avg: percentile in 50-100 range
        # If company_value < avg: percentile in 0-50 range
        
        ratio = company_value / industry_avg
        
        if ratio >= 1.0:
            # Above average: map to 50-100
            # ratio 1.0 -> 50, ratio 2.0 -> 75, ratio 4.0+ -> 95
            percentile = 50 + min(45, (ratio - 1.0) * 30)
        else:
            # Below average: map to 0-50
            # ratio 0.0 -> 5, ratio 0.5 -> 25, ratio 1.0 -> 50
            percentile = ratio * 50
        
        return round(percentile, 1)
    
    def _assess_competitive_position(
        self,
        revenue_percentile: Optional[float],
        employee_percentile: Optional[float],
        profit_margin_diff: Optional[float]
    ) -> str:
        """
        Assess overall competitive position.
        
        Args:
            revenue_percentile: Revenue percentile (0-100)
            employee_percentile: Employee percentile (0-100)
            profit_margin_diff: Profit margin vs industry avg (percentage points)
            
        Returns:
            "above_average" | "average" | "below_average"
        """
        scores = []
        
        # Revenue position
        if revenue_percentile is not None:
            if revenue_percentile >= 60:
                scores.append(1)  # Above average
            elif revenue_percentile >= 40:
                scores.append(0)  # Average
            else:
                scores.append(-1)  # Below average
        
        # Employee position
        if employee_percentile is not None:
            if employee_percentile >= 60:
                scores.append(1)
            elif employee_percentile >= 40:
                scores.append(0)
            else:
                scores.append(-1)
        
        # Profitability position
        if profit_margin_diff is not None:
            if profit_margin_diff >= 5:
                scores.append(1)
            elif profit_margin_diff >= -5:
                scores.append(0)
            else:
                scores.append(-1)
        
        if not scores:
            return "average"
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score > 0.3:
            return "above_average"
        elif avg_score < -0.3:
            return "below_average"
        else:
            return "average"

    def _score_trends(self, trends: List[TrendAnalysis]) -> float:
        """Score trend component (0-100)"""
        if not trends:
            return 50.0

        positive_trends = sum(1 for t in trends if t.trend_status == "positive")
        neutral_trends = sum(1 for t in trends if t.trend_status == "neutral")

        total_trends = len(trends)
        score = ((positive_trends * 100) + (neutral_trends * 60)) / total_trends

        return min(score, 100.0)

    def _identify_strengths_weaknesses(
        self,
        liquidity_score: float,
        profitability_score: float,
        leverage_score: float,
        efficiency_score: float,
        cash_flow_score: float,
        trend_score: float
    ) -> tuple[List[str], List[str]]:
        """Identify key strengths and weaknesses (Week 5 updated with cash flow)"""
        strengths = []
        weaknesses = []

        # Liquidity
        if liquidity_score >= 75:
            strengths.append("Strong liquidity position")
        elif liquidity_score < 50:
            weaknesses.append("Weak liquidity ratios")

        # Profitability
        if profitability_score >= 75:
            strengths.append("Excellent profitability")
        elif profitability_score < 50:
            weaknesses.append("Low profit margins")

        # Leverage
        if leverage_score >= 75:
            strengths.append("Conservative debt levels")
        elif leverage_score < 50:
            weaknesses.append("High leverage risk")

        # Efficiency
        if efficiency_score >= 75:
            strengths.append("Efficient asset utilization")
        elif efficiency_score < 50:
            weaknesses.append("Poor asset efficiency")

        # Cash Flow (Week 5 addition)
        if cash_flow_score >= 75:
            strengths.append("Strong cash flow generation")
        elif cash_flow_score < 50:
            weaknesses.append("Weak cash flow performance")

        # Trends
        if trend_score >= 75:
            strengths.append("Positive growth trends")
        elif trend_score < 50:
            weaknesses.append("Declining performance trends")

        return strengths, weaknesses

    def _generate_recommendations(
        self,
        weaknesses: List[str],
        latest_ratios: RatioAnalysis
    ) -> List[str]:
        """Generate actionable recommendations based on weaknesses"""
        recommendations = []

        for weakness in weaknesses:
            if "liquidity" in weakness.lower():
                recommendations.append("Improve working capital management and reduce current liabilities")
            elif "profit" in weakness.lower():
                recommendations.append("Focus on cost reduction and revenue optimization strategies")
            elif "leverage" in weakness.lower():
                recommendations.append("Consider debt restructuring or equity financing to reduce leverage")
            elif "efficiency" in weakness.lower():
                recommendations.append("Optimize asset utilization and improve operational efficiency")
            elif "trend" in weakness.lower():
                recommendations.append("Investigate root causes of declining performance")

        if not recommendations:
            recommendations.append("Maintain current financial strategy and monitor key metrics")

        return recommendations[:3]  # Limit to top 3 recommendations
