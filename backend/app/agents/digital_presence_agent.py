"""
DigitalPresenceAgent - Website Analysis and Online Presence Assessment

Week 7 Implementation: Foundation
- Pydantic models for website analysis
- Website crawler integration (Firecrawl/Jina)
- Tech stack detection
- SEO basics
- Contact information extraction

Author: MI-Navigator Development Team
Created: 2026-01-25 (Week 7)
"""

import logging
import re
from typing import Optional, Dict, Any, List, Set
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

from app.integrations.website_crawler import WebsiteAnalysisClient, CrawlerSource

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================

class WebsiteStatus(str, Enum):
    """Website availability status"""
    ONLINE = "online"
    OFFLINE = "offline"
    SLOW = "slow"
    ERROR = "error"


class SEOQuality(str, Enum):
    """SEO quality rating"""
    EXCELLENT = "excellent"  # 80-100
    GOOD = "good"  # 60-79
    FAIR = "fair"  # 40-59
    POOR = "poor"  # 0-39


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class TechStack(BaseModel):
    """Technology stack detected on website"""

    frameworks: List[str] = Field(
        default_factory=list,
        description="Frontend/backend frameworks (React, Vue, Django, etc.)"
    )

    cms: Optional[str] = Field(
        None,
        description="Content Management System (WordPress, Drupal, etc.)"
    )

    hosting: Optional[str] = Field(
        None,
        description="Hosting provider (AWS, Azure, Cloudflare, etc.)"
    )

    analytics: List[str] = Field(
        default_factory=list,
        description="Analytics tools (Google Analytics, Matomo, etc.)"
    )

    cdn: Optional[str] = Field(
        None,
        description="CDN provider (Cloudflare, Akamai, etc.)"
    )

    languages: List[str] = Field(
        default_factory=list,
        description="Programming languages detected"
    )

    libraries: List[str] = Field(
        default_factory=list,
        description="JavaScript libraries and other dependencies"
    )

    confidence_score: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Confidence in tech stack detection (0-100)"
    )

    class Config:
        schema_extra = {
            "example": {
                "frameworks": ["React", "Next.js"],
                "cms": None,
                "hosting": "Vercel",
                "analytics": ["Google Analytics"],
                "cdn": "Cloudflare",
                "languages": ["JavaScript", "TypeScript"],
                "libraries": ["axios", "react-query"],
                "confidence_score": 85.0
            }
        }


class SEOAnalysis(BaseModel):
    """SEO analysis results"""

    title: Optional[str] = Field(
        None,
        description="Page title tag"
    )

    meta_description: Optional[str] = Field(
        None,
        description="Meta description tag"
    )

    meta_keywords: List[str] = Field(
        default_factory=list,
        description="Meta keywords (if present)"
    )

    headings_count: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of H1, H2, H3, etc. headings"
    )

    images_without_alt: int = Field(
        0,
        ge=0,
        description="Number of images without alt text"
    )

    has_sitemap: bool = Field(
        False,
        description="Whether sitemap.xml exists"
    )

    has_robots_txt: bool = Field(
        False,
        description="Whether robots.txt exists"
    )

    is_mobile_friendly: Optional[bool] = Field(
        None,
        description="Mobile-friendliness indicator"
    )

    page_speed_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Page speed score (0-100)"
    )

    seo_score: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Overall SEO quality score (0-100)"
    )

    seo_quality: SEOQuality = Field(
        SEOQuality.POOR,
        description="SEO quality rating"
    )

    issues: List[str] = Field(
        default_factory=list,
        description="SEO issues detected"
    )

    recommendations: List[str] = Field(
        default_factory=list,
        description="SEO improvement recommendations"
    )

    class Config:
        schema_extra = {
            "example": {
                "title": "Company Name - Leading Solutions Provider",
                "meta_description": "We provide innovative solutions...",
                "meta_keywords": ["solutions", "technology"],
                "headings_count": {"h1": 1, "h2": 5, "h3": 10},
                "images_without_alt": 3,
                "has_sitemap": True,
                "has_robots_txt": True,
                "is_mobile_friendly": True,
                "page_speed_score": 75.0,
                "seo_score": 72.0,
                "seo_quality": "good",
                "issues": ["3 images without alt text"],
                "recommendations": ["Add alt text to all images"]
            }
        }


