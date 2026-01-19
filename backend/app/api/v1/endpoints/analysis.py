"""
Analysis API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, HttpUrl
from enum import Enum
import uuid
import asyncio
from datetime import datetime

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()

# In-memory job storage (in production, use Redis or database)
analysis_jobs: Dict[str, Dict[str, Any]] = {}


class GeographyType(str, Enum):
    POLAND = "poland"
    EUROPE = "europe"
    CEE = "cee"
    GLOBAL = "global"


class WebsiteAnalysisRequest(BaseModel):
    url: HttpUrl


class WebsiteAnalysisJobResponse(BaseModel):
    job_id: str
    status: str
    url: str
    created_at: str


class WebsiteContentData(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    products: List[str] = []
    services: List[str] = []
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    social_links: Dict[str, str] = {}


class TechStackData(BaseModel):
    cms: Optional[str] = None
    frameworks: List[str] = []
    analytics: List[str] = []
    hosting: Optional[str] = None
    ssl_enabled: bool = False


class WebsiteAnalysisResult(BaseModel):
    job_id: str
    status: str
    url: str
    content: Optional[WebsiteContentData] = None
    tech_stack: Optional[TechStackData] = None
    screenshot_url: Optional[str] = None
    error: Optional[str] = None
    completed_at: Optional[str] = None


class MarketAnalysisRequest(BaseModel):
    industry: str
    geography: GeographyType = GeographyType.POLAND
    depth: str = "standard"


class MarketDataPoint(BaseModel):
    region: str
    market_size: float
    growth_rate: float
    key_players: int
    year: int


class MarketAnalysisResponse(BaseModel):
    id: str
    industry: str
    geography: str
    status: str
    data: List[MarketDataPoint]
    insights: List[str]
    trends: List[dict]


# Mock data for different geographies
POLAND_MARKET_DATA = {
    "manufacturing": [
        MarketDataPoint(region="Polska", market_size=45.2, growth_rate=4.5, key_players=1250, year=2024),
        MarketDataPoint(region="Mazowieckie", market_size=12.8, growth_rate=5.2, key_players=380, year=2024),
        MarketDataPoint(region="Śląskie", market_size=9.4, growth_rate=3.8, key_players=290, year=2024),
        MarketDataPoint(region="Wielkopolskie", market_size=7.6, growth_rate=4.9, key_players=215, year=2024),
    ],
    "technology": [
        MarketDataPoint(region="Polska", market_size=28.5, growth_rate=12.3, key_players=890, year=2024),
        MarketDataPoint(region="Mazowieckie", market_size=14.2, growth_rate=14.1, key_players=420, year=2024),
        MarketDataPoint(region="Małopolskie", market_size=5.8, growth_rate=15.8, key_players=185, year=2024),
        MarketDataPoint(region="Dolnośląskie", market_size=4.1, growth_rate=11.2, key_players=145, year=2024),
    ],
    "logistics": [
        MarketDataPoint(region="Polska", market_size=52.8, growth_rate=6.7, key_players=980, year=2024),
        MarketDataPoint(region="Mazowieckie", market_size=15.2, growth_rate=7.2, key_players=285, year=2024),
        MarketDataPoint(region="Śląskie", market_size=11.5, growth_rate=5.9, key_players=195, year=2024),
        MarketDataPoint(region="Pomorskie", market_size=8.3, growth_rate=8.1, key_players=165, year=2024),
    ],
}

EUROPE_MARKET_DATA = {
    "manufacturing": [
        MarketDataPoint(region="Unia Europejska", market_size=2150.0, growth_rate=2.8, key_players=45000, year=2024),
        MarketDataPoint(region="Niemcy", market_size=580.5, growth_rate=1.9, key_players=12500, year=2024),
        MarketDataPoint(region="Francja", market_size=320.2, growth_rate=2.1, key_players=8900, year=2024),
        MarketDataPoint(region="Włochy", market_size=285.8, growth_rate=2.4, key_players=7800, year=2024),
        MarketDataPoint(region="Polska", market_size=45.2, growth_rate=4.5, key_players=1250, year=2024),
        MarketDataPoint(region="Hiszpania", market_size=195.4, growth_rate=2.9, key_players=5200, year=2024),
    ],
    "technology": [
        MarketDataPoint(region="Unia Europejska", market_size=890.5, growth_rate=9.8, key_players=28000, year=2024),
        MarketDataPoint(region="Niemcy", market_size=185.2, growth_rate=8.5, key_players=5800, year=2024),
        MarketDataPoint(region="Francja", market_size=142.8, growth_rate=10.2, key_players=4200, year=2024),
        MarketDataPoint(region="Holandia", market_size=85.6, growth_rate=11.5, key_players=2100, year=2024),
        MarketDataPoint(region="Polska", market_size=28.5, growth_rate=12.3, key_players=890, year=2024),
        MarketDataPoint(region="Szwecja", market_size=62.4, growth_rate=9.1, key_players=1850, year=2024),
    ],
    "logistics": [
        MarketDataPoint(region="Unia Europejska", market_size=1420.0, growth_rate=4.2, key_players=35000, year=2024),
        MarketDataPoint(region="Niemcy", market_size=385.5, growth_rate=3.8, key_players=8500, year=2024),
        MarketDataPoint(region="Holandia", market_size=165.2, growth_rate=5.1, key_players=3200, year=2024),
        MarketDataPoint(region="Francja", market_size=198.8, growth_rate=3.5, key_players=5100, year=2024),
        MarketDataPoint(region="Polska", market_size=52.8, growth_rate=6.7, key_players=980, year=2024),
        MarketDataPoint(region="Belgia", market_size=95.4, growth_rate=4.8, key_players=2400, year=2024),
    ],
}


def get_market_insights(industry: str, geography: str) -> List[str]:
    """Generate market insights based on industry and geography."""
    if geography == "poland":
        return [
            f"Rynek {industry} w Polsce wykazuje stabilny wzrost",
            "Główne ośrodki rozwoju to województwa: mazowieckie, śląskie i wielkopolskie",
            "Przewidywany wzrost w ciągu 5 lat: 15-25%",
            "Kluczowe czynniki wzrostu: digitalizacja, inwestycje zagraniczne",
        ]
    else:
        return [
            f"Europejski rynek {industry} jest jednym z największych na świecie",
            "Polska plasuje się w czołówce krajów CEE pod względem dynamiki wzrostu",
            "Niemcy i Francja dominują pod względem wielkości rynku",
            "Trend: konsolidacja rynku i rosnąca automatyzacja",
        ]


def get_market_trends(industry: str, geography: str) -> List[dict]:
    """Generate market trends based on industry and geography."""
    base_trends = [
        {"name": "Digitalizacja", "impact": "high", "timeline": "2024-2027"},
        {"name": "Automatyzacja", "impact": "high", "timeline": "2024-2028"},
        {"name": "Zrównoważony rozwój", "impact": "medium", "timeline": "2025-2030"},
    ]

    if geography == "europe":
        base_trends.extend([
            {"name": "Regulacje EU (ESG)", "impact": "high", "timeline": "2024-2026"},
            {"name": "Integracja łańcuchów dostaw", "impact": "medium", "timeline": "2024-2027"},
        ])
    else:
        base_trends.extend([
            {"name": "Ekspansja na rynki CEE", "impact": "medium", "timeline": "2024-2026"},
            {"name": "Polski Ład dla przemysłu", "impact": "low", "timeline": "2024-2025"},
        ])

    return base_trends


async def perform_website_analysis(job_id: str, url: str):
    """Background task to perform website analysis."""
    await asyncio.sleep(2)  # Simulate analysis time

    # Mock analysis results based on URL
    url_lower = url.lower()

    if "fado" in url_lower:
        content = WebsiteContentData(
            title="FADO Sp. z o.o. - Producent tworzyw sztucznych",
            description="Wiodący producent komponentów z tworzyw sztucznych dla przemysłu motoryzacyjnego i AGD",
            company_name="FADO Sp. z o.o.",
            industry="Manufacturing - Plastics Processing",
            products=["Komponenty wtryskowe", "Formy wtryskowe", "Produkty z tworzyw technicznych"],
            services=["Wtrysk tworzyw", "Projektowanie form", "Montaż podzespołów"],
            contact_email="kontakt@fado.pl",
            contact_phone="+48 22 123 45 67",
            address="ul. Przemysłowa 15, 00-001 Warszawa",
            social_links={
                "linkedin": "https://linkedin.com/company/fado",
                "facebook": "https://facebook.com/fadopolska"
            }
        )
        tech_stack = TechStackData(
            cms="WordPress",
            frameworks=["React", "Next.js"],
            analytics=["Google Analytics", "Hotjar"],
            hosting="AWS",
            ssl_enabled=True
        )
    else:
        # Generic website analysis
        domain = url.split("//")[-1].split("/")[0]
        content = WebsiteContentData(
            title=f"Website Analysis - {domain}",
            description="Company website with business information",
            company_name=domain.split(".")[0].capitalize(),
            industry="General Business",
            products=["Product 1", "Product 2"],
            services=["Service 1", "Service 2"],
            contact_email=f"contact@{domain}",
            social_links={}
        )
        tech_stack = TechStackData(
            cms="Unknown",
            frameworks=["JavaScript"],
            analytics=["Google Analytics"],
            ssl_enabled=True
        )

    # Update job status
    analysis_jobs[job_id].update({
        "status": "completed",
        "content": content.model_dump(),
        "tech_stack": tech_stack.model_dump(),
        "screenshot_url": f"/screenshots/{job_id}.png",
        "completed_at": datetime.utcnow().isoformat()
    })


@router.post("/website", response_model=WebsiteAnalysisJobResponse)
async def analyze_website(request: WebsiteAnalysisRequest):
    """
    Create a website analysis job.

    The analysis runs asynchronously. Use the returned job_id to poll for results.
    """
    job_id = str(uuid.uuid4())
    url = str(request.url)

    # Create job entry
    analysis_jobs[job_id] = {
        "job_id": job_id,
        "status": "processing",
        "url": url,
        "created_at": datetime.utcnow().isoformat(),
        "content": None,
        "tech_stack": None,
        "screenshot_url": None,
        "error": None,
        "completed_at": None
    }

    # Start background analysis
    asyncio.create_task(perform_website_analysis(job_id, url))

    return WebsiteAnalysisJobResponse(
        job_id=job_id,
        status="processing",
        url=url,
        created_at=analysis_jobs[job_id]["created_at"]
    )


@router.get("/website/{job_id}", response_model=WebsiteAnalysisResult)
async def get_website_analysis(job_id: str):
    """
    Get website analysis results by job ID.

    Returns the analysis results if completed, or status if still processing.
    """
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Analysis job not found")

    job_data = analysis_jobs[job_id]

    # Convert dict to Pydantic models if present
    content = None
    tech_stack = None

    if job_data["content"]:
        content = WebsiteContentData(**job_data["content"])
    if job_data["tech_stack"]:
        tech_stack = TechStackData(**job_data["tech_stack"])

    return WebsiteAnalysisResult(
        job_id=job_data["job_id"],
        status=job_data["status"],
        url=job_data["url"],
        content=content,
        tech_stack=tech_stack,
        screenshot_url=job_data["screenshot_url"],
        error=job_data["error"],
        completed_at=job_data["completed_at"]
    )


@router.post("/market", response_model=MarketAnalysisResponse)
async def analyze_market(
    request: MarketAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze market size and trends with geographic filtering.

    Supports geographies: poland, europe, cee, global
    """
    import uuid

    industry = request.industry.lower()
    geography = request.geography.value

    # Get data based on geography
    if geography == "poland":
        data_source = POLAND_MARKET_DATA
    else:
        data_source = EUROPE_MARKET_DATA

    # Get industry data or default
    if industry in data_source:
        market_data = data_source[industry]
    else:
        # Default to manufacturing if industry not found
        market_data = data_source.get("manufacturing", [])

    return MarketAnalysisResponse(
        id=str(uuid.uuid4()),
        industry=industry,
        geography=geography,
        status="completed",
        data=market_data,
        insights=get_market_insights(industry, geography),
        trends=get_market_trends(industry, geography)
    )


