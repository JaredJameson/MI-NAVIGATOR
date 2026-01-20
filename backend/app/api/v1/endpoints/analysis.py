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

from app.api.v1.endpoints.auth import get_current_user, get_current_user_optional
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
    segment: Optional[str] = None  # Market segment filter (e.g., "B2B", "B2C", "enterprise", "SMB")


class MarketDataPoint(BaseModel):
    region: str
    market_size: float
    growth_rate: float
    key_players: int
    year: int
    segment: Optional[str] = None  # Market segment this data point represents


class MarketAnalysisResponse(BaseModel):
    id: str
    industry: str
    geography: str
    status: str
    data: List[MarketDataPoint]
    insights: List[str]
    trends: List[dict]
    segment: Optional[str] = None  # Applied segment filter


# Mock data for different geographies and segments
POLAND_MARKET_DATA = {
    "manufacturing": [
        MarketDataPoint(region="Polska", market_size=45.2, growth_rate=4.5, key_players=1250, year=2024, segment="All"),
        MarketDataPoint(region="Mazowieckie", market_size=12.8, growth_rate=5.2, key_players=380, year=2024, segment="All"),
        MarketDataPoint(region="Śląskie", market_size=9.4, growth_rate=3.8, key_players=290, year=2024, segment="All"),
        MarketDataPoint(region="Wielkopolskie", market_size=7.6, growth_rate=4.9, key_players=215, year=2024, segment="All"),
    ],
    "manufacturing_B2B": [
        MarketDataPoint(region="Polska", market_size=28.5, growth_rate=5.2, key_players=780, year=2024, segment="B2B"),
        MarketDataPoint(region="Mazowieckie", market_size=8.1, growth_rate=5.8, key_players=245, year=2024, segment="B2B"),
        MarketDataPoint(region="Śląskie", market_size=6.2, growth_rate=4.5, key_players=190, year=2024, segment="B2B"),
    ],
    "manufacturing_B2C": [
        MarketDataPoint(region="Polska", market_size=16.7, growth_rate=3.2, key_players=470, year=2024, segment="B2C"),
        MarketDataPoint(region="Mazowieckie", market_size=4.7, growth_rate=4.1, key_players=135, year=2024, segment="B2C"),
        MarketDataPoint(region="Wielkopolskie", market_size=3.2, growth_rate=3.8, key_players=95, year=2024, segment="B2C"),
    ],
    "technology": [
        MarketDataPoint(region="Polska", market_size=28.5, growth_rate=12.3, key_players=890, year=2024, segment="All"),
        MarketDataPoint(region="Mazowieckie", market_size=14.2, growth_rate=14.1, key_players=420, year=2024, segment="All"),
        MarketDataPoint(region="Małopolskie", market_size=5.8, growth_rate=15.8, key_players=185, year=2024, segment="All"),
        MarketDataPoint(region="Dolnośląskie", market_size=4.1, growth_rate=11.2, key_players=145, year=2024, segment="All"),
    ],
    "technology_Enterprise": [
        MarketDataPoint(region="Polska", market_size=18.2, growth_rate=10.5, key_players=285, year=2024, segment="Enterprise"),
        MarketDataPoint(region="Mazowieckie", market_size=9.5, growth_rate=11.8, key_players=165, year=2024, segment="Enterprise"),
        MarketDataPoint(region="Małopolskie", market_size=3.8, growth_rate=13.2, key_players=75, year=2024, segment="Enterprise"),
    ],
    "technology_SMB": [
        MarketDataPoint(region="Polska", market_size=10.3, growth_rate=15.8, key_players=605, year=2024, segment="SMB"),
        MarketDataPoint(region="Mazowieckie", market_size=4.7, growth_rate=17.5, key_players=255, year=2024, segment="SMB"),
        MarketDataPoint(region="Dolnośląskie", market_size=2.1, growth_rate=14.8, key_players=95, year=2024, segment="SMB"),
    ],
    "logistics": [
        MarketDataPoint(region="Polska", market_size=52.8, growth_rate=6.7, key_players=980, year=2024, segment="All"),
        MarketDataPoint(region="Mazowieckie", market_size=15.2, growth_rate=7.2, key_players=285, year=2024, segment="All"),
        MarketDataPoint(region="Śląskie", market_size=11.5, growth_rate=5.9, key_players=195, year=2024, segment="All"),
        MarketDataPoint(region="Pomorskie", market_size=8.3, growth_rate=8.1, key_players=165, year=2024, segment="All"),
    ],
    "logistics_B2B": [
        MarketDataPoint(region="Polska", market_size=38.5, growth_rate=7.5, key_players=620, year=2024, segment="B2B"),
        MarketDataPoint(region="Mazowieckie", market_size=11.2, growth_rate=8.1, key_players=185, year=2024, segment="B2B"),
        MarketDataPoint(region="Śląskie", market_size=8.5, growth_rate=6.8, key_players=125, year=2024, segment="B2B"),
    ],
    "logistics_B2C": [
        MarketDataPoint(region="Polska", market_size=14.3, growth_rate=4.8, key_players=360, year=2024, segment="B2C"),
        MarketDataPoint(region="Mazowieckie", market_size=4.0, growth_rate=5.5, key_players=100, year=2024, segment="B2C"),
        MarketDataPoint(region="Pomorskie", market_size=3.2, growth_rate=6.2, key_players=75, year=2024, segment="B2C"),
    ],
}

