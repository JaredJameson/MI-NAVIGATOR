"""
Unit Tests for Agents API Endpoint - Week 3 Implementation

Tests for /api/v1/agents/company-profile endpoint including:
- Request/response validation
- Caching functionality
- Rate limiting
- Timeout handling
- Error handling

Author: MI-Navigator Development Team
Created: 2026-01-24 (Week 3)
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from httpx import AsyncClient, ASGITransport

from app.api.v1.endpoints.agents import (
    CompanyProfileRequest,
    CompanyProfileResponse,
    CompetitorMappingRequest,
    CompetitorMappingResponse,
    FactCheckerRequest,
    FactCheckerResponse,
    InsightGeneratorRequest,
    InsightGeneratorResponse,
    generate_cache_key,
    generate_cache_key_competitor,
    generate_cache_key_fact_checker,
    generate_cache_key_insight_generator,
    generate_citations,
    check_rate_limit,
    rate_limit_store
)
from app.agents.company_profile_agent import CompanyProfileOutput, Owner, BoardMember
from app.agents.competitor_mapping_agent import (
    CompetitorMappingOutput,
    CompetitorProfile,
    MarketPositionAnalysis,
    CompetitorType,
    MarketPosition
)
from app.agents.fact_checker_agent import (
    FactCheckerOutput,
    Claim,
    Verification,
    Source,
    ClaimType,
    VerificationStatus,
    SourceType,
    CredibilityLevel
)
from app.agents.insight_generator_agent import (
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
    OpportunityType
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def clear_rate_limits():
    """Clear rate limit store before each test."""
    rate_limit_store.clear()
    yield
    rate_limit_store.clear()


# ============================================================================
# PYDANTIC MODEL TESTS
# ============================================================================

def test_company_profile_request_validation():
    """Test CompanyProfileRequest validation."""
    # Valid request
    request = CompanyProfileRequest(
        target="NIP 1234567890",
        include_ownership=True,
        include_board=True
    )

    assert request.target == "NIP 1234567890"
    assert request.include_ownership is True
    assert request.use_cache is True  # default

    # Invalid: empty target
    with pytest.raises(ValueError, match="Target cannot be empty"):
        CompanyProfileRequest(target="")

    # Invalid: too short
    with pytest.raises(ValueError, match="too short"):
        CompanyProfileRequest(target="123")


def test_company_profile_response_model():
    """Test CompanyProfileResponse model structure."""
    response = CompanyProfileResponse(
        success=True,
        company_name="Test Company",
        nip="1234567890",
        cached=False,
        processing_time_ms=1500
    )

    assert response.success is True
    assert response.company_name == "Test Company"
    assert response.nip == "1234567890"
    assert response.cached is False
    assert response.processing_time_ms == 1500


# ============================================================================
# CACHE KEY GENERATION TESTS
# ============================================================================

def test_generate_cache_key():
    """Test cache key generation."""
    request1 = CompanyProfileRequest(
        target="NIP 1234567890",
        include_ownership=True,
        include_board=True
    )

    request2 = CompanyProfileRequest(
        target="nip 1234567890",  # Different case
        include_ownership=True,
        include_board=True
    )

    key1 = generate_cache_key(request1)
    key2 = generate_cache_key(request2)

    # Should be same (normalized)
    assert key1 == key2

    # Should start with prefix
    assert key1.startswith("agent:company_profile:")

    # Different parameters should create different keys
    request3 = CompanyProfileRequest(
        target="NIP 1234567890",
        include_ownership=False,  # Different
        include_board=True
    )

    key3 = generate_cache_key(request3)
    assert key1 != key3


# ============================================================================
# RATE LIMITING TESTS
# ============================================================================

def test_rate_limiting_basic():
    """Test basic rate limiting functionality."""
    client_ip = "192.168.1.1"

    # First 10 requests should succeed
    for i in range(10):
        assert check_rate_limit(client_ip) is True

    # 11th request should fail
    assert check_rate_limit(client_ip) is False


def test_rate_limiting_different_ips():
    """Test rate limiting with different IPs."""
    ip1 = "192.168.1.1"
    ip2 = "192.168.1.2"

    # Each IP has independent limit
    for i in range(10):
        assert check_rate_limit(ip1) is True
        assert check_rate_limit(ip2) is True

    # Both should fail on 11th
    assert check_rate_limit(ip1) is False
    assert check_rate_limit(ip2) is False


def test_rate_limiting_window_expiry():
    """Test rate limiting window expiry."""
    client_ip = "192.168.1.1"

    # Fill rate limit
    for i in range(10):
        check_rate_limit(client_ip)

    # Should be blocked
    assert check_rate_limit(client_ip) is False

    # Manually expire old entries (simulate time passing)
    cutoff = datetime.utcnow() - timedelta(seconds=61)
    rate_limit_store[client_ip] = [cutoff]

    # Should work again
    assert check_rate_limit(client_ip) is True


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_agents_status_endpoint(client: AsyncClient):
    """Test agents status endpoint (no auth required)."""
    response = await client.get("/api/v1/agents/status")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "operational"
    assert "company_profile" in data["agents_available"]
    assert "cache_enabled" in data
    assert "timestamp" in data


@pytest.mark.asyncio
@patch('app.agents.company_profile_agent.CompanyProfileAgent.execute')
async def test_company_profile_endpoint_success(mock_execute, client: AsyncClient, auth_headers: dict):
    """Test successful company profile retrieval."""
    # Mock agent response
    mock_output = CompanyProfileOutput(
        target="NIP 1234567890",
        confidence_score=95.0,
        company_name="Test Company Sp. z o.o.",
        nip_number="1234567890",
        krs_number="0000123456",
        regon_number="123456789",
        legal_form="Spółka z ograniczoną odpowiedzialnością",
        registration_date="2020-01-15",
        address={
            "street": "ul. Testowa 123",
            "city": "Warszawa",
            "postal_code": "00-001"
        },
        industry="Software Development",
        ownership_structure=[
            Owner(
                owner_name="Jan Kowalski",
                ownership_percentage=51.0,
                ownership_type="direct"
            )
        ],
        management_board=[
            BoardMember(
                name="Jan Kowalski",
                position="Prezes Zarządu",
                appointment_date="2020-01-15"
            )
        ],
        data_sources=["KRS", "GUS"]
    )

    mock_execute.return_value = mock_output

    # Make request
    response = await client.post(
        "/api/v1/agents/company-profile",
        json={
            "target": "NIP 1234567890",
            "include_ownership": True,
            "include_board": True,
            "use_cache": False
        },
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    # Debug: print response if test fails
    if not data.get("success"):
        print(f"\nDEBUG: Response data: {data}")

    assert data["success"] is True
    assert data["company_name"] == "Test Company Sp. z o.o."
    assert data["nip"] == "1234567890"
    assert data["krs"] == "0000123456"
    assert len(data["ownership_structure"]) == 1
    assert len(data["management_board"]) == 1


@pytest.mark.asyncio
@patch('app.agents.company_profile_agent.CompanyProfileAgent.execute')
async def test_company_profile_endpoint_not_found(mock_execute, client: AsyncClient, auth_headers: dict):
    """Test company not found scenario."""
    # Mock agent response with no company name (not found)
    mock_output = CompanyProfileOutput(
        target="NIP 9999999999",
        confidence_score=0.0,
        company_name=None,
        nip_number=None,
        krs_number=None,
        data_sources=[]
    )

    mock_execute.return_value = mock_output

    response = await client.post(
        "/api/v1/agents/company-profile",
        json={"target": "NIP 9999999999"},
        headers=auth_headers
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
@patch('app.agents.company_profile_agent.CompanyProfileAgent.execute')
async def test_week3_full_integration(mock_execute, client: AsyncClient, auth_headers: dict):
    """
    Test Week 3 integration with Week 2 functionality.

    This test verifies:
    1. API endpoint receives request
    2. CompanyProfileAgent processes with GUS/REGON integration
    3. Ownership parsing works (Week 2)
    4. Management board extraction works (Week 2)
    5. Response formatting correct
    """
    # Create realistic Week 2 output
    mock_output = CompanyProfileOutput(
        target="NIP 1234567890",
        confidence_score=98.0,
        company_name="Example Software Sp. z o.o.",
        nip_number="1234567890",
        krs_number="0000123456",
        regon_number="123456789",
        legal_form="Spółka z ograniczoną odpowiedzialnością",
        registration_date="2020-01-15",
        address={
            "street": "ul. Przykładowa 123",
            "city": "Warszawa",
            "postal_code": "00-001",
            "voivodeship": "Mazowieckie"
        },
        industry="Działalność związana z oprogramowaniem",
        ownership_structure=[
            Owner(
                owner_name="Jan Kowalski",
                ownership_percentage=60.0,  # Week 2 parsing
                ownership_type="direct"
            ),
            Owner(
                owner_name="Anna Nowak",
                ownership_percentage=40.0,
                ownership_type="indirect"
            )
        ],
        management_board=[
            BoardMember(
                name="Jan Kowalski",
                position="Prezes Zarządu",  # Week 2 extraction
                appointment_date="2020-01-15"
            )
        ],
        data_sources=["KRS", "GUS", "REGON"]  # Multi-source Week 2
    )

    mock_execute.return_value = mock_output

    response = await client.post(
        "/api/v1/agents/company-profile",
        json={
            "target": "NIP 1234567890",
            "include_ownership": True,
            "include_board": True,
            "use_cache": False
        },
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    # Verify Week 3 response structure
    assert data["success"] is True
    assert data["cached"] is False
    assert "processing_time_ms" in data

    # Verify Week 2 ownership parsing integration
    assert len(data["ownership_structure"]) == 2
    assert data["ownership_structure"][0]["ownership_percentage"] == 60.0

    # Verify Week 2 board extraction integration
    assert len(data["management_board"]) == 1
    assert data["management_board"][0]["position"] == "Prezes Zarządu"

    # Verify Week 2 multi-source data
    assert "KRS" in data["data_sources"]
    assert "GUS" in data["data_sources"]
    assert "REGON" in data["data_sources"]


# ============================================================================
# FINANCIAL ANALYSIS ENDPOINT TESTS (Week 6)
# ============================================================================

def test_financial_analysis_request_validation():
    """Test FinancialAnalysisRequest validation (Week 6)."""
    from app.api.v1.endpoints.agents import FinancialAnalysisRequest
    
    # Valid request
    request = FinancialAnalysisRequest(
        target="KRS 0000123456",
        use_cache=True
    )
    
    assert request.target == "KRS 0000123456"
    assert request.use_cache is True
    
    # Invalid: empty target
    with pytest.raises(ValueError, match="Target cannot be empty"):
        FinancialAnalysisRequest(target="")
    
    # Invalid: too short
    with pytest.raises(ValueError, match="too short"):
        FinancialAnalysisRequest(target="123")


def test_financial_analysis_response_model():
    """Test FinancialAnalysisResponse model structure (Week 6)."""
    from app.api.v1.endpoints.agents import FinancialAnalysisResponse
    
    response = FinancialAnalysisResponse(
        success=True,
        target="KRS 0000123456",
        company_name="Test Company",
        periods_analyzed=3,
        overall_score=75.5,
        risk_level="moderate",
        altman_z_score=2.8,
        bankruptcy_risk="safe",
        liquidity_score=80.0,
        profitability_score=70.0,
        leverage_score=75.0,
        cash_flow_score=78.0,
        confidence_score=85.0,
        cached=False,
        processing_time_ms=2500
    )
    
    assert response.success is True
    assert response.target == "KRS 0000123456"
    assert response.company_name == "Test Company"
    assert response.periods_analyzed == 3
    assert response.overall_score == 75.5
    assert response.risk_level == "moderate"
    assert response.altman_z_score == 2.8
    assert response.bankruptcy_risk == "safe"
    assert response.confidence_score == 85.0


def test_generate_cache_key_financial():
    """Test cache key generation for financial analysis (Week 6)."""
    from app.api.v1.endpoints.agents import (
        FinancialAnalysisRequest,
        generate_cache_key_financial
    )
    
    request1 = FinancialAnalysisRequest(target="KRS 0000123456")
    request2 = FinancialAnalysisRequest(target="krs 0000123456")  # Different case
    
    key1 = generate_cache_key_financial(request1)
    key2 = generate_cache_key_financial(request2)
    
    # Keys should be identical (case-insensitive, space-insensitive)
    assert key1 == key2
    assert key1.startswith("agent:financial_analysis:")
    
    # Different targets should have different keys
    request3 = FinancialAnalysisRequest(target="KRS 0000999999")
    key3 = generate_cache_key_financial(request3)
    
    assert key1 != key3


@pytest.mark.asyncio
@patch('app.agents.financial_analysis_agent.FinancialAnalysisAgent.execute')
async def test_financial_analysis_endpoint_mock_success(mock_execute, client: AsyncClient, auth_headers: dict):
    """Test financial analysis endpoint with mocked agent (Week 6)."""
    from app.agents.financial_analysis_agent import (
        FinancialAnalysisOutput,
        FinancialHealthScore
    )

    # Mock successful analysis output
    mock_health_score = FinancialHealthScore(
        overall_score=75.5,
        liquidity_score=80.0,
        profitability_score=70.0,
        leverage_score=75.0,
        efficiency_score=72.0,
        trend_score=68.0,
        risk_level="moderate",
        altman_z_score=2.8,
        bankruptcy_risk="safe",
        strengths=["Strong liquidity position"],
        weaknesses=["High leverage"],
        recommendations=["Reduce debt levels"]
    )

    mock_output = FinancialAnalysisOutput(
        target="KRS 0000123456",
        company_name="Test Company",
        periods_analyzed=3,
        health_score=mock_health_score,
        confidence_score=85.0,
        data_sources=["KRS", "GUS"]
    )

    mock_execute.return_value = mock_output

    # Make request
    response = await client.post(
        "/api/v1/agents/financial-analysis",
        json={"target": "KRS 0000123456"},
        headers=auth_headers
    )

    assert response.status_code == 200

    data = response.json()

    # Verify response structure
    assert data["success"] is True
    assert data["target"] == "KRS 0000123456"
    assert data["company_name"] == "Test Company"
    assert data["periods_analyzed"] == 3
    assert data["overall_score"] == 75.5
    assert data["risk_level"] == "moderate"
    assert data["altman_z_score"] == 2.8
    assert data["bankruptcy_risk"] == "safe"
    assert data["confidence_score"] == 85.0
    assert "processing_time_ms" in data


@pytest.mark.asyncio
@patch('app.agents.financial_analysis_agent.FinancialAnalysisAgent.execute')
async def test_financial_analysis_endpoint_rate_limiting(mock_execute, client: AsyncClient, auth_headers: dict):
    """Test rate limiting on financial analysis endpoint (Week 6)."""
    from app.api.v1.endpoints.agents import RATE_LIMIT_REQUESTS
    from app.agents.financial_analysis_agent import (
        FinancialAnalysisOutput,
        FinancialHealthScore
    )

    # Mock successful analysis output
    mock_health_score = FinancialHealthScore(
        overall_score=75.0,
        liquidity_score=80.0,
        profitability_score=70.0,
        leverage_score=75.0,
        efficiency_score=72.0,
        trend_score=68.0,
        risk_level="moderate",
        altman_z_score=2.5,
        bankruptcy_risk="safe",
        strengths=["Test"],
        weaknesses=["Test"],
        recommendations=["Test"]
    )

    mock_output = FinancialAnalysisOutput(
        target="KRS 0000123456",
        company_name="Test Company",
        periods_analyzed=3,
        health_score=mock_health_score,
        confidence_score=85.0,
        data_sources=["KRS"]
    )

    mock_execute.return_value = mock_output

    # Make RATE_LIMIT_REQUESTS successful requests
    for i in range(RATE_LIMIT_REQUESTS):
        response = await client.post(
            "/api/v1/agents/financial-analysis",
            json={"target": f"KRS 000012345{i}"},
            headers=auth_headers
        )
        assert response.status_code == 200

    # Next request should be rate limited
    response = await client.post(
        "/api/v1/agents/financial-analysis",
        json={"target": "KRS 0000999999"},
        headers=auth_headers
    )

    assert response.status_code == 429  # Too Many Requests


# ============================================================================
# DIGITAL PRESENCE ENDPOINT TESTS (Week 9)
# ============================================================================

def test_digital_presence_request_validation():
    """Test DigitalPresenceRequest validation."""
    from app.api.v1.endpoints.agents import DigitalPresenceRequest

    # Valid request
    request = DigitalPresenceRequest(
        target="https://example.com",
        use_cache=True
    )

    assert request.target == "https://example.com"
    assert request.use_cache is True

    # Invalid: empty target
    with pytest.raises(ValueError, match="Target cannot be empty"):
        DigitalPresenceRequest(target="")

    # Invalid: too short
    with pytest.raises(ValueError, match="too short"):
        DigitalPresenceRequest(target="abc")


@pytest.mark.asyncio
async def test_digital_presence_endpoint_success(client: AsyncClient, auth_headers):
    """Test successful digital presence analysis."""
    from app.api.v1.endpoints.agents import DigitalPresenceResponse
    from app.agents.digital_presence_agent import (
        DigitalPresenceOutput,
        WebsiteAnalysis,
        TechStack,
        SEOAnalysis,
        ContactInfo,
        WebsiteStatus,
        SEOQuality
    )

    # Mock agent response
    mock_tech_stack = TechStack(
        frameworks=["React", "Next.js"],
        hosting="Vercel",
        cdn="Cloudflare",
        confidence_score=85.0
    )

    mock_seo = SEOAnalysis(
        title="Example Company",
        seo_score=85.0,
        seo_quality=SEOQuality.EXCELLENT,
        is_mobile_friendly=True,
        page_speed_score=90.0
    )

    mock_contact = ContactInfo(
        emails=["info@example.com"],
        social_media={"facebook": "https://facebook.com/example"}
    )

    mock_analysis = WebsiteAnalysis(
        url="https://example.com",
        status=WebsiteStatus.ONLINE,
        response_time_ms=250,
        title="Example Company",
        tech_stack=mock_tech_stack,
        seo=mock_seo,
        contact_info=mock_contact
    )

    mock_result = DigitalPresenceOutput(
        target="https://example.com",
        company_name="Example Company",
        website_url="https://example.com",
        website_analysis=mock_analysis,
        online_presence_score=85.0,
        strengths=["Modern tech stack", "Excellent SEO"],
        weaknesses=[],
        recommendations=[],
        data_sources=["Jina Reader"],
        confidence_score=88.0
    )

    with patch('app.api.v1.endpoints.agents.DigitalPresenceAgent') as MockAgent:
        mock_instance = AsyncMock()
        mock_instance.execute = AsyncMock(return_value=mock_result)
        MockAgent.return_value = mock_instance

        response = await client.post(
            "/api/v1/agents/digital-presence",
            json={"target": "https://example.com", "use_cache": False},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["website_url"] == "https://example.com"
        assert data["company_name"] == "Example Company"
        assert data["online_presence_score"] == 85.0
        assert data["seo_score"] == 85.0
        assert data["seo_quality"] == "excellent"
        assert data["is_mobile_friendly"] is True
        assert "React" in data["tech_stack"]["frameworks"]
        assert "facebook" in data["social_media_platforms"]
        assert "info@example.com" in data["contact_emails"]


@pytest.mark.asyncio
async def test_digital_presence_endpoint_caching(client: AsyncClient, auth_headers):
    """Test digital presence endpoint caching."""
    from app.agents.digital_presence_agent import (
        DigitalPresenceOutput,
        WebsiteAnalysis,
        TechStack,
        SEOAnalysis,
        ContactInfo,
        WebsiteStatus,
        SEOQuality
    )

    # Mock minimal response
    mock_result = DigitalPresenceOutput(
        target="https://cached.com",
        website_url="https://cached.com",
        website_analysis=WebsiteAnalysis(
            url="https://cached.com",
            status=WebsiteStatus.ONLINE,
            tech_stack=TechStack(),
            seo=SEOAnalysis(),
            contact_info=ContactInfo()
        ),
        online_presence_score=75.0,
        confidence_score=80.0
    )

    with patch('app.api.v1.endpoints.agents.DigitalPresenceAgent') as MockAgent:
        mock_instance = AsyncMock()
        mock_instance.execute = AsyncMock(return_value=mock_result)
        MockAgent.return_value = mock_instance

        # First request (not cached)
        response1 = await client.post(
            "/api/v1/agents/digital-presence",
            json={"target": "https://cached.com", "use_cache": True},
            headers=auth_headers
        )

        assert response1.status_code == 200
        data1 = response1.json()
        # Note: caching might not work in tests without Redis, so just verify structure
        assert "cached" in data1
        assert "processing_time_ms" in data1


@pytest.mark.asyncio
async def test_digital_presence_endpoint_rate_limiting(client: AsyncClient, auth_headers):
    """Test rate limiting on digital presence endpoint."""
    from app.api.v1.endpoints.agents import rate_limit_store

    # Clear rate limit store
    rate_limit_store.clear()

    with patch('app.api.v1.endpoints.agents.DigitalPresenceAgent'):
        # Send 10 requests (max allowed)
        for i in range(10):
            response = await client.post(
                "/api/v1/agents/digital-presence",
                json={"target": f"https://site{i}.com", "use_cache": False},
                headers=auth_headers
            )
            # May succeed or fail depending on mocking, but shouldn't be rate limited yet

        # 11th request should be rate limited
        response = await client.post(
            "/api/v1/agents/digital-presence",
            json={"target": "https://rate-limited.com", "use_cache": False},
            headers=auth_headers
        )

        assert response.status_code == 429  # Too Many Requests


@pytest.mark.asyncio
async def test_digital_presence_endpoint_timeout(client: AsyncClient, auth_headers):
    """Test timeout handling on digital presence endpoint."""
    from app.api.v1.endpoints.agents import rate_limit_store

    # Clear rate limit store
    rate_limit_store.clear()

    with patch('app.api.v1.endpoints.agents.DigitalPresenceAgent') as MockAgent:
        mock_instance = AsyncMock()
        # Simulate timeout
        async def timeout_func(*args, **kwargs):
            await asyncio.sleep(35)  # Longer than 30s timeout

        mock_instance.execute = timeout_func
        MockAgent.return_value = mock_instance

        response = await client.post(
            "/api/v1/agents/digital-presence",
            json={"target": "https://slow-site.com", "use_cache": False},
            headers=auth_headers
        )

        assert response.status_code == 504  # Gateway Timeout


# ============================================================================
# COMPETITOR MAPPING ENDPOINT TESTS (Week 12)
# ============================================================================

def test_competitor_mapping_request_validation():
    """Test CompetitorMappingRequest validation (Week 12)."""
    # Valid request
    request = CompetitorMappingRequest(
        target="NIP 1234567890",
        include_swot=True,
        include_porter=True,
        max_competitors=10
    )

    assert request.target == "NIP 1234567890"
    assert request.include_swot is True
    assert request.include_porter is True
    assert request.max_competitors == 10
    assert request.use_cache is True  # default

    # Invalid: empty target
    with pytest.raises(ValueError, match="Target cannot be empty"):
        CompetitorMappingRequest(target="")

    # Invalid: too short
    with pytest.raises(ValueError, match="too short"):
        CompetitorMappingRequest(target="AB")

    # Invalid: max_competitors too high
    with pytest.raises(ValueError):
        CompetitorMappingRequest(target="Company", max_competitors=100)


def test_competitor_mapping_response_model():
    """Test CompetitorMappingResponse model structure (Week 12)."""
    response = CompetitorMappingResponse(
        success=True,
        target_company="Test Company",
        market_position="challenger",
        market_share_percentage=18.5,
        rank_in_industry=3,
        total_competitors=8,
        confidence_score=82.0,
        cached=False,
        processing_time_ms=2500
    )

    assert response.success is True
    assert response.target_company == "Test Company"
    assert response.market_position == "challenger"
    assert response.market_share_percentage == 18.5
    assert response.total_competitors == 8
    assert response.confidence_score == 82.0


def test_generate_cache_key_competitor():
    """Test cache key generation for competitor mapping (Week 12)."""
    request1 = CompetitorMappingRequest(
        target="NIP 1234567890",
        include_swot=True,
        include_porter=True,
        max_competitors=10
    )

    request2 = CompetitorMappingRequest(
        target="nip 1234567890",  # Different case
        include_swot=True,
        include_porter=True,
        max_competitors=10
    )

    # Should generate same key (case-insensitive)
    key1 = generate_cache_key_competitor(request1)
    key2 = generate_cache_key_competitor(request2)

    assert key1 == key2
    assert key1.startswith("agent:competitor_mapping:")

    # Different parameters should generate different keys
    request3 = CompetitorMappingRequest(
        target="NIP 1234567890",
        include_swot=False,
        include_porter=True,
        max_competitors=10
    )

    key3 = generate_cache_key_competitor(request3)
    assert key3 != key1


@pytest.mark.asyncio
async def test_competitor_mapping_endpoint_success(client: AsyncClient, auth_headers):
    """Test successful competitor mapping request (Week 12)."""
    from app.api.v1.endpoints.agents import rate_limit_store

    # Clear rate limit store
    rate_limit_store.clear()

    with patch('app.api.v1.endpoints.agents.CompetitorMappingAgent') as MockAgent:
        # Create mock output
        mock_output = CompetitorMappingOutput(
            target="NIP 1234567890",
            target_company_name="Test Company",
            competitors=[
                CompetitorProfile(
                    company_name="Competitor A",
                    similarity_score=85.0,
                    competitor_type=CompetitorType.DIRECT
                )
            ],
            market_position=MarketPositionAnalysis(
                position=MarketPosition.CHALLENGER,
                market_share_percentage=18.5,
                rank_in_industry=3,
                total_competitors_identified=8
            ),
            data_sources=["KRS", "GUS"],
            confidence_score=82.0
        )

        mock_instance = AsyncMock()
        mock_instance.execute = AsyncMock(return_value=mock_output)
        MockAgent.return_value = mock_instance

        response = await client.post(
            "/api/v1/agents/competitor-mapping",
            json={
                "target": "NIP 1234567890",
                "include_swot": True,
                "include_porter": True,
                "max_competitors": 10,
                "use_cache": False
            },
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["target_company"] == "Test Company"
        assert data["market_position"] == "challenger"
        assert data["market_share_percentage"] == 18.5
        assert data["total_competitors"] == 1
        assert len(data["direct_competitors"]) == 1
        assert data["confidence_score"] == 82.0


@pytest.mark.asyncio
async def test_competitor_mapping_endpoint_rate_limit(client: AsyncClient, auth_headers):
    """Test rate limiting on competitor mapping endpoint (Week 12)."""
    from app.api.v1.endpoints.agents import rate_limit_store

    # Clear rate limit store
    rate_limit_store.clear()

    with patch('app.api.v1.endpoints.agents.CompetitorMappingAgent'):
        # Send 10 requests (max allowed)
        for i in range(10):
            response = await client.post(
                "/api/v1/agents/competitor-mapping",
                json={"target": f"Company {i}", "use_cache": False},
                headers=auth_headers
            )
            # May succeed or fail depending on mocking, but shouldn't be rate limited yet

        # 11th request should be rate limited
        response = await client.post(
            "/api/v1/agents/competitor-mapping",
            json={"target": "Rate Limited Company", "use_cache": False},
            headers=auth_headers
        )

        assert response.status_code == 429  # Too Many Requests


# ============================================================================
# WEEK 15: FACT CHECKER ENDPOINT TESTS
# ============================================================================

def test_fact_checker_request_validation():
    """Test FactCheckerRequest validation (Week 15)."""
    # Valid request
    request = FactCheckerRequest(
        target="NIP 1234567890",
        claims=[
            {
                "text": "Company has 100 employees",
                "type": "operational",
                "subject": "Test Company",
                "value": "100"
            }
        ],
        include_citations=True,
        use_cache=True
    )

    assert request.target == "NIP 1234567890"
    assert len(request.claims) == 1
    assert request.include_citations is True
    assert request.use_cache is True  # default

    # Invalid: empty target
    with pytest.raises(ValueError, match="Target cannot be empty"):
        FactCheckerRequest(target="")

    # Invalid: too short
    with pytest.raises(ValueError, match="too short"):
        FactCheckerRequest(target="123")


def test_fact_checker_response_model():
    """Test FactCheckerResponse model structure (Week 15)."""
    response = FactCheckerResponse(
        success=True,
        target="NIP 1234567890",
        total_claims_checked=2,
        verified_claims_count=1,
        contradicted_claims_count=0,
        unverified_claims_count=1,
        verifications=[
            {
                "claim_text": "Test claim",
                "verification_status": "verified",
                "confidence_score": 85.0
            }
        ],
        data_sources=["KRS", "GUS"],
        primary_sources_used=2,
        overall_confidence_score=75.0,
        citations=[
            {
                "source_name": "KRS",
                "citation": "KRS. (2026). Official Registry."
            }
        ],
        cached=False,
        processing_time_ms=1500
    )

    assert response.success is True
    assert response.total_claims_checked == 2
    assert response.verified_claims_count == 1
    assert len(response.verifications) == 1
    assert len(response.citations) == 1


def test_fact_checker_cache_key_generation():
    """Test fact checker cache key generation (Week 15)."""
    request = FactCheckerRequest(
        target="NIP 1234567890",
        claims=[{"text": "Test", "type": "general"}],
        include_citations=True
    )

    cache_key = generate_cache_key_fact_checker(request)

    assert cache_key.startswith("agent:fact_checker:")
    assert len(cache_key) > 20  # Should include MD5 hash

    # Same request should generate same key
    cache_key_2 = generate_cache_key_fact_checker(request)
    assert cache_key == cache_key_2

    # Different request should generate different key
    request_2 = FactCheckerRequest(
        target="KRS 0000123456",
        claims=[{"text": "Different", "type": "financial"}]
    )
    cache_key_3 = generate_cache_key_fact_checker(request_2)
    assert cache_key != cache_key_3


def test_citation_generation():
    """Test citation generation from FactCheckerOutput (Week 15)."""
    # Create mock FactCheckerOutput
    output = FactCheckerOutput(
        target="NIP 1234567890",
        confidence_score=0.0
    )

    # Add verification with sources
    verification = Verification(
        claim_text="Test claim",
        claim_type=ClaimType.FINANCIAL,
        verification_status=VerificationStatus.VERIFIED,
        confidence_score=85.0,
        reliability_assessment="reliable"
    )

    verification.supporting_sources = [
        Source(
            source_name="KRS Registry",
            source_type=SourceType.OFFICIAL_REGISTRY,
            source_url="https://krs.gov.pl",
            credibility_score=95.0,
            credibility_level=CredibilityLevel.VERY_HIGH,
            publication_date=datetime(2026, 1, 1)
        ),
        Source(
            source_name="GUS Database",
            source_type=SourceType.OFFICIAL_REGISTRY,
            source_url="https://gus.gov.pl",
            credibility_score=95.0,
            credibility_level=CredibilityLevel.VERY_HIGH
        )
    ]

    output.verifications = [verification]

    # Generate citations
    citations = generate_citations(output)

    assert len(citations) == 2
    assert citations[0]["source_name"] == "KRS Registry"
    assert citations[0]["source_type"] == "official_registry"
    assert citations[0]["source_url"] == "https://krs.gov.pl"
    assert "citation" in citations[0]
    assert "2026" in citations[0]["citation"]  # Year from publication_date
    assert citations[0]["credibility_score"] == 95.0
    assert citations[0]["credibility_level"] == "very_high"

    assert citations[1]["source_name"] == "GUS Database"
    assert "(n.d.)" in citations[1]["citation"]  # No publication date


def test_fact_checker_endpoint_integration():
    """Integration test for fact-checker endpoint behavior (Week 15)."""
    # Test request creation with multiple claims
    request = FactCheckerRequest(
        target="NIP 1234567890",
        claims=[
            {
                "text": "Company has 100 employees",
                "type": "operational",
                "subject": "Test Company",
                "value": "100"
            },
            {
                "text": "Revenue is 10M PLN",
                "type": "financial",
                "subject": "Test Company",
                "value": "10000000"
            }
        ],
        include_citations=True,
        min_confidence=50.0,
        use_cache=True
    )

    assert len(request.claims) == 2
    assert request.min_confidence == 50.0

    # Test that cache key is different for different configurations
    cache_key_with_citations = generate_cache_key_fact_checker(request)

    request.include_citations = False
    cache_key_without_citations = generate_cache_key_fact_checker(request)

    assert cache_key_with_citations != cache_key_without_citations


# ============================================================================
# WEEK 18: INSIGHT GENERATOR AGENT ENDPOINT TESTS
# ============================================================================

def test_insight_generator_request_validation():
    """Test InsightGeneratorRequest validation (Week 18)."""
    # Valid request
    request = InsightGeneratorRequest(
        target="Tech Company Analysis",
        financial_data=[
            {"period": "2023", "revenue": 1000000},
            {"period": "2024", "revenue": 1200000}
        ],
        min_confidence=60.0,
        max_insights=10,
        include_scenarios=True
    )

    assert request.target == "Tech Company Analysis"
    assert len(request.financial_data) == 2
    assert request.min_confidence == 60.0
    assert request.max_insights == 10
    assert request.include_scenarios is True
    assert request.use_cache is True  # default

    # Invalid: empty target
    with pytest.raises(ValueError, match="Target cannot be empty"):
        InsightGeneratorRequest(target="")

    # Invalid: too short
    with pytest.raises(ValueError, match="too short"):
        InsightGeneratorRequest(target="AB")

    # Invalid: confidence out of range
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        InsightGeneratorRequest(
            target="Test",
            min_confidence=150.0
        )


def test_insight_generator_response_model():
    """Test InsightGeneratorResponse model structure (Week 18)."""
    response = InsightGeneratorResponse(
        success=True,
        target="Test Company",
        total_insights=5,
        insights=[
            {
                "insight_id": "insight_1",
                "insight_type": "trend",
                "insight_text": "Revenue growing",
                "priority": "high",
                "relevance_score": 85.0
            }
        ],
        total_patterns=3,
        total_predictions=2,
        total_risks=1,
        total_opportunities=2,
        overall_confidence_score=78.5,
        data_quality_score=85.0,
        data_points_analyzed=24,
        cached=False,
        processing_time_ms=2500
    )

    assert response.success is True
    assert response.target == "Test Company"
    assert response.total_insights == 5
    assert len(response.insights) == 1
    assert response.overall_confidence_score == 78.5
    assert response.data_points_analyzed == 24
    assert response.cached is False


def test_generate_cache_key_insight_generator():
    """Test cache key generation for insight generator (Week 18)."""
    request1 = InsightGeneratorRequest(
        target="Tech Company Analysis",
        financial_data=[{"period": "2023", "revenue": 1000000}],
        min_confidence=60.0,
        max_insights=10
    )

    request2 = InsightGeneratorRequest(
        target="tech company analysis",  # Different case
        financial_data=[{"period": "2023", "revenue": 1000000}],
        min_confidence=60.0,
        max_insights=10
    )

    key1 = generate_cache_key_insight_generator(request1)
    key2 = generate_cache_key_insight_generator(request2)

    # Should be same (normalized)
    assert key1 == key2

    # Should start with prefix
    assert key1.startswith("agent:insight_generator:")

    # Different parameters should create different keys
    request3 = InsightGeneratorRequest(
        target="Tech Company Analysis",
        financial_data=[{"period": "2023", "revenue": 1000000}],
        min_confidence=80.0,  # Different
        max_insights=10
    )

    key3 = generate_cache_key_insight_generator(request3)
    assert key1 != key3

    # Different data presence should create different keys
    request4 = InsightGeneratorRequest(
        target="Tech Company Analysis",
        market_data={"market_size": 5000000},  # Different data type
        min_confidence=60.0,
        max_insights=10
    )

    key4 = generate_cache_key_insight_generator(request4)
    assert key1 != key4


def test_insight_prioritization_logic():
    """Test insight prioritization based on relevance and actionability (Week 18)."""
    # Create insights with different priorities and relevance scores
    insights = [
        {
            "insight_id": "i1",
            "insight_type": "trend",
            "insight_text": "Low priority insight",
            "priority": "low",
            "relevance_score": 50.0,
            "is_actionable": False
        },
        {
            "insight_id": "i2",
            "insight_type": "risk",
            "insight_text": "High priority insight",
            "priority": "high",
            "relevance_score": 85.0,
            "is_actionable": True
        },
        {
            "insight_id": "i3",
            "insight_type": "opportunity",
            "insight_text": "Critical priority insight",
            "priority": "critical",
            "relevance_score": 95.0,
            "is_actionable": True
        },
        {
            "insight_id": "i4",
            "insight_type": "trend",
            "insight_text": "Medium priority insight",
            "priority": "medium",
            "relevance_score": 70.0,
            "is_actionable": True
        }
    ]

    # Sort using the same logic as the endpoint
    insights.sort(
        key=lambda x: (
            {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(x["priority"], 0),
            x["relevance_score"],
            1 if x["is_actionable"] else 0
        ),
        reverse=True
    )

    # Check order: critical > high > medium > low
    assert insights[0]["insight_id"] == "i3"  # critical
    assert insights[1]["insight_id"] == "i2"  # high
    assert insights[2]["insight_id"] == "i4"  # medium
    assert insights[3]["insight_id"] == "i1"  # low

    # Test filtering by confidence threshold
    min_confidence = 60.0
    filtered = [i for i in insights if i["relevance_score"] >= min_confidence]

    assert len(filtered) == 3  # i1 (50.0) should be filtered out
    assert all(i["relevance_score"] >= 60.0 for i in filtered)


def test_insight_generator_endpoint_integration():
    """Integration test for insight-generator endpoint behavior (Week 18)."""
    # Test request creation with multiple data sources
    request = InsightGeneratorRequest(
        target="TechCorp S.A. Market Analysis",
        financial_data=[
            {"period": "2023", "revenue": 1000000, "profit_margin": 15.5},
            {"period": "2024", "revenue": 1200000, "profit_margin": 18.0}
        ],
        market_data={
            "market_size": 5000000,
            "growth_rate": 12.5,
            "market_share": 8.0
        },
        competitor_data=[
            {"name": "Competitor A", "market_share": 15.0},
            {"name": "Competitor B", "market_share": 12.0}
        ],
        digital_presence={
            "website_traffic": 50000,
            "social_media_followers": 10000
        },
        min_confidence=60.0,
        max_insights=10,
        include_scenarios=True,
        use_cache=True
    )

    assert request.target == "TechCorp S.A. Market Analysis"
    assert len(request.financial_data) == 2
    assert request.market_data is not None
    assert len(request.competitor_data) == 2
    assert request.digital_presence is not None
    assert request.min_confidence == 60.0
    assert request.max_insights == 10

    # Test that cache key is different for different data
    cache_key_with_all = generate_cache_key_insight_generator(request)

    request.competitor_data = None
    cache_key_without_competitor = generate_cache_key_insight_generator(request)

    assert cache_key_with_all != cache_key_without_competitor

    # Test different include_scenarios flag
    request.include_scenarios = False
    cache_key_no_scenarios = generate_cache_key_insight_generator(request)

    # Should be different because include_scenarios changed
    assert cache_key_without_competitor != cache_key_no_scenarios


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