@router.post("/competitive")
async def analyze_competition(company_id: str):
    """Analyze competitive landscape."""
    # TODO: Implement competitive analysis
    return {
        "status": "processing",
        "job_id": "job_125"
    }


@router.post("/framework/{framework_type}")
async def apply_framework(framework_type: str, company_id: str):
    """Apply strategic framework (SWOT, Porter, PESTLE)."""
    # TODO: Implement framework application
    return {
        "framework": framework_type,
        "status": "processing",
        "job_id": "job_126"
    }


# Mock SWOT data for different companies
SWOT_DATA = {
    "fado": {
        "company_name": "FADO Sp. z o.o.",
        "strengths": [
            {"title": "Silna pozycja rynkowa", "description": "Lider w segmencie tworzyw sztucznych w Polsce"},
            {"title": "Doświadczony zespół", "description": "Kadra z wieloletnim doświadczeniem w branży"},
            {"title": "Nowoczesne technologie", "description": "Inwestycje w automatyzację i R&D"},
            {"title": "Szeroka sieć dystrybucji", "description": "Obecność w całej Polsce i eksport do UE"},
        ],
        "weaknesses": [
            {"title": "Zależność od dostawców", "description": "Ograniczona liczba kluczowych dostawców surowców"},
            {"title": "Koszty energii", "description": "Wysoki udział kosztów energii w produkcji"},
            {"title": "Rotacja pracowników", "description": "Wyzwania z utrzymaniem wykwalifikowanej kadry"},
        ],
        "opportunities": [
            {"title": "Zielona transformacja", "description": "Rosnący popyt na produkty ekologiczne"},
            {"title": "Ekspansja zagraniczna", "description": "Potencjał rozwoju na rynkach CEE"},
            {"title": "Nowe segmenty", "description": "Możliwość wejścia w sektor medyczny"},
            {"title": "Digitalizacja", "description": "Automatyzacja procesów i Przemysł 4.0"},
        ],
        "threats": [
            {"title": "Konkurencja cenowa", "description": "Presja ze strony tanich importerów z Azji"},
            {"title": "Regulacje środowiskowe", "description": "Zaostrzające się wymogi UE dot. tworzyw"},
            {"title": "Wahania cen surowców", "description": "Niestabilność cen ropy i pochodnych"},
        ],
    },
    "default": {
        "company_name": "Przykładowa firma",
        "strengths": [
            {"title": "Mocna strona 1", "description": "Opis mocnej strony firmy"},
            {"title": "Mocna strona 2", "description": "Kolejny atut przedsiębiorstwa"},
        ],
        "weaknesses": [
            {"title": "Słaba strona 1", "description": "Opis słabości do poprawy"},
            {"title": "Słaba strona 2", "description": "Kolejny obszar wymagający uwagi"},
        ],
        "opportunities": [
            {"title": "Szansa 1", "description": "Możliwość rozwoju biznesu"},
            {"title": "Szansa 2", "description": "Kolejna okazja rynkowa"},
        ],
        "threats": [
            {"title": "Zagrożenie 1", "description": "Ryzyko zewnętrzne"},
            {"title": "Zagrożenie 2", "description": "Kolejne potencjalne zagrożenie"},
        ],
    }
}