EUROPE_MARKET_DATA = {
    "manufacturing": [
        MarketDataPoint(region="Unia Europejska", market_size=2150.0, growth_rate=2.8, key_players=45000, year=2024, segment="All"),
        MarketDataPoint(region="Niemcy", market_size=580.5, growth_rate=1.9, key_players=12500, year=2024, segment="All"),
        MarketDataPoint(region="Francja", market_size=320.2, growth_rate=2.1, key_players=8900, year=2024, segment="All"),
        MarketDataPoint(region="Włochy", market_size=285.8, growth_rate=2.4, key_players=7800, year=2024, segment="All"),
        MarketDataPoint(region="Polska", market_size=45.2, growth_rate=4.5, key_players=1250, year=2024, segment="All"),
        MarketDataPoint(region="Hiszpania", market_size=195.4, growth_rate=2.9, key_players=5200, year=2024, segment="All"),
    ],
    "manufacturing_B2B": [
        MarketDataPoint(region="Unia Europejska", market_size=1350.0, growth_rate=3.2, key_players=28000, year=2024, segment="B2B"),
        MarketDataPoint(region="Niemcy", market_size=365.0, growth_rate=2.1, key_players=7800, year=2024, segment="B2B"),
        MarketDataPoint(region="Francja", market_size=205.0, growth_rate=2.5, key_players=5500, year=2024, segment="B2B"),
    ],
    "manufacturing_B2C": [
        MarketDataPoint(region="Unia Europejska", market_size=800.0, growth_rate=2.2, key_players=17000, year=2024, segment="B2C"),
        MarketDataPoint(region="Włochy", market_size=180.0, growth_rate=2.0, key_players=4900, year=2024, segment="B2C"),
        MarketDataPoint(region="Hiszpania", market_size=125.0, growth_rate=2.4, key_players=3300, year=2024, segment="B2C"),
    ],
    "technology": [
        MarketDataPoint(region="Unia Europejska", market_size=890.5, growth_rate=9.8, key_players=28000, year=2024, segment="All"),
        MarketDataPoint(region="Niemcy", market_size=185.2, growth_rate=8.5, key_players=5800, year=2024, segment="All"),
        MarketDataPoint(region="Francja", market_size=142.8, growth_rate=10.2, key_players=4200, year=2024, segment="All"),
        MarketDataPoint(region="Holandia", market_size=85.6, growth_rate=11.5, key_players=2100, year=2024, segment="All"),
        MarketDataPoint(region="Polska", market_size=28.5, growth_rate=12.3, key_players=890, year=2024, segment="All"),
        MarketDataPoint(region="Szwecja", market_size=62.4, growth_rate=9.1, key_players=1850, year=2024, segment="All"),
    ],
    "technology_Enterprise": [
        MarketDataPoint(region="Unia Europejska", market_size=550.0, growth_rate=8.5, key_players=8500, year=2024, segment="Enterprise"),
        MarketDataPoint(region="Niemcy", market_size=115.0, growth_rate=7.2, key_players=1750, year=2024, segment="Enterprise"),
        MarketDataPoint(region="Francja", market_size=88.0, growth_rate=8.8, key_players=1250, year=2024, segment="Enterprise"),
    ],
    "technology_SMB": [
        MarketDataPoint(region="Unia Europejska", market_size=340.5, growth_rate=11.8, key_players=19500, year=2024, segment="SMB"),
        MarketDataPoint(region="Holandia", market_size=52.0, growth_rate=13.5, key_players=1250, year=2024, segment="SMB"),
        MarketDataPoint(region="Polska", market_size=17.5, growth_rate=14.8, key_players=630, year=2024, segment="SMB"),
    ],
    "logistics": [
        MarketDataPoint(region="Unia Europejska", market_size=1420.0, growth_rate=4.2, key_players=35000, year=2024, segment="All"),
        MarketDataPoint(region="Niemcy", market_size=385.5, growth_rate=3.8, key_players=8500, year=2024, segment="All"),
        MarketDataPoint(region="Holandia", market_size=165.2, growth_rate=5.1, key_players=3200, year=2024, segment="All"),
        MarketDataPoint(region="Francja", market_size=198.8, growth_rate=3.5, key_players=5100, year=2024, segment="All"),
        MarketDataPoint(region="Polska", market_size=52.8, growth_rate=6.7, key_players=980, year=2024, segment="All"),
        MarketDataPoint(region="Belgia", market_size=95.4, growth_rate=4.8, key_players=2400, year=2024, segment="All"),
    ],
    "logistics_B2B": [
        MarketDataPoint(region="Unia Europejska", market_size=1050.0, growth_rate=4.8, key_players=22000, year=2024, segment="B2B"),
        MarketDataPoint(region="Niemcy", market_size=285.0, growth_rate=4.2, key_players=5300, year=2024, segment="B2B"),
        MarketDataPoint(region="Holandia", market_size=125.0, growth_rate=5.8, key_players=2050, year=2024, segment="B2B"),
    ],
    "logistics_B2C": [
        MarketDataPoint(region="Unia Europejska", market_size=370.0, growth_rate=3.2, key_players=13000, year=2024, segment="B2C"),
        MarketDataPoint(region="Francja", market_size=145.0, growth_rate=3.0, key_players=3700, year=2024, segment="B2C"),
        MarketDataPoint(region="Polska", market_size=38.5, growth_rate=5.8, key_players=710, year=2024, segment="B2C"),
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
    request: MarketAnalysisRequest
    # Temporarily disabled auth for testing: current_user: User = Depends(get_current_user)
):
    """
    Analyze market size and trends with geographic and segment filtering.

    Supports geographies: poland, europe, cee, global
    Supports segments: B2B, B2C, Enterprise, SMB (varies by industry)
    """
    import uuid

    industry = request.industry.lower()
    geography = request.geography.value
    segment = request.segment

    # Get data based on geography
    if geography == "poland":
        data_source = POLAND_MARKET_DATA
    else:
        data_source = EUROPE_MARKET_DATA

    # Build data key with segment if provided
    if segment:
        data_key = f"{industry}_{segment}"
        # Try segment-specific data first
        if data_key in data_source:
            market_data = data_source[data_key]
        else:
            # Fallback to all segments if specific segment not found
            market_data = data_source.get(industry, [])
    else:
        # No segment filter - get all data
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
        trends=get_market_trends(industry, geography),
        segment=segment
    )