class ContactInfo(BaseModel):
    """Contact information extracted from website"""

    emails: List[str] = Field(
        default_factory=list,
        description="Email addresses found"
    )

    phones: List[str] = Field(
        default_factory=list,
        description="Phone numbers found"
    )

    addresses: List[str] = Field(
        default_factory=list,
        description="Physical addresses found"
    )

    social_media: Dict[str, str] = Field(
        default_factory=dict,
        description="Social media profiles (platform -> URL)"
    )

    contact_page_url: Optional[str] = Field(
        None,
        description="URL of contact page if found"
    )

    has_contact_form: bool = Field(
        False,
        description="Whether a contact form is present"
    )

    class Config:
        schema_extra = {
            "example": {
                "emails": ["info@company.com", "contact@company.com"],
                "phones": ["+48 123 456 789"],
                "addresses": ["ul. Testowa 123, 00-001 Warszawa"],
                "social_media": {
                    "facebook": "https://facebook.com/company",
                    "linkedin": "https://linkedin.com/company/company"
                },
                "contact_page_url": "https://company.com/contact",
                "has_contact_form": True
            }
        }


class WebsiteAnalysis(BaseModel):
    """Complete website analysis results"""

    url: str = Field(
        ...,
        description="Website URL analyzed"
    )

    status: WebsiteStatus = Field(
        WebsiteStatus.ONLINE,
        description="Website availability status"
    )

    response_time_ms: Optional[int] = Field(
        None,
        ge=0,
        description="Response time in milliseconds"
    )

    title: Optional[str] = Field(
        None,
        description="Website title"
    )

    description: Optional[str] = Field(
        None,
        description="Website description"
    )

    content_length: int = Field(
        0,
        ge=0,
        description="Content length in characters"
    )

    language: Optional[str] = Field(
        None,
        description="Primary language detected"
    )

    tech_stack: TechStack = Field(
        ...,
        description="Technology stack analysis"
    )

    seo: SEOAnalysis = Field(
        ...,
        description="SEO analysis results"
    )

    contact_info: ContactInfo = Field(
        ...,
        description="Contact information extracted"
    )

    screenshot_url: Optional[str] = Field(
        None,
        description="URL to website screenshot (if captured)"
    )

    analyzed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of analysis"
    )

    class Config:
        schema_extra = {
            "example": {
                "url": "https://example.com",
                "status": "online",
                "response_time_ms": 350,
                "title": "Example Company",
                "description": "Leading solutions provider",
                "content_length": 15000,
                "language": "pl",
                "tech_stack": {},
                "seo": {},
                "contact_info": {},
                "screenshot_url": None,
                "analyzed_at": "2026-01-25T10:00:00Z"
            }
        }


class DigitalPresenceOutput(BaseModel):
    """Output from DigitalPresenceAgent"""

    target: str = Field(
        ...,
        description="Company identifier or website URL"
    )

    company_name: Optional[str] = Field(
        None,
        description="Company name"
    )

    website_url: str = Field(
        ...,
        description="Primary website URL analyzed"
    )

    website_analysis: WebsiteAnalysis = Field(
        ...,
        description="Complete website analysis"
    )

    online_presence_score: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Overall online presence quality score (0-100)"
    )

    strengths: List[str] = Field(
        default_factory=list,
        description="Digital presence strengths"
    )

    weaknesses: List[str] = Field(
        default_factory=list,
        description="Digital presence weaknesses"
    )

    recommendations: List[str] = Field(
        default_factory=list,
        description="Improvement recommendations"
    )

    data_sources: List[str] = Field(
        default_factory=list,
        description="Data sources used"
    )

    confidence_score: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Confidence in analysis results (0-100)"
    )

    @validator('confidence_score')
    def validate_confidence_score(cls, v):
        """Validate confidence score is within range."""
        if not 0 <= v <= 100:
            raise ValueError("Confidence score must be between 0 and 100")
        return v

    class Config:
        schema_extra = {
            "example": {
                "target": "https://example.com",
                "company_name": "Example Company",
                "website_url": "https://example.com",
                "website_analysis": {},
                "online_presence_score": 75.0,
                "strengths": ["Modern tech stack", "Good SEO"],
                "weaknesses": ["Missing social media links"],
                "recommendations": ["Add LinkedIn profile"],
                "data_sources": ["Jina Reader", "Tech Stack Detection"],
                "confidence_score": 85.0
            }
        }


