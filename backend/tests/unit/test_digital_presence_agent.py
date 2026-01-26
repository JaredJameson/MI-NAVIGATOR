"""
Unit Tests for DigitalPresenceAgent - Week 7 Implementation

Tests for:
- Pydantic models validation
- Tech stack detection
- SEO analysis
- Contact information extraction
- Overall digital presence scoring
- Agent execution flow

Author: MI-Navigator Development Team
Created: 2026-01-25 (Week 7)
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from app.agents.digital_presence_agent import (
    DigitalPresenceAgent,
    DigitalPresenceOutput,
    WebsiteAnalysis,
    TechStack,
    SEOAnalysis,
    ContactInfo,
    WebsiteStatus,
    SEOQuality,
    CrawlerSource
)


# ============================================================================
# PYDANTIC MODEL TESTS
# ============================================================================

def test_tech_stack_model_valid():
    """Test TechStack model with valid data."""
    tech_stack = TechStack(
        frameworks=["React", "Next.js"],
        cms=None,
        hosting="Vercel",
        analytics=["Google Analytics"],
        cdn="Cloudflare",
        languages=["JavaScript", "TypeScript"],
        libraries=["axios"],
        confidence_score=85.0
    )

    assert len(tech_stack.frameworks) == 2
    assert "React" in tech_stack.frameworks
    assert tech_stack.hosting == "Vercel"
    assert tech_stack.confidence_score == 85.0


def test_tech_stack_model_empty():
    """Test TechStack model with no data."""
    tech_stack = TechStack()

    assert tech_stack.frameworks == []
    assert tech_stack.cms is None
    assert tech_stack.confidence_score == 0.0


def test_seo_analysis_model_valid():
    """Test SEOAnalysis model with valid data."""
    seo = SEOAnalysis(
        title="Company Name - Solutions",
        meta_description="We provide innovative solutions",
        meta_keywords=["solutions", "technology"],
        headings_count={"h1": 1, "h2": 5},
        images_without_alt=3,
        has_sitemap=True,
        has_robots_txt=True,
        is_mobile_friendly=True,
        page_speed_score=75.0,
        seo_score=72.0,
        seo_quality=SEOQuality.GOOD,
        issues=["3 images without alt text"],
        recommendations=["Add alt text"]
    )

    assert seo.title == "Company Name - Solutions"
    assert seo.seo_score == 72.0
    assert seo.seo_quality == SEOQuality.GOOD
    assert seo.has_sitemap is True


def test_seo_quality_enum_values():
    """Test SEO quality enum values."""
    assert SEOQuality.EXCELLENT == "excellent"
    assert SEOQuality.GOOD == "good"
    assert SEOQuality.FAIR == "fair"
    assert SEOQuality.POOR == "poor"


def test_contact_info_model_valid():
    """Test ContactInfo model with valid data."""
    contact = ContactInfo(
        emails=["info@company.com", "contact@company.com"],
        phones=["+48 123 456 789"],
        addresses=["ul. Testowa 123, Warszawa"],
        social_media={
            "facebook": "https://facebook.com/company",
            "linkedin": "https://linkedin.com/company/company"
        },
        contact_page_url="https://company.com/contact",
        has_contact_form=True
    )

    assert len(contact.emails) == 2
    assert "+48 123 456 789" in contact.phones
    assert "facebook" in contact.social_media
    assert contact.has_contact_form is True


def test_website_analysis_model_valid():
    """Test WebsiteAnalysis model with complete data."""
    tech_stack = TechStack(
        frameworks=["React"],
        confidence_score=80.0
    )

    seo = SEOAnalysis(
        title="Test Site",
        seo_score=70.0,
        seo_quality=SEOQuality.GOOD
    )

    contact = ContactInfo(
        emails=["info@test.com"]
    )

    analysis = WebsiteAnalysis(
        url="https://test.com",
        status=WebsiteStatus.ONLINE,
        response_time_ms=350,
        title="Test Company",
        description="Test description",
        content_length=15000,
        language="pl",
        tech_stack=tech_stack,
        seo=seo,
        contact_info=contact,
        screenshot_url=None
    )

    assert analysis.url == "https://test.com"
    assert analysis.status == WebsiteStatus.ONLINE
    assert analysis.response_time_ms == 350
    assert analysis.tech_stack.frameworks == ["React"]
    assert analysis.seo.seo_score == 70.0


def test_digital_presence_output_model_valid():
    """Test DigitalPresenceOutput model validation."""
    tech_stack = TechStack()
    seo = SEOAnalysis()
    contact = ContactInfo()

    website_analysis = WebsiteAnalysis(
        url="https://test.com",
        status=WebsiteStatus.ONLINE,
        tech_stack=tech_stack,
        seo=seo,
        contact_info=contact
    )

    output = DigitalPresenceOutput(
        target="https://test.com",
        company_name="Test Company",
        website_url="https://test.com",
        website_analysis=website_analysis,
        online_presence_score=75.0,
        strengths=["Modern tech stack"],
        weaknesses=["Poor SEO"],
        recommendations=["Improve meta tags"],
        data_sources=["Jina Reader"],
        confidence_score=85.0
    )

    assert output.target == "https://test.com"
    assert output.online_presence_score == 75.0
    assert output.confidence_score == 85.0
    assert len(output.strengths) == 1


def test_digital_presence_output_confidence_validation():
    """Test confidence score validation in DigitalPresenceOutput."""
    from pydantic import ValidationError

    tech_stack = TechStack()
    seo = SEOAnalysis()
    contact = ContactInfo()

    website_analysis = WebsiteAnalysis(
        url="https://test.com",
        status=WebsiteStatus.ONLINE,
        tech_stack=tech_stack,
        seo=seo,
        contact_info=contact
    )

    # Valid confidence scores
    output1 = DigitalPresenceOutput(
        target="test.com",
        website_url="https://test.com",
        website_analysis=website_analysis,
        confidence_score=0.0
    )
    assert output1.confidence_score == 0.0

    output2 = DigitalPresenceOutput(
        target="test.com",
        website_url="https://test.com",
        website_analysis=website_analysis,
        confidence_score=100.0
    )
    assert output2.confidence_score == 100.0

    # Invalid confidence score - Pydantic raises ValidationError
    with pytest.raises(ValidationError):
        DigitalPresenceOutput(
            target="test.com",
            website_url="https://test.com",
            website_analysis=website_analysis,
            confidence_score=150.0
        )


# ============================================================================
# AGENT LOGIC TESTS
# ============================================================================

def test_normalize_url():
    """Test URL normalization."""
    agent = DigitalPresenceAgent()

    # Already a URL
    assert agent._normalize_url("https://example.com") == "https://example.com"
    assert agent._normalize_url("http://example.com") == "http://example.com"

    # Domain only
    assert agent._normalize_url("example.com") == "https://example.com"
    assert agent._normalize_url("  example.com  ") == "https://example.com"


def test_analyze_tech_stack_categorization():
    """Test tech stack categorization logic."""
    agent = DigitalPresenceAgent()

    # Test framework detection
    detected_stack = ["React", "Next.js", "WordPress", "AWS", "Google Analytics", "Cloudflare", "JavaScript"]

    # Mock crawler
    agent.crawler = AsyncMock()
    agent.crawler.detect_tech_stack = AsyncMock(return_value=detected_stack)

    # Run analysis (need to use asyncio for async method)
    import asyncio
    tech_stack = asyncio.run(agent._analyze_tech_stack("https://test.com", "<html></html>"))

    assert "React" in tech_stack.frameworks
    assert "Next.js" in tech_stack.frameworks
    assert tech_stack.cms == "WordPress"
    assert tech_stack.hosting == "AWS"
    assert "Google Analytics" in tech_stack.analytics
    assert tech_stack.cdn == "Cloudflare"
    assert "JavaScript" in tech_stack.languages
    assert tech_stack.confidence_score == 85.0


def test_analyze_seo_scoring():
    """Test SEO scoring algorithm."""
    agent = DigitalPresenceAgent()

    # Good SEO
    page_data = {
        "title": "Company Name - Leading Solutions Provider",
        "description": "We provide innovative solutions for businesses",
        "html": "<html><body>" + "x" * 2000 + "</body></html>"
    }

    seo = agent._analyze_seo(page_data)

    assert seo.title == "Company Name - Leading Solutions Provider"
    assert seo.meta_description == "We provide innovative solutions for businesses"
    assert seo.seo_score >= 80.0  # Should be excellent
    assert seo.seo_quality in [SEOQuality.EXCELLENT, SEOQuality.GOOD]


def test_analyze_seo_missing_elements():
    """Test SEO analysis with missing elements."""
    agent = DigitalPresenceAgent()

    # Poor SEO - missing title and description
    page_data = {
        "title": None,
        "description": None,
        "html": "<html><body>Short content</body></html>"
    }

    seo = agent._analyze_seo(page_data)

    assert seo.title is None
    assert seo.meta_description is None
    assert "Missing title tag" in seo.issues
    assert "Missing meta description" in seo.issues
    # Base score is 50, so quality is FAIR
    assert seo.seo_quality == SEOQuality.FAIR
    assert seo.seo_score == 50.0


def test_calculate_online_presence_score():
    """Test online presence score calculation."""
    agent = DigitalPresenceAgent()

    # Excellent presence
    tech_stack = TechStack(
        frameworks=["React", "Next.js"],
        hosting="AWS",
        cdn="Cloudflare",
        analytics=["Google Analytics"],
        confidence_score=85.0
    )

    seo = SEOAnalysis(
        seo_score=85.0,
        seo_quality=SEOQuality.EXCELLENT
    )

    contact = ContactInfo(
        emails=["info@company.com"],
        phones=["+48 123 456 789"],
        social_media={"linkedin": "https://linkedin.com/company"},
        has_contact_form=True
    )

    score = agent._calculate_online_presence_score(tech_stack, seo, contact)

    # Score should be high with all components present
    assert score >= 75.0
    assert score <= 100.0


def test_identify_strengths_weaknesses():
    """Test strengths and weaknesses identification."""
    agent = DigitalPresenceAgent()

    # Strong presence
    tech_stack = TechStack(
        frameworks=["React", "Vue"],
        cdn="Cloudflare",
        confidence_score=85.0
    )

    seo = SEOAnalysis(
        seo_score=85.0,
        seo_quality=SEOQuality.EXCELLENT
    )

    contact = ContactInfo(
        emails=["info@company.com", "sales@company.com"],
        social_media={"linkedin": "url", "facebook": "url"}
    )

    strengths, weaknesses = agent._identify_strengths_weaknesses(tech_stack, seo, contact)

    assert len(strengths) > 0
    assert any("tech stack" in s.lower() for s in strengths)
    assert any("seo" in s.lower() for s in strengths)
    assert any("email" in s.lower() for s in strengths)
    assert any("social media" in s.lower() for s in strengths)


@pytest.mark.asyncio
async def test_agent_execute_success():
    """Test successful agent execution."""
    agent = DigitalPresenceAgent()

    # Mock all external dependencies
    mock_page_data = {
        "success": True,
        "url": "https://test.com",
        "title": "Test Company",
        "description": "Test description",
        "content": "Website content here",
        "html": "<html><body>Content</body></html>",
        "response_time_ms": 350
    }

    mock_tech_stack = ["React", "Next.js", "Cloudflare"]
    mock_contact_data = {
        "emails": ["info@test.com"],
        "phones": ["+48 123 456 789"],
        "addresses": [],
        "social_media": {"linkedin": "https://linkedin.com/company/test"},
        "has_contact_form": True
    }

    with patch('app.agents.digital_presence_agent.WebsiteAnalysisClient') as MockClient:
        mock_instance = AsyncMock()
        mock_instance.scrape_page = AsyncMock(return_value=mock_page_data)
        mock_instance.detect_tech_stack = AsyncMock(return_value=mock_tech_stack)
        mock_instance.extract_contact_info = AsyncMock(return_value=mock_contact_data)
        mock_instance.close = AsyncMock()
        MockClient.return_value = mock_instance

        result = await agent.execute("https://test.com")

    assert isinstance(result, DigitalPresenceOutput)
    assert result.website_url == "https://test.com"
    assert result.company_name == "Test Company"
    assert result.online_presence_score > 0
    assert result.confidence_score > 0
    assert len(result.data_sources) > 0


@pytest.mark.asyncio
async def test_agent_execute_error_handling():
    """Test agent error handling when website is unavailable."""
    agent = DigitalPresenceAgent()

    with patch('app.agents.digital_presence_agent.WebsiteAnalysisClient') as MockClient:
        mock_instance = AsyncMock()
        # scrape_page exception is caught by _scrape_website, so it returns success=False
        mock_instance.scrape_page = AsyncMock(side_effect=Exception("Network error"))
        # detect_tech_stack also needs to be mocked to avoid further errors
        mock_instance.detect_tech_stack = AsyncMock(return_value=[])
        mock_instance.extract_contact_info = AsyncMock(return_value={
            "emails": [], "phones": [], "addresses": [],
            "social_media": {}, "has_contact_form": False
        })
        mock_instance.close = AsyncMock()
        MockClient.return_value = mock_instance

        result = await agent.execute("https://invalid-site.com")

    # Exception is caught by _scrape_website, so execute() continues normally
    assert isinstance(result, DigitalPresenceOutput)
    assert result.website_analysis.status == WebsiteStatus.ERROR  # success=False from _scrape_website
    assert result.online_presence_score == 0.0
    # Confidence is calculated normally: base(50) + tech_stack.confidence(30)*0.2 = 56
    assert 50 <= result.confidence_score <= 60
    assert len(result.weaknesses) > 0  # Will have weaknesses from analysis
    assert len(result.data_sources) > 0  # Normal data sources


# ============================================================================
# WEEK 8 ADVANCED FEATURES TESTS
# ============================================================================

def test_enhanced_seo_with_html_parsing():
    """Test enhanced SEO analysis with real HTML parsing."""
    agent = DigitalPresenceAgent()

    # HTML with complete SEO elements
    html = """
    <html>
    <head>
        <title>Company Name - Perfect SEO Title Here</title>
        <meta name="description" content="This is a perfectly optimized meta description with exactly the right length for search engines to display properly and attract clicks.">
        <meta name="keywords" content="seo, optimization, marketing, digital">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
        <h1>Main Heading</h1>
        <h2>Section 1</h2>
        <h2>Section 2</h2>
        <p>Content here...</p>
        <img src="logo.png" alt="Company Logo">
        <img src="banner.png" alt="Banner">
        <img src="icon.png">  <!-- Missing alt -->
    </body>
    </html>
    """

    page_data = {
        "html": html,
        "title": "Company Name - Perfect SEO Title Here",
        "description": "This is a perfectly optimized meta description",
        "response_time_ms": 250
    }

    seo = agent._analyze_seo(page_data)

    # Verify enhanced SEO parsing
    assert seo.title == "Company Name - Perfect SEO Title Here"
    assert len(seo.meta_keywords) == 4
    assert "seo" in seo.meta_keywords
    assert "optimization" in seo.meta_keywords

    # Verify headings count
    assert seo.headings_count.get('h1') == 1
    assert seo.headings_count.get('h2') == 2

    # Verify images without alt
    assert seo.images_without_alt == 1

    # Verify mobile-friendly detection
    assert seo.is_mobile_friendly is True

    # Should have high SEO score
    assert seo.seo_score >= 85.0
    assert seo.seo_quality in [SEOQuality.EXCELLENT, SEOQuality.GOOD]


def test_social_media_detection():
    """Test social media presence detection from HTML."""
    agent = DigitalPresenceAgent()

    html = """
    <html>
    <body>
        <footer>
            <a href="https://facebook.com/mycompany">Facebook</a>
            <a href="https://twitter.com/mycompany">Twitter</a>
            <a href="https://www.linkedin.com/company/mycompany">LinkedIn</a>
            <a href="https://instagram.com/mycompany">Instagram</a>
            <a href="https://youtube.com/@mycompany">YouTube</a>
        </footer>
    </body>
    </html>
    """

    social_media = agent._detect_social_media(html, "https://test.com")

    # Verify detection
    assert len(social_media) == 5
    assert 'facebook' in social_media
    assert 'twitter' in social_media
    assert 'linkedin' in social_media
    assert 'instagram' in social_media
    assert 'youtube' in social_media

    # Verify URLs
    assert 'facebook.com/mycompany' in social_media['facebook']
    assert 'linkedin.com/company/mycompany' in social_media['linkedin']


def test_email_validation():
    """Test email validation with pattern matching."""
    agent = DigitalPresenceAgent()

    # Test valid emails
    valid_emails = [
        "info@company.com",
        "contact@company.pl",
        "support@my-company.co.uk",
    ]

    validated = agent._validate_emails(valid_emails)
    assert len(validated) == 3
    assert "info@company.com" in validated

    # Test with invalid/placeholder emails
    mixed_emails = [
        "info@company.com",
        "invalid-email",
        "info@example.com",  # Placeholder, should be filtered
        "test@test.com",  # Placeholder, should be filtered
        "contact@company.com",
    ]

    validated = agent._validate_emails(mixed_emails)
    assert len(validated) == 2  # Only info@company.com and contact@company.com
    assert "info@example.com" not in validated
    assert "test@test.com" not in validated

    # Test duplicate removal
    duplicates = ["info@company.com", "info@company.com", "INFO@COMPANY.COM"]
    validated = agent._validate_emails(duplicates)
    assert len(validated) == 1  # Duplicates removed, case-insensitive


def test_phone_validation():
    """Test phone number validation."""
    agent = DigitalPresenceAgent()

    # Test valid phones
    valid_phones = [
        "+48 123 456 789",
        "(555) 123-4567",
        "1234567",  # Minimum 7 digits
    ]

    validated = agent._validate_phones(valid_phones)
    assert len(validated) == 3

    # Test with invalid/placeholder phones
    mixed_phones = [
        "+48 123 456 789",
        "123",  # Too short
        "123-456-7890",  # Placeholder, should be filtered
        "000-000-0000",  # Placeholder, should be filtered
        "(555) 987-6543",
    ]

    validated = agent._validate_phones(mixed_phones)
    assert len(validated) == 2  # Only +48... and (555) 987-6543
    assert "123-456-7890" not in validated
    assert "000-000-0000" not in validated

    # Test duplicate removal
    duplicates = ["+48 123 456 789", "+48 123 456 789"]
    validated = agent._validate_phones(duplicates)
    assert len(validated) == 1


def test_performance_analysis():
    """Test performance metrics analysis."""
    agent = DigitalPresenceAgent()

    # Test excellent performance
    perf = agent._analyze_performance(
        response_time_ms=150,
        is_mobile_friendly=True,
        content_length=50000  # 50KB
    )

    assert perf['response_time_ms'] == 150
    assert perf['is_mobile_friendly'] is True
    assert perf['performance_score'] >= 90.0
    assert perf['performance_level'] == 'excellent'
    assert len(perf['issues']) == 0

    # Test poor performance
    perf_poor = agent._analyze_performance(
        response_time_ms=3500,
        is_mobile_friendly=False,
        content_length=2000000  # 2MB
    )

    assert perf_poor['performance_score'] < 60.0  # Base 50 + content 5 = 55
    assert perf_poor['performance_score'] > 40.0  # Should still be above 40
    assert perf_poor['performance_level'] in ['poor', 'fair', 'very poor']
    assert len(perf_poor['issues']) > 0
    assert len(perf_poor['recommendations']) > 0

    # Test good performance
    perf_good = agent._analyze_performance(
        response_time_ms=400,
        is_mobile_friendly=True,
        content_length=200000  # 200KB
    )

    # Response 400ms (30) + mobile (30) + content 200KB (15) + base (50) = 125 → capped at 100
    assert perf_good['performance_score'] >= 90.0
    assert perf_good['performance_level'] in ['excellent', 'good']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