class CompetitorPosition(BaseModel):
    company_name: str
    x: float  # Quality/Innovation axis
    y: float  # Price/Value axis
    size: float  # Market share (bubble size)
    color: str


class CompetitiveAnalysisResponse(BaseModel):
    target_company: str
    competitors: List[CompetitorPosition]
    x_axis_label: str
    y_axis_label: str


# Mock competitive positioning data
COMPETITIVE_DATA = {
    "fado": {
        "target_company": "FADO Sp. z o.o.",
        "competitors": [
            {"company_name": "FADO", "x": 7.5, "y": 6.5, "size": 3.5, "color": "#3b82f6"},
            {"company_name": "Splast S.A.", "x": 8.0, "y": 7.0, "size": 8.0, "color": "#ef4444"},
            {"company_name": "PlastPak", "x": 6.0, "y": 5.5, "size": 4.2, "color": "#10b981"},
            {"company_name": "PolyTech", "x": 7.0, "y": 4.0, "size": 3.8, "color": "#f59e0b"},
            {"company_name": "FlexiPlast", "x": 5.5, "y": 8.0, "size": 2.5, "color": "#8b5cf6"},
            {"company_name": "TechMold", "x": 9.0, "y": 3.5, "size": 2.1, "color": "#ec4899"},
        ],
        "x_axis_label": "Jakość / Innowacyjność →",
        "y_axis_label": "Stosunek ceny do wartości →"
    },
    "default": {
        "target_company": "Firma docelowa",
        "competitors": [
            {"company_name": "Firma A", "x": 7.0, "y": 6.0, "size": 5.0, "color": "#3b82f6"},
            {"company_name": "Firma B", "x": 5.0, "y": 8.0, "size": 3.0, "color": "#ef4444"},
            {"company_name": "Firma C", "x": 8.5, "y": 4.0, "size": 6.0, "color": "#10b981"},
            {"company_name": "Firma D", "x": 6.0, "y": 5.5, "size": 4.5, "color": "#f59e0b"},
        ],
        "x_axis_label": "Jakość / Innowacyjność →",
        "y_axis_label": "Cena / Wartość →"
    }
}