# ============================================================================
# AGENT CLASS
# ============================================================================

class DigitalPresenceAgent:
    """
    Autonomous agent for website analysis and online presence assessment.

    Week 7 Capabilities:
    - Website crawling and parsing
    - Tech stack detection
    - Basic SEO analysis
    - Contact information extraction

    Week 8 Enhancements (COMPLETE):
    - Advanced SEO metrics (meta tags, keywords, heading structure)
    - Social media presence mapping (8 platforms)
    - Enhanced contact validation (email/phone patterns)
    - Performance metrics analysis
    - Mobile-friendliness testing
    """

    def __init__(
        self,
        crawler_source: CrawlerSource = CrawlerSource.JINA,
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize Digital Presence Agent.

        Args:
            crawler_source: Which crawler service to use
            api_key: API key for the crawler service
            timeout: Request timeout in seconds
        """
        self.crawler_source = crawler_source
        self.api_key = api_key
        self.timeout = timeout
        self.crawler: Optional[WebsiteAnalysisClient] = None

    async def execute(self, target: str) -> DigitalPresenceOutput:
        """
        Execute digital presence analysis.

        Args:
            target: Website URL or company identifier

        Returns:
            DigitalPresenceOutput with complete analysis
        """
        logger.info(f"DigitalPresenceAgent starting analysis for: {target}")

        try:
            # Initialize crawler
            self.crawler = WebsiteAnalysisClient(
                source=self.crawler_source,
                api_key=self.api_key,
                timeout=self.timeout
            )

            # Normalize URL
            website_url = self._normalize_url(target)

            # Scrape website
            page_data = await self._scrape_website(website_url)

            # Detect tech stack
            tech_stack = await self._analyze_tech_stack(website_url, page_data.get("html"))

            # Analyze SEO
            seo_analysis = self._analyze_seo(page_data)

            # Extract contact info
            contact_info = await self._extract_contact_info(website_url, page_data.get("html"))

            # Build website analysis
            website_analysis = WebsiteAnalysis(
                url=website_url,
                status=WebsiteStatus.ONLINE if page_data.get("success") else WebsiteStatus.ERROR,
                response_time_ms=page_data.get("response_time_ms"),
                title=page_data.get("title"),
                description=seo_analysis.meta_description,
                content_length=len(page_data.get("content", "")),
                language=page_data.get("language", "en"),
                tech_stack=tech_stack,
                seo=seo_analysis,
                contact_info=contact_info,
                screenshot_url=page_data.get("screenshot_url")
            )

            # Calculate overall online presence score
            online_presence_score = self._calculate_online_presence_score(
                tech_stack, seo_analysis, contact_info
            )

            # Identify strengths and weaknesses
            strengths, weaknesses = self._identify_strengths_weaknesses(
                tech_stack, seo_analysis, contact_info
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(weaknesses, seo_analysis)

            # Calculate confidence
            confidence_score = self._calculate_confidence(page_data, tech_stack, seo_analysis)

            return DigitalPresenceOutput(
                target=target,
                company_name=page_data.get("title"),
                website_url=website_url,
                website_analysis=website_analysis,
                online_presence_score=online_presence_score,
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=recommendations,
                data_sources=[self.crawler_source.value, "Tech Stack Detection", "SEO Analysis"],
                confidence_score=confidence_score
            )

        except Exception as e:
            logger.error(f"Error in DigitalPresenceAgent: {str(e)}", exc_info=True)

            # Return minimal output on error
            return DigitalPresenceOutput(
                target=target,
                company_name=None,
                website_url=self._normalize_url(target),
                website_analysis=WebsiteAnalysis(
                    url=self._normalize_url(target),
                    status=WebsiteStatus.ERROR,
                    tech_stack=TechStack(),
                    seo=SEOAnalysis(),
                    contact_info=ContactInfo()
                ),
                online_presence_score=0.0,
                strengths=[],
                weaknesses=["Website analysis failed"],
                recommendations=["Verify website URL and accessibility"],
                data_sources=[],
                confidence_score=0.0
            )

        finally:
            if self.crawler:
                await self.crawler.close()

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    def _normalize_url(self, target: str) -> str:
        """Normalize target to full URL."""
        target = target.strip()

        # If already a URL, return as-is
        if target.startswith("http://") or target.startswith("https://"):
            return target

        # Otherwise assume it's a domain
        return f"https://{target}"

    async def _scrape_website(self, url: str) -> Dict[str, Any]:
        """Scrape website and return page data."""
        try:
            result = await self.crawler.scrape_page(url)
            return result
        except Exception as e:
            logger.error(f"Website scraping failed for {url}: {str(e)}")
            return {
                "success": False,
                "url": url,
                "title": None,
                "content": "",
                "html": None
            }

    async def _analyze_tech_stack(self, url: str, html: Optional[str]) -> TechStack:
        """Analyze technology stack."""
        try:
            detected_stack = await self.crawler.detect_tech_stack(url, html)

            # Parse detected stack into categories
            frameworks = []
            cms = None
            hosting = None
            analytics = []
            cdn = None
            languages = []
            libraries = []

            for tech in detected_stack:
                tech_lower = tech.lower()

                # Frameworks
                if any(fw in tech_lower for fw in ["react", "vue", "angular", "next", "nuxt", "django", "flask", "laravel"]):
                    frameworks.append(tech)

                # CMS
                elif any(c in tech_lower for c in ["wordpress", "drupal", "joomla", "wix", "squarespace"]):
                    cms = tech

                # Hosting
                elif any(h in tech_lower for h in ["aws", "azure", "gcp", "vercel", "netlify", "heroku"]):
                    hosting = tech

                # Analytics
                elif any(a in tech_lower for a in ["google analytics", "matomo", "plausible", "hotjar"]):
                    analytics.append(tech)

                # CDN
                elif any(cdn_name in tech_lower for cdn_name in ["cloudflare", "akamai", "fastly", "cloudfront"]):
                    cdn = tech

                # Languages
                elif any(lang in tech_lower for lang in ["javascript", "typescript", "python", "php", "ruby"]):
                    languages.append(tech)

                # Libraries
                else:
                    libraries.append(tech)

            confidence = 85.0 if len(detected_stack) > 0 else 30.0

            return TechStack(
                frameworks=frameworks,
                cms=cms,
                hosting=hosting,
                analytics=analytics,
                cdn=cdn,
                languages=languages,
                libraries=libraries,
                confidence_score=confidence
            )

        except Exception as e:
            logger.error(f"Tech stack detection failed: {str(e)}")
            return TechStack(confidence_score=0.0)

    def _analyze_seo(self, page_data: Dict[str, Any]) -> SEOAnalysis:
        """
        Analyze SEO factors with enhanced HTML parsing.
        
        Week 8 Enhancement: Real HTML parsing for comprehensive SEO analysis
        """
        try:
            html = page_data.get("html", "")
            title = page_data.get("title")
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser') if html else None
            
            # Extract meta description
            meta_description = page_data.get("description")
            if not meta_description and soup:
                meta_tag = soup.find('meta', attrs={'name': 'description'})
                if meta_tag:
                    meta_description = meta_tag.get('content', '').strip()
            
            # Extract meta keywords
            meta_keywords = []
            if soup:
                keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
                if keywords_tag:
                    keywords_content = keywords_tag.get('content', '')
                    meta_keywords = [k.strip() for k in keywords_content.split(',') if k.strip()]
            
            # Count headings (h1-h6)
            headings_count = {}
            if soup:
                for i in range(1, 7):
                    headings = soup.find_all(f'h{i}')
                    if headings:
                        headings_count[f'h{i}'] = len(headings)
            
            # Count images without alt text
            images_without_alt = 0
            if soup:
                images = soup.find_all('img')
                for img in images:
                    if not img.get('alt') or not img.get('alt').strip():
                        images_without_alt += 1
            
            # Check for mobile-friendly viewport
            is_mobile_friendly = False
            if soup:
                viewport_tag = soup.find('meta', attrs={'name': 'viewport'})
                is_mobile_friendly = viewport_tag is not None
            
            # Detect canonical URL
            canonical_url = None
            if soup:
                canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
                if canonical_tag:
                    canonical_url = canonical_tag.get('href')
            
            # SEO checks and issues
            issues = []
            recommendations = []
            
            # Title validation
            if not title:
                issues.append("Missing title tag")
                recommendations.append("Add a descriptive title tag")
            elif len(title) < 30:
                issues.append(f"Title too short ({len(title)} chars)")
                recommendations.append("Use a longer, more descriptive title (50-60 chars)")
            elif len(title) > 60:
                issues.append(f"Title too long ({len(title)} chars)")
                recommendations.append("Shorten title to 50-60 characters for better display")
            
            # Meta description validation
            if not meta_description:
                issues.append("Missing meta description")
                recommendations.append("Add a meta description (150-160 chars)")
            elif len(meta_description) < 120:
                issues.append(f"Meta description too short ({len(meta_description)} chars)")
                recommendations.append("Expand meta description to 150-160 characters")
            elif len(meta_description) > 160:
                issues.append(f"Meta description too long ({len(meta_description)} chars)")
                recommendations.append("Shorten meta description to 150-160 characters")
            
            # Heading structure
            if soup:
                h1_tags = soup.find_all('h1')
                if len(h1_tags) == 0:
                    issues.append("Missing H1 heading")
                    recommendations.append("Add a single H1 heading for main page topic")
                elif len(h1_tags) > 1:
                    issues.append(f"Multiple H1 headings ({len(h1_tags)})")
                    recommendations.append("Use only one H1 heading per page")
            
            # Images without alt text
            if images_without_alt > 0:
                issues.append(f"{images_without_alt} images without alt text")
                recommendations.append("Add descriptive alt text to all images for accessibility")
            
            # Mobile-friendly check
            if not is_mobile_friendly:
                issues.append("Missing viewport meta tag")
                recommendations.append("Add viewport meta tag for mobile-friendly display")
            
            # Meta keywords (less important but still tracked)
            if not meta_keywords:
                # Not adding to issues as keywords meta tag is less important nowadays
                pass
            
            # Calculate SEO score (0-100)
            seo_score = 50.0  # Base score
            
            # Title (20 points)
            if title:
                if 30 <= len(title) <= 60:
                    seo_score += 20.0
                elif len(title) > 0:
                    seo_score += 10.0
            
            # Meta description (20 points)
            if meta_description:
                if 120 <= len(meta_description) <= 160:
                    seo_score += 20.0
                elif len(meta_description) > 0:
                    seo_score += 10.0
            
            # Heading structure (15 points)
            if soup:
                h1_tags = soup.find_all('h1')
                if len(h1_tags) == 1:
                    seo_score += 10.0
                if headings_count.get('h2', 0) > 0:
                    seo_score += 5.0
            
            # Content length (10 points)
            if len(html) > 2000:
                seo_score += 10.0
            elif len(html) > 1000:
                seo_score += 5.0
            
            # Mobile-friendly (10 points)
            if is_mobile_friendly:
                seo_score += 10.0
            
            # Images with alt text (10 points)
            if soup:
                images = soup.find_all('img')
                total_images = len(images)
                if total_images > 0:
                    images_with_alt = total_images - images_without_alt
                    alt_ratio = images_with_alt / total_images
                    seo_score += alt_ratio * 10.0
            
            # Meta keywords (5 points bonus)
            if meta_keywords:
                seo_score += 5.0
            
            # Cap at 100
            seo_score = min(seo_score, 100.0)
            
            # Determine SEO quality
            if seo_score >= 80:
                seo_quality = SEOQuality.EXCELLENT
            elif seo_score >= 60:
                seo_quality = SEOQuality.GOOD
            elif seo_score >= 40:
                seo_quality = SEOQuality.FAIR
            else:
                seo_quality = SEOQuality.POOR
            
            # Calculate page speed score from response time (0-100)
            page_speed_score = None
            response_time = page_data.get("response_time_ms")
            if response_time is not None:
                # Convert response time to 0-100 score (lower time = higher score)
                if response_time < 200:
                    page_speed_score = 100.0
                elif response_time < 500:
                    page_speed_score = 80.0
                elif response_time < 1000:
                    page_speed_score = 60.0
                elif response_time < 3000:
                    page_speed_score = 40.0
                else:
                    page_speed_score = 20.0

            return SEOAnalysis(
                title=title,
                meta_description=meta_description,
                meta_keywords=meta_keywords,
                headings_count=headings_count,
                images_without_alt=images_without_alt,
                has_sitemap=False,  # Would require separate sitemap.xml check
                has_robots_txt=False,  # Would require separate robots.txt check
                is_mobile_friendly=is_mobile_friendly,
                page_speed_score=page_speed_score,
                seo_score=seo_score,
                seo_quality=seo_quality,
                issues=issues,
                recommendations=recommendations
            )
        
        except Exception as e:
            logger.error(f"SEO analysis failed: {str(e)}")
            return SEOAnalysis(seo_quality=SEOQuality.POOR)

    async def _extract_contact_info(self, url: str, html: Optional[str]) -> ContactInfo:
        """
        Extract contact information with enhanced validation.
        
        Week 8 Enhancement: Pattern validation and social media integration
        """
        try:
            # Get contact data from crawler
            contact_data = await self.crawler.extract_contact_info(url, html)
            
            # Enhance with social media detection
            detected_social = self._detect_social_media(html, url)
            
            # Merge social media data (detected takes priority if not in crawler data)
            social_media = contact_data.get("social_media", {})
            for platform, link in detected_social.items():
                if platform not in social_media:
                    social_media[platform] = link
            
            # Validate and filter emails
            emails = self._validate_emails(contact_data.get("emails", []))
            
            # Validate and filter phones
            phones = self._validate_phones(contact_data.get("phones", []))
            
            return ContactInfo(
                emails=emails,
                phones=phones,
                addresses=contact_data.get("addresses", []),
                social_media=social_media,
                contact_page_url=contact_data.get("contact_page_url"),
                has_contact_form=contact_data.get("has_contact_form", False)
            )
        
        except Exception as e:
            logger.error(f"Contact extraction failed: {str(e)}")
            return ContactInfo()

    def _detect_social_media(self, html: Optional[str], url: str) -> Dict[str, str]:
        """
        Detect social media presence from HTML.
        
        Week 8 Enhancement: Enhanced social media detection with multiple patterns
        
        Returns:
            Dictionary mapping platform names to profile URLs
        """
        social_media = {}
        
        if not html:
            return social_media
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Social media patterns
            patterns = {
                'facebook': [
                    r'https?://(?:www\.)?facebook\.com/[\w.-]+',
                    r'https?://(?:www\.)?fb\.com/[\w.-]+',
                ],
                'twitter': [
                    r'https?://(?:www\.)?twitter\.com/[\w.-]+',
                    r'https?://(?:www\.)?x\.com/[\w.-]+',
                ],
                'linkedin': [
                    r'https?://(?:www\.)?linkedin\.com/(?:company|in)/[\w.-]+',
                ],
                'instagram': [
                    r'https?://(?:www\.)?instagram\.com/[\w.-]+',
                ],
                'youtube': [
                    r'https?://(?:www\.)?youtube\.com/(?:c|channel|user)/[\w.-]+',
                    r'https?://(?:www\.)?youtube\.com/@[\w.-]+',
                ],
                'github': [
                    r'https?://(?:www\.)?github\.com/[\w.-]+',
                ],
                'tiktok': [
                    r'https?://(?:www\.)?tiktok\.com/@[\w.-]+',
                ],
                'pinterest': [
                    r'https?://(?:www\.)?pinterest\.com/[\w.-]+',
                ],
            }
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href'].strip()
                
                # Match against patterns
                for platform, pattern_list in patterns.items():
                    if platform not in social_media:
                        for pattern in pattern_list:
                            if re.match(pattern, href, re.IGNORECASE):
                                social_media[platform] = href
                                break
            
            # Also check for social media in footer, header, and nav elements
            for section in ['footer', 'header', 'nav']:
                section_elem = soup.find(section)
                if section_elem:
                    section_links = section_elem.find_all('a', href=True)
                    for link in section_links:
                        href = link['href'].strip()
                        for platform, pattern_list in patterns.items():
                            if platform not in social_media:
                                for pattern in pattern_list:
                                    if re.match(pattern, href, re.IGNORECASE):
                                        social_media[platform] = href
                                        break
            
            logger.info(f"Detected {len(social_media)} social media platforms for {url}")
            return social_media
        
        except Exception as e:
            logger.error(f"Social media detection failed: {str(e)}")
            return {}

    def _validate_emails(self, emails: List[str]) -> List[str]:
        """
        Validate email addresses using regex patterns.
        
        Week 8 Enhancement: Email pattern validation
        """
        if not emails:
            return []
        
        # Email validation pattern (RFC 5322 simplified)
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        validated = []
        seen = set()  # Remove duplicates
        
        for email in emails:
            email = email.strip().lower()
            
            # Skip common placeholder/spam emails
            if email in ['info@example.com', 'contact@example.com', 'test@test.com']:
                continue
            
            # Validate format
            if email_pattern.match(email) and email not in seen:
                validated.append(email)
                seen.add(email)
        
        return validated
    
    def _validate_phones(self, phones: List[str]) -> List[str]:
        """
        Validate phone numbers.
        
        Week 8 Enhancement: Phone number pattern validation
        """
        if not phones:
            return []
        
        validated = []
        seen = set()  # Remove duplicates
        
        for phone in phones:
            phone = phone.strip()
            
            # Skip placeholder numbers
            if phone in ['123-456-7890', '000-000-0000', '111-111-1111']:
                continue
            
            # Must contain at least 7 digits (minimum valid phone)
            digits = re.sub(r'\D', '', phone)
            if len(digits) >= 7 and phone not in seen:
                validated.append(phone)
                seen.add(phone)
        
        return validated

    def _analyze_performance(
        self,
        response_time_ms: Optional[int],
        is_mobile_friendly: bool,
        content_length: int
    ) -> Dict[str, Any]:
        """
        Analyze website performance metrics.
        
        Week 8 Enhancement: Performance analysis and scoring
        
        Returns:
            Dictionary with performance metrics and score
        """
        performance = {
            'response_time_ms': response_time_ms,
            'is_mobile_friendly': is_mobile_friendly,
            'content_size_bytes': content_length,
            'performance_score': 0.0,
            'performance_level': 'poor',
            'issues': [],
            'recommendations': []
        }
        
        try:
            score = 50.0  # Base score
            
            # Response time scoring (40 points)
            if response_time_ms is not None:
                if response_time_ms < 200:
                    score += 40.0
                    performance['performance_level'] = 'excellent'
                elif response_time_ms < 500:
                    score += 30.0
                    performance['performance_level'] = 'good'
                elif response_time_ms < 1000:
                    score += 20.0
                    performance['performance_level'] = 'fair'
                elif response_time_ms < 3000:
                    score += 10.0
                    performance['performance_level'] = 'poor'
                else:
                    performance['performance_level'] = 'very poor'
                    performance['issues'].append(f"Slow response time: {response_time_ms}ms")
                    performance['recommendations'].append("Optimize server response time")
            
            # Mobile-friendly scoring (30 points)
            if is_mobile_friendly:
                score += 30.0
            else:
                performance['issues'].append("Not mobile-friendly")
                performance['recommendations'].append("Add responsive design and viewport meta tag")
            
            # Content size scoring (20 points)
            if content_length > 0:
                if content_length < 100000:  # < 100KB
                    score += 20.0
                elif content_length < 500000:  # < 500KB
                    score += 15.0
                elif content_length < 1000000:  # < 1MB
                    score += 10.0
                else:
                    score += 5.0
                    performance['issues'].append(f"Large page size: {content_length / 1000:.1f}KB")
                    performance['recommendations'].append("Reduce page size through optimization")
            
            performance['performance_score'] = min(score, 100.0)
            
            # Update performance level based on final score
            if performance['performance_score'] >= 80:
                performance['performance_level'] = 'excellent'
            elif performance['performance_score'] >= 60:
                performance['performance_level'] = 'good'
            elif performance['performance_score'] >= 40:
                performance['performance_level'] = 'fair'
            else:
                performance['performance_level'] = 'poor'
        
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
        
        return performance

    def _calculate_online_presence_score(
        self,
        tech_stack: TechStack,
        seo: SEOAnalysis,
        contact_info: ContactInfo
    ) -> float:
        """Calculate overall online presence score (0-100)."""
        score = 0.0

        # Tech stack (30 points)
        if tech_stack.frameworks:
            score += 15.0
        if tech_stack.cdn or tech_stack.hosting:
            score += 10.0
        if tech_stack.analytics:
            score += 5.0

        # SEO (40 points)
        score += (seo.seo_score * 0.4)

        # Contact info (30 points)
        if contact_info.emails:
            score += 10.0
        if contact_info.phones:
            score += 5.0
        if contact_info.social_media:
            score += 10.0
        if contact_info.has_contact_form:
            score += 5.0

        return min(score, 100.0)

    def _identify_strengths_weaknesses(
        self,
        tech_stack: TechStack,
        seo: SEOAnalysis,
        contact_info: ContactInfo
    ) -> tuple[List[str], List[str]]:
        """Identify strengths and weaknesses."""
        strengths = []
        weaknesses = []

        # Tech stack
        if tech_stack.frameworks:
            strengths.append(f"Modern tech stack: {', '.join(tech_stack.frameworks[:2])}")
        else:
            weaknesses.append("No modern frameworks detected")

        if tech_stack.cdn:
            strengths.append(f"Using CDN: {tech_stack.cdn}")

        # SEO
        if seo.seo_quality in [SEOQuality.EXCELLENT, SEOQuality.GOOD]:
            strengths.append(f"Good SEO quality ({seo.seo_score:.0f}/100)")
        else:
            weaknesses.append(f"Poor SEO quality ({seo.seo_score:.0f}/100)")

        # Contact info
        if contact_info.emails:
            strengths.append(f"Contact emails available ({len(contact_info.emails)})")
        else:
            weaknesses.append("No contact emails found")

        if contact_info.social_media:
            strengths.append(f"Social media presence ({len(contact_info.social_media)} platforms)")
        else:
            weaknesses.append("No social media links found")

        return strengths, weaknesses

    def _generate_recommendations(
        self,
        weaknesses: List[str],
        seo: SEOAnalysis
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Add SEO recommendations
        recommendations.extend(seo.recommendations)

        # Add general recommendations based on weaknesses
        if any("social media" in w.lower() for w in weaknesses):
            recommendations.append("Add social media profile links (LinkedIn, Facebook, Twitter)")

        if any("contact" in w.lower() for w in weaknesses):
            recommendations.append("Add visible contact information (email, phone)")

        if any("seo" in w.lower() for w in weaknesses):
            recommendations.append("Improve SEO by adding meta tags and structured content")

        return recommendations

    def _calculate_confidence(
        self,
        page_data: Dict[str, Any],
        tech_stack: TechStack,
        seo: SEOAnalysis
    ) -> float:
        """Calculate confidence score."""
        confidence = 50.0  # Base confidence

        if page_data.get("success"):
            confidence += 20.0

        if tech_stack.confidence_score > 0:
            confidence += (tech_stack.confidence_score * 0.2)

        if seo.seo_score > 0:
            confidence += 10.0

        return min(confidence, 100.0)