class SWOTItem(BaseModel):
    title: str
    description: str


class SWOTAnalysisResponse(BaseModel):
    company_name: str
    strengths: List[SWOTItem]
    weaknesses: List[SWOTItem]
    opportunities: List[SWOTItem]
    threats: List[SWOTItem]


@router.get("/swot/{company_id}", response_model=SWOTAnalysisResponse)
async def get_swot_analysis(
    company_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get SWOT analysis for a company."""
    # Use company-specific data if available, otherwise use default
    company_key = company_id.lower().replace("_", "").replace("-", "")
    if "fado" in company_key:
        swot_data = SWOT_DATA["fado"]
    else:
        swot_data = SWOT_DATA["default"]
        swot_data["company_name"] = f"Analiza SWOT - {company_id}"

    return SWOTAnalysisResponse(
        company_name=swot_data["company_name"],
        strengths=[SWOTItem(**s) for s in swot_data["strengths"]],
        weaknesses=[SWOTItem(**w) for w in swot_data["weaknesses"]],
        opportunities=[SWOTItem(**o) for o in swot_data["opportunities"]],
        threats=[SWOTItem(**t) for t in swot_data["threats"]]
    )


@router.get("/job/{job_id}")
async def get_analysis_job(job_id: str):
    """Get analysis job status and results."""
    # TODO: Implement job status retrieval
    return {
        "job_id": job_id,
        "status": "completed",
        "progress": 100,
        "results": {}
    }


class FactSource(BaseModel):
    name: str
    type: str
    value: Any
    date: Optional[str] = None


class FactCheckRequest(BaseModel):
    company_name: str
    facts: Dict[str, Dict[str, Any]]


class FactCheckResponse(BaseModel):
    fact_check_report: Dict[str, Any]


@router.post("/fact-check", response_model=FactCheckResponse)
async def check_facts(
    request: FactCheckRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Verify data accuracy through cross-referencing multiple sources.

    Assigns confidence scores (HIGH/MEDIUM/LOW/UNVERIFIED) and detects conflicts.

    Example request:
    {
        "company_name": "FADO Sp. z o.o.",
        "facts": {
            "employee_count": {
                "sources": [
                    {"name": "LinkedIn", "type": "social_media", "value": "245", "date": "2024-01-15"},
                    {"name": "Website", "type": "company_website", "value": "250+", "date": "2024-01-10"},
                    {"name": "GUS estimate", "type": "official_registry", "value": "200-300", "date": "2023-12-01"}
                ]
            },
            "revenue_2023": {
                "sources": [
                    {"name": "KRS Financial Report", "type": "official_registry", "value": "50.2M PLN", "date": "2024-03-15"}
                ]
            }
        }
    }
    """
    from app.services.fact_checker import fact_checker

    # Add company name to request data
    company_data = request.facts.copy()
    company_data["company_name"] = request.company_name

    # Run fact checking
    result = fact_checker.check_company_profile(company_data)

    return FactCheckResponse(**result)


class InsightGenerationRequest(BaseModel):
    company_name: str
    financial_data: Optional[Dict[str, Any]] = None
    market_data: Optional[Dict[str, Any]] = None
    digital_data: Optional[Dict[str, Any]] = None
    competitor_data: Optional[Dict[str, Any]] = None


class InsightGenerationResponse(BaseModel):
    insights_report: Dict[str, Any]


@router.post("/generate-insights", response_model=InsightGenerationResponse)
async def generate_insights(
    request: InsightGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate actionable insights, recommendations, and risk assessment from company data.

    Analyzes financial health, market position, digital presence, and competitive landscape
    to produce data-backed insights and specific recommendations.

    Example request:
    {
        "company_name": "FADO Sp. z o.o.",
        "financial_data": {
            "revenue": 50200000,
            "revenue_growth": 25.5,
            "profit_margin": 18.2,
            "debt_to_equity": 0.8,
            "liquidity_ratio": 2.1
        },
        "market_data": {
            "market_share": 15.5,
            "market_growth": 12.3,
            "competitor_count": 45,
            "market_size": 500000000
        },
        "digital_data": {
            "website_traffic": 85000,
            "social_media_followers": 12500,
            "seo_score": 72,
            "mobile_responsive": true
        }
    }
    """
    from app.services.insight_generator import insight_generator

    # Generate insights report
    result = insight_generator.generate_insights_report(
        company_name=request.company_name,
        financial_data=request.financial_data,
        market_data=request.market_data,
        digital_data=request.digital_data,
        competitor_data=request.competitor_data
    )

    return InsightGenerationResponse(**result)


# ==================== REPORT COMPOSER ENDPOINT ====================

class ReportComposeRequest(BaseModel):
    """Request to compose a comprehensive report"""
    company_name: str
    sections: Dict[str, Any]
    include_sources: bool = True
    language: str = "pl"

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "ACME Corp Sp. z o.o.",
                "sections": {
                    "company_profile": {
                        "legal_form": "Spółka z ograniczoną odpowiedzialnością",
                        "founded_year": 2015,
                        "industry": "Produkcja tworzyw sztucznych",
                        "nip": "1234567890",
                        "krs": "0000123456"
                    },
                    "financial_analysis": {
                        "metrics": {
                            "revenue": 15000000,
                            "revenue_growth": 22.5,
                            "profit_margin": 15.2,
                            "debt_to_equity": 0.8,
                            "current_ratio": 2.1
                        }
                    },
                    "insights": [
                        {
                            "title": "Silny wzrost przychodów",
                            "description": "Firma notuje 22.5% wzrost przychodów rok do roku",
                            "type": "opportunity",
                            "impact": "high",
                            "data_backed": True
                        }
                    ],
                    "opportunities": [
                        {
                            "title": "Ekspansja na rynek CEE",
                            "description": "Możliwość wejścia na rynki Europy Środkowo-Wschodniej",
                            "impact": "high",
                            "timeline": "medium_term"
                        }
                    ],
                    "risks": [
                        {
                            "title": "Rosnąca konkurencja",
                            "description": "Wzrost liczby konkurentów w segmencie",
                            "severity": "medium",
                            "likelihood": "high"
                        }
                    ],
                    "recommendations": [
                        {
                            "title": "Inwestycja w automatyzację",
                            "description": "Zwiększenie wydajności poprzez automatyzację linii produkcyjnych",
                            "priority": "high",
                            "timeline": "short_term"
                        }
                    ]
                },
                "include_sources": True,
                "language": "pl"
            }
        }


class ReportComposeResponse(BaseModel):
    """Response with composed report"""
    title: str
    subtitle: str
    generated_at: str
    company_name: str
    language: str
    executive_summary: Dict[str, Any]
    table_of_contents: List[Dict[str, Any]]
    sections: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@router.post(
    "/compose-report",
    response_model=ReportComposeResponse,
    summary="Compose comprehensive report",
    description="""
    Compose a comprehensive, well-structured report from multiple agent outputs.

    Features:
    - Aggregates sections from different analysis agents
    - Generates executive summary
    - Creates table of contents
    - Formats source citations
    - Ensures professional structure

    Test Steps (Feature #158):
    1. Run comprehensive analysis
    2. Verify report composer runs
    3. Verify all sections included
    4. Verify table of contents generated
    5. Verify sources cited throughout
    """
)
async def compose_report(
    request: ReportComposeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Compose a comprehensive report from multiple agent outputs.

    This endpoint aggregates data from various analysis agents (company profile,
    financial analysis, market analysis, insights, etc.) and composes a cohesive,
    well-structured report with:
    - Executive summary
    - Table of contents
    - All provided sections in logical order
    - Source citations
    - Professional formatting

    Example usage:
    ```python
    response = requests.post("/api/v1/analysis/compose-report", json={
        "company_name": "ACME Corp",
        "sections": {
            "company_profile": {...},
            "financial_analysis": {...},
            "insights": [...],
            "recommendations": [...]
        },
        "include_sources": True,
        "language": "pl"
    })
    ```
    """
    from app.services.report_composer import ReportComposerService

    # Initialize composer service
    composer = ReportComposerService()

    # Compose report
    report = composer.compose_report(
        company_name=request.company_name,
        sections=request.sections,
        include_sources=request.include_sources,
        language=request.language
    )

    return ReportComposeResponse(**report)