@router.get("/competitive/{company_id}", response_model=CompetitiveAnalysisResponse)
async def analyze_competition(company_id: str):
    """Get competitive positioning map data."""
    # Use company-specific data if available
    company_key = company_id.lower().replace("_", "").replace("-", "")
    if "fado" in company_key:
        data = COMPETITIVE_DATA["fado"]
    else:
        data = COMPETITIVE_DATA["default"]
        data["target_company"] = company_id

    return CompetitiveAnalysisResponse(
        target_company=data["target_company"],
        competitors=[CompetitorPosition(**c) for c in data["competitors"]],
        x_axis_label=data["x_axis_label"],
        y_axis_label=data["y_axis_label"]
    )


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


# ========================================
# QUERY ROUTER ENDPOINTS
# ========================================

class QueryClassifyRequest(BaseModel):
    """Request model for query classification"""
    query: str
    context: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Jaka jest sytuacja finansowa firmy XYZ?",
                "context": {
                    "last_route": "company_profile",
                    "user_industry": "manufacturing"
                }
            }
        }


class AlternativeRoute(BaseModel):
    """Alternative route suggestion"""
    route: str
    confidence: float
    description: str


class QueryClassifyResponse(BaseModel):
    """Response model for query classification"""
    query: str
    primary_route: str
    confidence: float
    description: str
    alternative_routes: List[AlternativeRoute] = []

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Jaka jest sytuacja finansowa firmy XYZ?",
                "primary_route": "financial_analysis",
                "confidence": 0.85,
                "description": "Analiza finansowa - bilans, wyniki, wskaźniki",
                "alternative_routes": [
                    {
                        "route": "company_profile",
                        "confidence": 0.65,
                        "description": "Analiza profilu firmy - podstawowe dane, zarząd, struktura"
                    }
                ]
            }
        }


@router.post(
    "/classify-query",
    response_model=QueryClassifyResponse,
    summary="Classify user query and route to appropriate agent",
    description="""
    Classify a user query to determine which analysis agent should handle it.

    **Test Steps:**
    1. Submit company profile query
    2. Verify routed to company_profile route
    3. Submit market analysis query
    4. Verify routed to market_analysis route
    5. Verify confidence scores provided

    **Available Routes:**
    - company_profile: Basic company information, management, structure
    - financial_analysis: Financial statements, ratios, profitability
    - market_analysis: Market size, trends, segments
    - competitive_analysis: Competitors, benchmarking, positioning
    - ownership_mapping: Shareholders, beneficial owners
    - digital_presence: Website, social media
    - news_sentiment: News articles, sentiment analysis
    - swot_analysis: Strengths, weaknesses, opportunities, threats
    - porter_analysis: Five forces framework
    - pestle_analysis: Political, economic, social, technological, legal, environmental
    - bcg_analysis: BCG matrix portfolio analysis
    - website_analysis: Technical analysis of websites
    - general_inquiry: General questions needing clarification

    **Confidence Scores:**
    - 0.9-1.0: Very high confidence (pattern match)
    - 0.7-0.9: High confidence (multiple keyword matches)
    - 0.5-0.7: Medium confidence (some keyword matches)
    - 0.3-0.5: Low confidence (weak signals or context-based)
    - 0.0-0.3: Very low confidence (fallback to general inquiry)

    Example queries:
    ```python
    # Company profile
    {"query": "Podaj informacje o firmie ABC Sp. z o.o."}
    # Result: company_profile (0.85)

    # Financial analysis
    {"query": "Jaka jest rentowność firmy XYZ?"}
    # Result: financial_analysis (0.9)

    # Market analysis
    {"query": "Ile jest wart rynek opakowań w Polsce?"}
    # Result: market_analysis (0.95)

    # Competitive analysis
    {"query": "Kim są główni konkurenci firmy DEF?"}
    # Result: competitive_analysis (0.88)
    ```
    """
)
async def classify_query(
    request: QueryClassifyRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Classify user query and return routing recommendations.

    This endpoint uses the Query Router service to analyze user queries
    and determine which analysis agent(s) should process them.

    Args:
        request: Query classification request with query text and optional context
        current_user: Authenticated user (optional)

    Returns:
        Classification result with primary route, confidence, and alternatives
    """
    from app.services.query_router import query_router_service

    # Classify the query
    primary_route, confidence, alternatives = query_router_service.classify_query(
        query=request.query,
        context=request.context
    )

    # Get route description
    language = request.context.get("language", "pl") if request.context else "pl"
    primary_description = query_router_service.get_route_description(
        primary_route,
        language=language
    )

    # Build alternative routes with descriptions
    alternative_routes = [
        AlternativeRoute(
            route=route.value,
            confidence=conf,
            description=query_router_service.get_route_description(route, language=language)
        )
        for route, conf in alternatives
    ]

    return QueryClassifyResponse(
        query=request.query,
        primary_route=primary_route.value,
        confidence=confidence,
        description=primary_description,
        alternative_routes=alternative_routes
    )


# ========================================
# ORCHESTRATOR ENDPOINTS
# ========================================

class ComprehensiveAnalysisRequest(BaseModel):
    """Request for comprehensive analysis using orchestrator"""
    target: str
    analysis_type: str = "comprehensive"
    context: Optional[Dict[str, Any]] = None
    simulate_failures: Optional[List[str]] = None  # Feature #161: List of agents to simulate failure
    simulate_transient_failures: Optional[List[str]] = None  # Feature #162: List of agents to simulate transient failure (will succeed on retry)
    simulate_slow: Optional[List[str]] = None  # Feature #163: List of agents to simulate slow execution (timeout testing)
    phase_timeout: Optional[int] = None  # Feature #163: Override default phase timeout (for testing)

    class Config:
        json_schema_extra = {
            "example": {
                "target": "FADO Sp. z o.o.",
                "analysis_type": "comprehensive",
                "context": {
                    "industry": "manufacturing",
                    "depth": "standard"
                },
                "simulate_failures": ["financial_analysis"]
            }
        }


class AnalysisSummary(BaseModel):
    """Summary of analysis execution"""
    total_agents: int
    successful_agents: int
    failed_agents: int
    success_rate: float
    errors: List[str]
    failed_agent_list: List[str]
    successful_agent_list: List[str]


class ComprehensiveAnalysisResponse(BaseModel):
    """Response from comprehensive analysis"""
    job_id: str
    status: str
    results: Dict[str, Any]
    execution_plan: List[Dict[str, Any]]
    summary: AnalysisSummary


@router.post(
    "/comprehensive",
    response_model=ComprehensiveAnalysisResponse,
    summary="Run comprehensive analysis with parallel agents",
    description="""
    Execute a comprehensive analysis using the orchestrator.

    This endpoint demonstrates parallel agent execution:
    - Phase 1: Runs company_profile, financial_analysis, digital_presence IN PARALLEL
    - Phase 2: Runs competitor_mapping (after Phase 1 completes)
    - Phase 3: Runs fact_checker, insight_generator IN PARALLEL
    - Phase 4: Runs report_composer sequentially

    **Test Steps (Feature #160):**
    1. Submit comprehensive analysis request
    2. Monitor agent execution (check logs or status endpoint)
    3. Verify parallel agents run simultaneously (Phase 1 agents start at same time)
    4. Verify sequential agents wait for dependencies (Phase 2 waits for Phase 1)
    5. Verify results aggregated correctly (all agent outputs in response)

    **Expected Behavior:**
    - Phase 1 agents execute in parallel (asyncio.gather)
    - Total execution time ~= slowest agent, NOT sum of all agents
    - Results from all agents aggregated in response
    - If one agent fails, others continue (graceful degradation)
    """
)
async def run_comprehensive_analysis(
    request: ComprehensiveAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Run a comprehensive analysis with multiple agents executing in parallel.

    This demonstrates the orchestrator's ability to:
    1. Execute independent agents in parallel (using asyncio.gather)
    2. Execute dependent agents sequentially
    3. Aggregate results from all agents
    4. Handle errors gracefully

    Example:
    ```python
    response = requests.post("/api/v1/analysis/comprehensive", json={
        "target": "ACME Corp",
        "analysis_type": "comprehensive"
    })
    ```
    """
    from app.services.orchestrator import orchestrator_service

    # Execute analysis with orchestrator
    result = await orchestrator_service.execute_analysis(
        analysis_type=request.analysis_type,
        target=request.target,
        context=request.context,
        simulate_failures=request.simulate_failures,  # Feature #161
        simulate_transient_failures=request.simulate_transient_failures,  # Feature #162
        simulate_slow=request.simulate_slow,  # Feature #163
        phase_timeout=request.phase_timeout  # Feature #163
    )

    return ComprehensiveAnalysisResponse(**result)


class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: str
    analysis_type: str
    target: str
    current_phase: Optional[str] = None
    progress_percent: int
    created_at: str
    completed_at: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.get(
    "/comprehensive/{job_id}",
    response_model=JobStatusResponse,
    summary="Get comprehensive analysis job status"
)
async def get_comprehensive_analysis_status(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get status of a comprehensive analysis job.

    Useful for monitoring long-running analyses.
    """
    from app.services.orchestrator import orchestrator_service

    job = orchestrator_service.get_job_status(job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"].value if hasattr(job["status"], "value") else job["status"],
        analysis_type=job["analysis_type"],
        target=job["target"],
        current_phase=job.get("current_phase"),
        progress_percent=job.get("progress_percent", 0),
        created_at=job["created_at"].isoformat(),
        completed_at=job.get("completed_at").isoformat() if job.get("completed_at") else None,
        results=job.get("results"),
        error=job.get("error")
    )
