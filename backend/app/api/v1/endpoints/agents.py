"""
Agents API Endpoints - Week 3 Implementation

Provides access to autonomous agents for market intelligence analysis.
Currently implements: CompanyProfileAgent

Features:
- Redis caching for performance
- Rate limiting to prevent abuse
- Timeout handling for reliability
- Comprehensive error handling
- OpenAPI documentation

Author: MI-Navigator Development Team
Created: 2026-01-24 (Week 3)
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from collections import defaultdict

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.agents.company_profile_agent import CompanyProfileAgent, CompanyProfileOutput
from app.agents.financial_analysis_agent import FinancialAnalysisAgent, FinancialAnalysisOutput
from app.agents.digital_presence_agent import DigitalPresenceAgent, DigitalPresenceOutput
from app.agents.competitor_mapping_agent import CompetitorMappingAgent, CompetitorMappingOutput
from app.agents.fact_checker_agent import FactCheckerAgent, FactCheckerOutput
from app.agents.insight_generator_agent import InsightGeneratorAgent, InsightGeneratorOutput
from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis client for caching (lazy initialization)
redis_client: Optional[redis.Redis] = None

# Simple in-memory rate limiter (IP -> [(timestamp, count)])
rate_limit_store: Dict[str, List[datetime]] = defaultdict(list)
RATE_LIMIT_REQUESTS = 10  # requests
RATE_LIMIT_WINDOW = 60  # seconds

router = APIRouter()


# ============================================================================
# RATE LIMITING UTILITIES
# ============================================================================

def check_rate_limit(client_ip: str, max_requests: int = RATE_LIMIT_REQUESTS, window_seconds: int = RATE_LIMIT_WINDOW) -> bool:
    """
    Check if client has exceeded rate limit.

    Simple in-memory rate limiter using sliding window.

    Args:
        client_ip: Client IP address
        max_requests: Maximum requests allowed in window
        window_seconds: Time window in seconds

    Returns:
        True if rate limit OK, False if exceeded
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(seconds=window_seconds)

    # Clean old entries
    rate_limit_store[client_ip] = [
        ts for ts in rate_limit_store[client_ip]
        if ts > cutoff
    ]

    # Check limit
    if len(rate_limit_store[client_ip]) >= max_requests:
        return False

    # Add current request
    rate_limit_store[client_ip].append(now)

    return True


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class CompanyProfileRequest(BaseModel):
    """
    Request model for company profile agent.

    Supports identification by NIP, KRS, or REGON number.
    """

    target: str = Field(
        ...,
        description="Company identifier (NIP, KRS, or REGON number)",
        example="NIP 1234567890"
    )

    include_ownership: bool = Field(
        default=True,
        description="Include ownership structure in response"
    )

    include_board: bool = Field(
        default=True,
        description="Include management board in response"
    )

    include_financials: bool = Field(
        default=False,
        description="Include financial data (requires additional processing)"
    )

    use_cache: bool = Field(
        default=True,
        description="Use cached data if available"
    )

    @validator('target')
    def validate_target(cls, v):
        """Validate target format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Target cannot be empty")

        # Basic validation - actual validation happens in agent
        v = v.strip()

        if len(v) < 9:
            raise ValueError("Target identifier too short")

        return v

    class Config:
        schema_extra = {
            "example": {
                "target": "NIP 1234567890",
                "include_ownership": True,
                "include_board": True,
                "include_financials": False,
                "use_cache": True
            }
        }


class CompanyProfileResponse(BaseModel):
    """
    Response model for company profile agent.

    Contains comprehensive company information from multiple sources.
    """

    success: bool = Field(
        ...,
        description="Whether the request was successful"
    )

    company_name: Optional[str] = Field(
        None,
        description="Official company name"
    )

    nip: Optional[str] = Field(
        None,
        description="10-digit NIP (tax identification number)"
    )

    krs: Optional[str] = Field(
        None,
        description="10-digit KRS (court registration number)"
    )

    regon: Optional[str] = Field(
        None,
        description="9 or 14-digit REGON number"
    )

    legal_form: Optional[str] = Field(
        None,
        description="Legal form (e.g., 'Spółka z o.o.')"
    )

    registration_date: Optional[str] = Field(
        None,
        description="Company registration date (ISO format)"
    )

    address: Optional[Dict[str, Any]] = Field(
        None,
        description="Company address details"
    )

    pkd_main: Optional[str] = Field(
        None,
        description="Primary PKD classification code"
    )

    industry: Optional[str] = Field(
        None,
        description="Industry classification"
    )

    ownership_structure: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Ownership structure (if include_ownership=True)"
    )

    management_board: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Management board members (if include_board=True)"
    )

    share_capital: Optional[str] = Field(
        None,
        description="Share capital amount"
    )

    employee_range: Optional[str] = Field(
        None,
        description="Employee count range"
    )

    data_sources: Optional[List[str]] = Field(
        None,
        description="Sources used for data retrieval"
    )

    cached: bool = Field(
        default=False,
        description="Whether response was served from cache"
    )

    processing_time_ms: Optional[int] = Field(
        None,
        description="Processing time in milliseconds"
    )

    error: Optional[str] = Field(
        None,
        description="Error message if success=False"
    )

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "company_name": "Example Sp. z o.o.",
                "nip": "1234567890",
                "krs": "0000123456",
                "regon": "123456789",
                "legal_form": "Spółka z ograniczoną odpowiedzialnością",
                "registration_date": "2020-01-15",
                "address": {
                    "street": "ul. Testowa 123",
                    "city": "Warszawa",
                    "postal_code": "00-001",
                    "voivodeship": "Mazowieckie"
                },
                "pkd_main": "62.01.Z",
                "industry": "Działalność związana z oprogramowaniem",
                "ownership_structure": [
                    {
                        "owner_name": "Jan Kowalski",
                        "ownership_percentage": 51.0,
                        "ownership_type": "direct"
                    }
                ],
                "management_board": [
                    {
                        "name": "Jan Kowalski",
                        "position": "Prezes Zarządu",
                        "appointment_date": "2020-01-15"
                    }
                ],
                "share_capital": "100000 PLN",
                "employee_range": "10-49",
                "data_sources": ["KRS", "GUS", "REGON"],
                "cached": False,
                "processing_time_ms": 1250
            }
        }



# ============================================================================
# FINANCIAL ANALYSIS AGENT MODELS (Week 6)
# ============================================================================

class FinancialAnalysisRequest(BaseModel):
    """
    Request model for financial analysis agent (Week 6).
    
    Supports identification by NIP or KRS number.
    """
    
    target: str = Field(
        ...,
        description="Company identifier (KRS or NIP number)",
        example="KRS 0000123456"
    )
    
    use_cache: bool = Field(
        default=True,
        description="Use cached data if available"
    )
    
    @validator('target')
    def validate_target(cls, v):
        """Validate target format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Target cannot be empty")
        
        v = v.strip()
        
        if len(v) < 9:
            raise ValueError("Target identifier too short")
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "target": "KRS 0000123456",
                "use_cache": True
            }
        }


class FinancialAnalysisResponse(BaseModel):
    """
    Response model for financial analysis agent (Week 6).
    
    Contains comprehensive financial analysis results.
    """
    
    success: bool = Field(
        ...,
        description="Whether the request was successful"
    )
    
    target: str = Field(
        ...,
        description="Target company identifier"
    )
    
    company_name: Optional[str] = Field(
        None,
        description="Company name"
    )
    
    periods_analyzed: int = Field(
        0,
        description="Number of financial periods analyzed"
    )
    
    # Financial Health Score
    overall_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Overall financial health score (0-100)"
    )
    
    risk_level: Optional[str] = Field(
        None,
        description="Risk level: low|moderate|high|critical"
    )
    
    altman_z_score: Optional[float] = Field(
        None,
        description="Altman Z-Score for bankruptcy prediction"
    )
    
    bankruptcy_risk: Optional[str] = Field(
        None,
        description="Bankruptcy risk: safe|grey_zone|distress"
    )
    
    # Component Scores
    liquidity_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Liquidity score"
    )
    
    profitability_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Profitability score"
    )
    
    leverage_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Leverage score"
    )
    
    cash_flow_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Cash flow score"
    )
    
    # Industry Benchmark
    industry_benchmark: Optional[Dict[str, Any]] = Field(
        None,
        description="Industry benchmarking data"
    )
    
    # Strengths and Weaknesses
    strengths: Optional[List[str]] = Field(
        None,
        description="Key financial strengths"
    )
    
    weaknesses: Optional[List[str]] = Field(
        None,
        description="Key financial weaknesses"
    )
    
    recommendations: Optional[List[str]] = Field(
        None,
        description="Actionable recommendations"
    )
    
    # Metadata
    data_sources: Optional[List[str]] = Field(
        None,
        description="Sources used for data retrieval"
    )
    
    confidence_score: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Confidence in analysis results"
    )
    
    cached: bool = Field(
        default=False,
        description="Whether response was served from cache"
    )
    
    processing_time_ms: Optional[int] = Field(
        None,
        description="Processing time in milliseconds"
    )
    
    error: Optional[str] = Field(
        None,
        description="Error message if success=False"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "target": "KRS 0000123456",
                "company_name": "Example Sp. z o.o.",
                "periods_analyzed": 3,
                "overall_score": 75.5,
                "risk_level": "moderate",
                "altman_z_score": 2.8,
                "bankruptcy_risk": "safe",
                "liquidity_score": 80.0,
                "profitability_score": 70.0,
                "leverage_score": 75.0,
                "cash_flow_score": 78.0,
                "strengths": ["Strong liquidity position", "Positive cash flow"],
                "weaknesses": ["High leverage"],
                "recommendations": ["Reduce debt levels"],
                "data_sources": ["KRS", "GUS"],
                "confidence_score": 85.0,
                "cached": False,
                "processing_time_ms": 2500
            }
        }

# ============================================================================
# DIGITAL PRESENCE AGENT MODELS (Week 9)
# ============================================================================

class DigitalPresenceRequest(BaseModel):
    """
    Request model for digital presence agent (Week 9).
    
    Supports identification by website URL or company domain.
    """
    
    target: str = Field(
        ...,
        description="Website URL or domain to analyze",
        example="https://example.com"
    )
    
    use_cache: bool = Field(
        default=True,
        description="Use cached data if available"
    )
    
    @validator('target')
    def validate_target(cls, v):
        """Validate target format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Target cannot be empty")
        
        v = v.strip()
        
        # Basic validation - actual normalization happens in agent
        if len(v) < 4:
            raise ValueError("Target URL/domain too short")
        
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "target": "https://example.com",
                "use_cache": True
            }
        }


class DigitalPresenceResponse(BaseModel):
    """
    Response model for digital presence agent (Week 9).
    
    Contains comprehensive website analysis and online presence assessment.
    """
    
    success: bool = Field(
        ...,
        description="Whether the request was successful"
    )
    
    target: Optional[str] = Field(
        None,
        description="Original target URL/domain"
    )
    
    website_url: Optional[str] = Field(
        None,
        description="Normalized website URL"
    )
    
    company_name: Optional[str] = Field(
        None,
        description="Company name extracted from website"
    )
    
    # Website Status
    website_status: Optional[str] = Field(
        None,
        description="Website status: online|offline|slow|error"
    )
    
    response_time_ms: Optional[int] = Field(
        None,
        description="Website response time in milliseconds"
    )
    
    # Tech Stack
    tech_stack: Optional[Dict[str, Any]] = Field(
        None,
        description="Detected technology stack"
    )
    
    # SEO Analysis
    seo_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="SEO quality score (0-100)"
    )
    
    seo_quality: Optional[str] = Field(
        None,
        description="SEO quality level: excellent|good|fair|poor"
    )
    
    is_mobile_friendly: Optional[bool] = Field(
        None,
        description="Whether website is mobile-friendly"
    )
    
    page_speed_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Page speed score (0-100)"
    )
    
    # Social Media & Contact
    social_media_platforms: Optional[List[str]] = Field(
        None,
        description="Detected social media platforms"
    )
    
    contact_emails: Optional[List[str]] = Field(
        None,
        description="Extracted contact email addresses"
    )
    
    contact_phones: Optional[List[str]] = Field(
        None,
        description="Extracted contact phone numbers"
    )
    
    # Overall Assessment
    online_presence_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Overall online presence score (0-100)"
    )
    
    strengths: Optional[List[str]] = Field(
        None,
        description="Key digital presence strengths"
    )
    
    weaknesses: Optional[List[str]] = Field(
        None,
        description="Key digital presence weaknesses"
    )
    
    recommendations: Optional[List[str]] = Field(
        None,
        description="Actionable recommendations for improvement"
    )
    
    # Metadata
    data_sources: Optional[List[str]] = Field(
        None,
        description="Sources used for data retrieval"
    )
    
    confidence_score: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Confidence in analysis results"
    )
    
    cached: bool = Field(
        default=False,
        description="Whether response was served from cache"
    )
    
    processing_time_ms: Optional[int] = Field(
        None,
        description="Processing time in milliseconds"
    )
    
    error: Optional[str] = Field(
        None,
        description="Error message if success=False"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "target": "https://example.com",
                "website_url": "https://example.com",
                "company_name": "Example Company",
                "website_status": "online",
                "response_time_ms": 250,
                "tech_stack": {
                    "frameworks": ["React", "Next.js"],
                    "hosting": "Vercel",
                    "cdn": "Cloudflare"
                },
                "seo_score": 85.0,
                "seo_quality": "excellent",
                "is_mobile_friendly": True,
                "page_speed_score": 90.0,
                "social_media_platforms": ["facebook", "linkedin", "twitter"],
                "contact_emails": ["info@example.com"],
                "contact_phones": ["+48 123 456 789"],
                "online_presence_score": 82.5,
                "strengths": ["Modern tech stack", "Excellent SEO", "Active social media"],
                "weaknesses": ["No contact form"],
                "recommendations": ["Add contact form for better user engagement"],
                "data_sources": ["Jina Reader", "Tech Stack Detection"],
                "confidence_score": 88.0,
                "cached": False,
                "processing_time_ms": 1800
            }
        }


# ============================================================================
# COMPETITOR MAPPING AGENT MODELS (Week 12)
# ============================================================================

class CompetitorMappingRequest(BaseModel):
    """
    Request model for competitor mapping agent (Week 12).

    Supports identification by company name, KRS, or NIP number.
    """

    target: str = Field(
        ...,
        description="Company identifier (name, KRS, or NIP number)",
        example="NIP 1234567890"
    )

    include_swot: bool = Field(
        default=True,
        description="Include SWOT analysis in response"
    )

    include_porter: bool = Field(
        default=True,
        description="Include Porter's Five Forces analysis in response"
    )

    include_advantages: bool = Field(
        default=True,
        description="Include competitive advantages analysis in response"
    )

    max_competitors: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of competitors to analyze"
    )

    use_cache: bool = Field(
        default=True,
        description="Use cached data if available"
    )

    @validator('target')
    def validate_target(cls, v):
        """Validate target format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Target cannot be empty")

        v = v.strip()

        if len(v) < 3:
            raise ValueError("Target identifier too short")

        return v

    class Config:
        schema_extra = {
            "example": {
                "target": "NIP 1234567890",
                "include_swot": True,
                "include_porter": True,
                "include_advantages": True,
                "max_competitors": 10,
                "use_cache": True
            }
        }


class CompetitorMappingResponse(BaseModel):
    """
    Response model for competitor mapping agent (Week 12).

    Contains comprehensive competitive intelligence and market positioning analysis.
    """

    success: bool = Field(
        ...,
        description="Whether the request was successful"
    )

    target_company: Optional[str] = Field(
        None,
        description="Target company name"
    )

    # Market Position
    market_position: Optional[str] = Field(
        None,
        description="Market position classification: leader|challenger|follower|niche"
    )

    market_share_percentage: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Estimated market share percentage"
    )

    rank_in_industry: Optional[int] = Field(
        None,
        ge=1,
        description="Ranking position in the industry"
    )

    # Competitors
    total_competitors: int = Field(
        0,
        ge=0,
        description="Total number of competitors identified"
    )

    direct_competitors: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Direct competitors with similarity scores"
    )

    indirect_competitors: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Indirect competitors"
    )

    # Strategic Analysis
    swot_analysis: Optional[Dict[str, Any]] = Field(
        None,
        description="SWOT analysis (if include_swot=True)"
    )

    porter_analysis: Optional[Dict[str, Any]] = Field(
        None,
        description="Porter's Five Forces analysis (if include_porter=True)"
    )

    competitive_advantages: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Competitive advantages (if include_advantages=True)"
    )

    # Insights
    competitive_insights: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Strategic competitive insights"
    )

    market_gaps: Optional[List[str]] = Field(
        None,
        description="Identified market gaps and opportunities"
    )

    strategic_recommendations: Optional[List[str]] = Field(
        None,
        description="Strategic recommendations"
    )

    # Metadata
    data_sources: Optional[List[str]] = Field(
        None,
        description="Sources used for data retrieval"
    )

    confidence_score: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Confidence in analysis results"
    )

    cached: bool = Field(
        default=False,
        description="Whether response was served from cache"
    )

    processing_time_ms: Optional[int] = Field(
        None,
        description="Processing time in milliseconds"
    )

    error: Optional[str] = Field(
        None,
        description="Error message if success=False"
    )

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "target_company": "Example Sp. z o.o.",
                "market_position": "challenger",
                "market_share_percentage": 18.5,
                "rank_in_industry": 3,
                "total_competitors": 8,
                "direct_competitors": [
                    {
                        "company_name": "Competitor A",
                        "similarity_score": 85.0,
                        "market_share": 32.0
                    },
                    {
                        "company_name": "Competitor B",
                        "similarity_score": 78.0,
                        "market_share": 25.0
                    }
                ],
                "swot_analysis": {
                    "strengths": ["Strong brand", "Experienced team"],
                    "weaknesses": ["Limited resources"],
                    "opportunities": ["Market expansion"],
                    "threats": ["New entrants"]
                },
                "porter_analysis": {
                    "industry_attractiveness": "medium",
                    "competitive_rivalry": "high"
                },
                "competitive_advantages": [
                    {
                        "advantage_type": "differentiation",
                        "strength": "strong",
                        "description": "Unique value proposition"
                    }
                ],
                "competitive_insights": [
                    {
                        "type": "market_trend",
                        "description": "Growing demand for digital solutions"
                    }
                ],
                "market_gaps": ["Underserved SME segment"],
                "strategic_recommendations": [
                    "Focus on differentiation strategy",
                    "Build customer loyalty programs"
                ],
                "data_sources": ["KRS", "GUS", "Market Analysis"],
                "confidence_score": 82.0,
                "cached": False,
                "processing_time_ms": 2500
            }
        }


# ============================================================================
# WEEK 15: FACT CHECKER AGENT MODELS
# ============================================================================

class FactCheckerRequest(BaseModel):
    """
    Request model for fact checker agent (Week 15).

    Supports fact verification with claim extraction and multi-source validation.
    """

    target: str = Field(
        ...,
        description="Company identifier (NIP, KRS, or REGON number)",
        example="NIP 1234567890"
    )

    claims: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Claims to verify. If not provided, claims will be extracted from context."
    )

    text_to_analyze: Optional[str] = Field(
        default=None,
        description="Free text to analyze and extract claims from"
    )

    include_citations: bool = Field(
        default=True,
        description="Include source citations in response"
    )

    min_confidence: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Minimum confidence threshold (0-100)"
    )

    use_cache: bool = Field(
        default=True,
        description="Use cached data if available"
    )

    @validator('target')
    def validate_target(cls, v):
        """Validate target format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Target cannot be empty")

        v = v.strip()

        if len(v) < 9:
            raise ValueError("Target identifier too short")

        return v

    class Config:
        schema_extra = {
            "example": {
                "target": "NIP 1234567890",
                "claims": [
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
                "include_citations": True,
                "min_confidence": 50.0,
                "use_cache": True
            }
        }


class FactCheckerResponse(BaseModel):
    """
    Response model for fact checker agent (Week 15).

    Contains verification results with source citations and confidence scores.
    """

    success: bool = Field(
        ...,
        description="Whether the request was successful"
    )

    target: Optional[str] = Field(
        None,
        description="Company identifier that was analyzed"
    )

    # Verification Results
    total_claims_checked: int = Field(
        0,
        ge=0,
        description="Total number of claims checked"
    )

    verified_claims_count: int = Field(
        0,
        ge=0,
        description="Number of verified claims"
    )

    contradicted_claims_count: int = Field(
        0,
        ge=0,
        description="Number of contradicted claims"
    )

    unverified_claims_count: int = Field(
        0,
        ge=0,
        description="Number of unverified claims"
    )

    # Detailed Verifications
    verifications: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Detailed verification results for each claim"
    )

    # Source Information
    data_sources: Optional[List[str]] = Field(
        None,
        description="Sources used for verification"
    )

    primary_sources_used: int = Field(
        0,
        ge=0,
        description="Number of primary sources used"
    )

    average_source_credibility: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Average credibility score of sources"
    )

    # Citations (Week 15 feature)
    citations: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Formatted citations for all sources"
    )

    # Quality Metrics
    overall_confidence_score: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Overall confidence in verification results"
    )

    data_freshness_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Data freshness score (0-100)"
    )

    # Issues and Warnings
    critical_issues: Optional[List[str]] = Field(
        None,
        description="Critical issues identified"
    )

    warnings: Optional[List[str]] = Field(
        None,
        description="Warnings about data quality or verification"
    )

    errors: Optional[List[str]] = Field(
        None,
        description="Errors encountered during verification"
    )

    # Metadata
    cached: bool = Field(
        default=False,
        description="Whether response was served from cache"
    )

    processing_time_ms: Optional[int] = Field(
        None,
        description="Processing time in milliseconds"
    )

    error: Optional[str] = Field(
        None,
        description="Error message if success=False"
    )

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "target": "NIP 1234567890",
                "total_claims_checked": 2,
                "verified_claims_count": 1,
                "contradicted_claims_count": 0,
                "unverified_claims_count": 1,
                "verifications": [
                    {
                        "claim_text": "Company has 100 employees",
                        "verification_status": "verified",
                        "confidence_score": 85.0,
                        "supporting_sources": ["KRS", "GUS"],
                        "reliability_assessment": "reliable"
                    }
                ],
                "data_sources": ["KRS", "GUS", "Company Website"],
                "primary_sources_used": 2,
                "average_source_credibility": 90.0,
                "citations": [
                    {
                        "source_name": "KRS Registry",
                        "source_type": "official_registry",
                        "url": "https://krs.gov.pl",
                        "citation": "KRS Registry. (2026). Company Profile. Retrieved from https://krs.gov.pl",
                        "retrieved_date": "2026-01-25"
                    }
                ],
                "overall_confidence_score": 72.5,
                "data_freshness_score": 85.0,
                "critical_issues": [],
                "warnings": [],
                "errors": [],
                "cached": False,
                "processing_time_ms": 1500
            }
        }


class InsightGeneratorRequest(BaseModel):
    """
    Request model for insight generator agent (Week 18).

    Generates patterns, predictions, risks, and opportunities from company data.
    """

    target: str = Field(
        ...,
        description="Company identifier or context description",
        example="Tech Company Analysis"
    )

    # Context Data
    financial_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Historical financial data for trend analysis"
    )

    market_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Market conditions and trends data"
    )

    competitor_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Competitor analysis data"
    )

    digital_presence: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Digital presence metrics and analysis"
    )

    # Analysis Parameters
    min_confidence: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Minimum confidence score for insights (0-100)"
    )

    max_insights: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of insights to generate"
    )

    include_scenarios: bool = Field(
        default=True,
        description="Include scenario analysis (best/worst/likely)"
    )

    use_cache: bool = Field(
        default=True,
        description="Use cached data if available"
    )

    @validator('target')
    def validate_target(cls, v):
        """Validate target format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Target cannot be empty")
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Target description too short (minimum 3 characters)")
        return v

    @validator('min_confidence')
    def validate_confidence(cls, v):
        """Validate confidence threshold."""
        if v < 0 or v > 100:
            raise ValueError("Confidence must be between 0 and 100")
        return v

    class Config:
        schema_extra = {
            "example": {
                "target": "TechCorp S.A. Market Analysis",
                "financial_data": [
                    {"period": "2023", "revenue": 1000000, "profit_margin": 15.5},
                    {"period": "2024", "revenue": 1200000, "profit_margin": 18.0}
                ],
                "market_data": {
                    "market_size": 5000000,
                    "growth_rate": 12.5,
                    "market_share": 8.0
                },
                "min_confidence": 60.0,
                "max_insights": 10,
                "include_scenarios": True,
                "use_cache": True
            }
        }


class InsightGeneratorResponse(BaseModel):
    """
    Response model for insight generator agent (Week 18).

    Contains insights, patterns, predictions, risks, and opportunities.
    """

    success: bool = Field(
        ...,
        description="Whether the request was successful"
    )

    target: Optional[str] = Field(
        None,
        description="Target that was analyzed"
    )

    # Insights
    total_insights: int = Field(
        0,
        ge=0,
        description="Total number of insights generated"
    )

    insights: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Generated insights with priorities"
    )

    # Patterns
    total_patterns: int = Field(
        0,
        ge=0,
        description="Total number of patterns detected"
    )

    patterns_detected: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Detected patterns in the data"
    )

    # Predictions
    total_predictions: int = Field(
        0,
        ge=0,
        description="Total number of predictions made"
    )

    predictions: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Future predictions and forecasts"
    )

    # Risks
    total_risks: int = Field(
        0,
        ge=0,
        description="Total number of risks identified"
    )

    risks_identified: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Identified risks with severity levels"
    )

    # Opportunities
    total_opportunities: int = Field(
        0,
        ge=0,
        description="Total number of opportunities found"
    )

    opportunities: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Identified opportunities for growth"
    )

    # Quality Metrics
    overall_confidence_score: float = Field(
        0.0,
        ge=0,
        le=100,
        description="Overall confidence in insights (0-100)"
    )

    data_quality_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Quality score of input data (0-100)"
    )

    # Analysis Metadata
    analysis_depth: Optional[str] = Field(
        None,
        description="Depth of analysis performed"
    )

    data_points_analyzed: int = Field(
        0,
        ge=0,
        description="Number of data points analyzed"
    )

    # Issues and Warnings
    warnings: Optional[List[str]] = Field(
        None,
        description="Warnings about data quality or analysis"
    )

    errors: Optional[List[str]] = Field(
        None,
        description="Errors encountered during analysis"
    )

    # Metadata
    cached: bool = Field(
        default=False,
        description="Whether response was served from cache"
    )

    processing_time_ms: Optional[int] = Field(
        None,
        description="Processing time in milliseconds"
    )

    error: Optional[str] = Field(
        None,
        description="Error message if success=False"
    )

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "target": "TechCorp S.A. Market Analysis",
                "total_insights": 5,
                "insights": [
                    {
                        "insight_id": "insight_1",
                        "insight_type": "trend",
                        "insight_text": "Revenue growth accelerating with 20% YoY increase",
                        "priority": "high",
                        "relevance_score": 85.0,
                        "is_actionable": True,
                        "recommended_actions": ["Increase production capacity", "Expand sales team"]
                    }
                ],
                "total_patterns": 3,
                "patterns_detected": [
                    {
                        "pattern_id": "pattern_1",
                        "pattern_type": "growth",
                        "pattern_description": "Strong growth pattern in revenue",
                        "confidence_score": 90.0,
                        "strength": 85.0
                    }
                ],
                "total_predictions": 2,
                "predictions": [
                    {
                        "prediction_id": "pred_1",
                        "prediction_text": "Revenue likely to reach 1.5M in next period",
                        "prediction_confidence": "high",
                        "confidence_score": 80.0,
                        "time_horizon": "short_term"
                    }
                ],
                "total_risks": 1,
                "risks_identified": [
                    {
                        "risk_id": "risk_1",
                        "risk_type": "market",
                        "risk_description": "Market volatility may impact growth",
                        "risk_level": "medium",
                        "severity_score": 60.0
                    }
                ],
                "total_opportunities": 2,
                "opportunities": [
                    {
                        "opportunity_id": "opp_1",
                        "opportunity_type": "market_expansion",
                        "opportunity_description": "Strong demand in new market segment",
                        "potential_impact": "high",
                        "feasibility_score": 75.0
                    }
                ],
                "overall_confidence_score": 78.5,
                "data_quality_score": 85.0,
                "analysis_depth": "comprehensive",
                "data_points_analyzed": 24,
                "warnings": [],
                "errors": [],
                "cached": False,
                "processing_time_ms": 2500
            }
        }


class AgentStatusResponse(BaseModel):
    """Health check response for agents system."""

    status: str = Field(..., description="System status")
    agents_available: List[str] = Field(..., description="Available agent types")
    cache_enabled: bool = Field(..., description="Whether Redis caching is enabled")
    timestamp: str = Field(..., description="Current timestamp")


# ============================================================================
# REDIS CACHING UTILITIES
# ============================================================================

async def get_redis_client() -> Optional[redis.Redis]:
    """
    Get or create Redis client for caching.

    Returns:
        Redis client or None if Redis not configured
    """
    global redis_client

    if redis_client is not None:
        return redis_client

    # Check if Redis is configured
    redis_url = getattr(settings, 'REDIS_URL', None)

    if not redis_url:
        logger.warning("Redis not configured - caching disabled")
        return None

    try:
        redis_client = await redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5
        )

        # Test connection
        await redis_client.ping()
        logger.info("Redis client initialized successfully")

        return redis_client

    except Exception as e:
        logger.warning(f"Redis connection failed: {e} - caching disabled")
        return None


def generate_cache_key(request: CompanyProfileRequest) -> str:
    """
    Generate cache key for company profile request.

    Args:
        request: Company profile request

    Returns:
        MD5 hash cache key
    """
    # Normalize target (remove spaces, lowercase)
    normalized_target = request.target.replace(" ", "").lower()

    # Create key components
    key_data = {
        "target": normalized_target,
        "include_ownership": request.include_ownership,
        "include_board": request.include_board,
        "include_financials": request.include_financials
    }

    # Generate MD5 hash
    key_string = json.dumps(key_data, sort_keys=True)
    cache_key = hashlib.md5(key_string.encode()).hexdigest()

    return f"agent:company_profile:{cache_key}"


def generate_cache_key_financial(request: FinancialAnalysisRequest) -> str:
    """
    Generate cache key for financial analysis request (Week 6).
    
    Args:
        request: Financial analysis request
        
    Returns:
        MD5 hash cache key
    """
    # Normalize target (remove spaces, lowercase)
    normalized_target = request.target.replace(" ", "").lower()
    
    # Create key components
    key_data = {
        "target": normalized_target
    }
    
    # Generate MD5 hash
    key_string = json.dumps(key_data, sort_keys=True)
    cache_key = hashlib.md5(key_string.encode()).hexdigest()
    
    return f"agent:financial_analysis:{cache_key}"


def generate_cache_key_digital(request: DigitalPresenceRequest) -> str:
    """
    Generate cache key for digital presence request (Week 9).
    
    Args:
        request: Digital presence request
        
    Returns:
        MD5 hash cache key
    """
    # Normalize target (remove spaces, lowercase, strip protocol)
    normalized_target = request.target.replace(" ", "").lower()
    
    # Remove protocol for consistency
    for protocol in ['https://', 'http://', 'www.']:
        if normalized_target.startswith(protocol):
            normalized_target = normalized_target[len(protocol):]
    
    # Create key components
    key_data = {
        "target": normalized_target
    }
    
    # Generate MD5 hash
    key_string = json.dumps(key_data, sort_keys=True)
    cache_key = hashlib.md5(key_string.encode()).hexdigest()
    
    return f"agent:digital_presence:{cache_key}"


def generate_cache_key_competitor(request: CompetitorMappingRequest) -> str:
    """
    Generate cache key for competitor mapping request (Week 12).

    Args:
        request: Competitor mapping request

    Returns:
        MD5 hash cache key
    """
    # Normalize target (remove spaces, uppercase NIP/KRS prefixes)
    normalized_target = request.target.replace(" ", "").upper()

    # Create key components
    key_data = {
        "target": normalized_target,
        "max_competitors": request.max_competitors,
        "include_swot": request.include_swot,
        "include_porter": request.include_porter,
        "include_advantages": request.include_advantages
    }

    # Generate MD5 hash
    key_string = json.dumps(key_data, sort_keys=True)
    cache_key = hashlib.md5(key_string.encode()).hexdigest()

    return f"agent:competitor_mapping:{cache_key}"


def generate_cache_key_fact_checker(request: FactCheckerRequest) -> str:
    """
    Generate cache key for fact checker request (Week 15).

    Args:
        request: Fact checker request

    Returns:
        MD5 hash cache key
    """
    # Normalize target (remove spaces, lowercase)
    normalized_target = request.target.replace(" ", "").lower()

    # Create key components
    key_data = {
        "target": normalized_target,
        "claims": request.claims,
        "text": request.text_to_analyze,
        "include_citations": request.include_citations
    }

    # Generate MD5 hash
    key_string = json.dumps(key_data, sort_keys=True)
    cache_key = hashlib.md5(key_string.encode()).hexdigest()

    return f"agent:fact_checker:{cache_key}"


def generate_cache_key_insight_generator(request: InsightGeneratorRequest) -> str:
    """
    Generate cache key for insight generator request (Week 18).

    Args:
        request: Insight generator request

    Returns:
        MD5 hash cache key
    """
    # Normalize target (remove spaces, lowercase)
    normalized_target = request.target.replace(" ", "").lower()

    # Create key components
    key_data = {
        "target": normalized_target,
        "min_confidence": request.min_confidence,
        "max_insights": request.max_insights,
        "include_scenarios": request.include_scenarios,
        # Include data hashes for cache invalidation
        "has_financial": bool(request.financial_data),
        "has_market": bool(request.market_data),
        "has_competitor": bool(request.competitor_data),
        "has_digital": bool(request.digital_presence)
    }

    # Generate MD5 hash
    key_string = json.dumps(key_data, sort_keys=True)
    cache_key = hashlib.md5(key_string.encode()).hexdigest()

    return f"agent:insight_generator:{cache_key}"


def generate_citations(agent_output: FactCheckerOutput) -> List[Dict[str, Any]]:
    """
    Generate formatted citations from FactCheckerOutput (Week 15).

    Creates properly formatted citations in APA-style format for all sources.

    Args:
        agent_output: FactCheckerOutput from agent

    Returns:
        List of formatted citations
    """
    citations = []
    seen_sources = set()

    # Collect all unique sources from verifications
    for verification in agent_output.verifications:
        all_sources = verification.supporting_sources + verification.contradicting_sources

        for source in all_sources:
            # Skip duplicates
            source_key = f"{source.source_name}_{source.source_type}"
            if source_key in seen_sources:
                continue

            seen_sources.add(source_key)

            # Format citation
            citation_text = f"{source.source_name}. "

            if source.publication_date:
                year = source.publication_date.year
                citation_text += f"({year}). "
            else:
                citation_text += "(n.d.). "

            # Handle source_type (might be enum or string)
            source_type_str = source.source_type.value if hasattr(source.source_type, 'value') else source.source_type
            citation_text += f"{source_type_str.replace('_', ' ').title()}. "

            if source.source_url:
                citation_text += f"Retrieved from {source.source_url}"
            else:
                citation_text += "No URL available"

            # Handle credibility_level (might be enum or string)
            credibility_level_str = source.credibility_level.value if hasattr(source.credibility_level, 'value') else source.credibility_level

            citations.append({
                "source_name": source.source_name,
                "source_type": source_type_str,
                "source_url": source.source_url,
                "citation": citation_text,
                "retrieved_date": source.retrieved_date.strftime("%Y-%m-%d"),
                "credibility_score": source.credibility_score,
                "credibility_level": credibility_level_str
            })

    return citations


async def get_cached_response(
    cache_key: str,
    redis_client: Optional[redis.Redis]
) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached response from Redis.

    Args:
        cache_key: Cache key
        redis_client: Redis client

    Returns:
        Cached response or None
    """
    if not redis_client:
        return None

    try:
        cached_data = await redis_client.get(cache_key)

        if cached_data:
            logger.info(f"Cache hit: {cache_key}")
            return json.loads(cached_data)

        logger.debug(f"Cache miss: {cache_key}")
        return None

    except Exception as e:
        logger.warning(f"Cache retrieval error: {e}")
        return None


async def set_cached_response(
    cache_key: str,
    response_data: Dict[str, Any],
    redis_client: Optional[redis.Redis],
    ttl_seconds: int = 3600
) -> bool:
    """
    Store response in Redis cache.

    Args:
        cache_key: Cache key
        response_data: Response data to cache
        redis_client: Redis client
        ttl_seconds: Time-to-live in seconds (default: 1 hour)

    Returns:
        True if cached successfully, False otherwise
    """
    if not redis_client:
        return False

    try:
        await redis_client.setex(
            cache_key,
            ttl_seconds,
            json.dumps(response_data)
        )

        logger.info(f"Cached response: {cache_key} (TTL: {ttl_seconds}s)")
        return True

    except Exception as e:
        logger.warning(f"Cache storage error: {e}")
        return False


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get(
    "/status",
    response_model=AgentStatusResponse,
    summary="Get agents system status",
    description="Health check endpoint for the autonomous agents system"
)
async def get_agents_status():
    """
    Get current status of agents system.

    Returns:
        System status including available agents and cache status
    """
    redis_client = await get_redis_client()

    return AgentStatusResponse(
        status="operational",
        agents_available=["company_profile", "financial_analysis", "digital_presence"],
        cache_enabled=redis_client is not None,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@router.post(
    "/company-profile",
    response_model=CompanyProfileResponse,
    summary="Get company profile",
    description="Retrieve comprehensive company profile using autonomous agent",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Company profile retrieved successfully"},
        400: {"description": "Invalid request parameters"},
        404: {"description": "Company not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
        504: {"description": "Request timeout"}
    }
)
async def get_company_profile(
    request: Request,
    profile_request: CompanyProfileRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive company profile using CompanyProfileAgent.

    **Features:**
    - Multi-source data aggregation (KRS, GUS, REGON)
    - Ownership structure parsing
    - Management board extraction
    - Redis caching for performance
    - Rate limiting for stability
    - Timeout handling for reliability

    **Rate Limits:**
    - 10 requests per minute per IP address

    **Caching:**
    - Responses cached for 1 hour (3600 seconds)
    - Can be disabled with `use_cache=False`

    **Timeout:**
    - Maximum processing time: 30 seconds

    Args:
        request: FastAPI request object (for rate limiting)
        profile_request: Company profile request parameters
        current_user: Authenticated user (from JWT token)

    Returns:
        CompanyProfileResponse with company data

    Raises:
        HTTPException: 400 for invalid input, 404 if not found, 504 on timeout
    """
    start_time = datetime.utcnow()

    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 10 requests per minute."
        )

    logger.info(
        f"Company profile request from user {current_user.id}: "
        f"target={profile_request.target}"
    )

    try:
        # Initialize Redis client
        redis_client = await get_redis_client()

        # Check cache if enabled
        cached_response = None
        if profile_request.use_cache and redis_client:
            cache_key = generate_cache_key(profile_request)
            cached_response = await get_cached_response(cache_key, redis_client)

            if cached_response:
                # Return cached response
                processing_time = int(
                    (datetime.utcnow() - start_time).total_seconds() * 1000
                )

                cached_response['cached'] = True
                cached_response['processing_time_ms'] = processing_time

                logger.info(
                    f"Returning cached response for {profile_request.target} "
                    f"({processing_time}ms)"
                )

                return CompanyProfileResponse(**cached_response)

        # Execute agent with timeout
        agent = CompanyProfileAgent()

        try:
            # Set timeout to 30 seconds
            agent_result: CompanyProfileOutput = await asyncio.wait_for(
                agent.execute(target=profile_request.target),
                timeout=30.0
            )

        except asyncio.TimeoutError:
            logger.error(f"Agent timeout for {profile_request.target}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request timeout - company data retrieval took too long"
            )

        # Check if company was found
        if not agent_result.company_name:
            logger.warning(f"Company not found: {profile_request.target}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company not found: {profile_request.target}"
            )

        # Build response
        processing_time = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000
        )

        # Convert Pydantic models to dicts for response
        address_dict = None
        if agent_result.address:
            address_dict = agent_result.address.dict() if hasattr(agent_result.address, 'dict') else agent_result.address

        ownership_list = None
        if profile_request.include_ownership and agent_result.ownership_structure:
            ownership_list = [
                owner.dict() if hasattr(owner, 'dict') else owner
                for owner in agent_result.ownership_structure
            ]

        board_list = None
        if profile_request.include_board and agent_result.management_board:
            board_list = [
                member.dict() if hasattr(member, 'dict') else member
                for member in agent_result.management_board
            ]

        response_data = {
            "success": True,
            "company_name": agent_result.company_name,
            "nip": agent_result.nip_number,
            "krs": agent_result.krs_number,
            "regon": agent_result.regon_number,
            "legal_form": agent_result.legal_form,
            "registration_date": agent_result.registration_date,
            "address": address_dict,
            "pkd_main": None,  # Not in agent output, kept for API compatibility
            "industry": agent_result.industry,
            "ownership_structure": ownership_list,
            "management_board": board_list,
            "share_capital": None,  # Not in agent output, kept for API compatibility
            "employee_range": None,  # Not in agent output, kept for API compatibility
            "data_sources": agent_result.data_sources,
            "cached": False,
            "processing_time_ms": processing_time
        }

        # Cache response
        if profile_request.use_cache and redis_client:
            cache_key = generate_cache_key(profile_request)
            await set_cached_response(
                cache_key,
                response_data,
                redis_client,
                ttl_seconds=3600  # 1 hour
            )

        logger.info(
            f"Company profile retrieved: {agent_result.company_name} "
            f"({processing_time}ms)"
        )

        return CompanyProfileResponse(**response_data)

    except HTTPException:
        # Re-raise HTTP exceptions (already handled)
        raise

    except Exception as e:
        logger.error(
            f"Error retrieving company profile for {profile_request.target}: {e}",
            exc_info=True
        )

        return CompanyProfileResponse(
            success=False,
            error=f"Internal error: {str(e)}",
            cached=False,
            processing_time_ms=int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )
        )




# ============================================================================
# FINANCIAL ANALYSIS ENDPOINT (Week 6)
# ============================================================================

@router.post(
    "/financial-analysis",
    response_model=FinancialAnalysisResponse,
    summary="Get financial analysis",
    description="Comprehensive financial analysis using autonomous agent (Week 6)",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Financial analysis completed successfully"},
        400: {"description": "Invalid request parameters"},
        404: {"description": "Financial data not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
        504: {"description": "Request timeout"}
    }
)
async def get_financial_analysis(
    request: Request,
    analysis_request: FinancialAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive financial analysis using FinancialAnalysisAgent.
    
    **Features (Week 6):**
    - Multi-period financial statement analysis (3 years)
    - Liquidity, profitability, leverage, efficiency, cash flow ratios
    - Trend analysis (YoY, QoQ, seasonality detection)
    - Altman Z-Score bankruptcy prediction
    - Industry benchmarking (GUS statistics)
    - Financial health scoring (0-100)
    - Redis caching for performance
    - Rate limiting for stability
    - Timeout handling for reliability
    
    **Rate Limits:**
    - 10 requests per minute per IP address
    
    **Caching:**
    - Responses cached for 1 hour (3600 seconds)
    - Can be disabled with `use_cache=False`
    
    **Timeout:**
    - Maximum processing time: 30 seconds
    
    Args:
        request: FastAPI request object (for rate limiting)
        analysis_request: Financial analysis request parameters
        current_user: Authenticated user (from JWT token)
        
    Returns:
        FinancialAnalysisResponse with comprehensive financial analysis
        
    Raises:
        HTTPException: 400 for invalid input, 404 if not found, 504 on timeout
    """
    start_time = datetime.utcnow()
    
    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 10 requests per minute."
        )
    
    logger.info(
        f"Financial analysis request from user {current_user.id}: "
        f"target={analysis_request.target}"
    )
    
    try:
        # Initialize Redis client
        redis_client = await get_redis_client()
        
        # Check cache if enabled
        cached_response = None
        if analysis_request.use_cache and redis_client:
            cache_key = generate_cache_key_financial(analysis_request)
            cached_response = await get_cached_response(cache_key, redis_client)
            
            if cached_response:
                # Return cached response
                processing_time = int(
                    (datetime.utcnow() - start_time).total_seconds() * 1000
                )
                
                cached_response['cached'] = True
                cached_response['processing_time_ms'] = processing_time
                
                logger.info(
                    f"Returning cached response for {analysis_request.target} "
                    f"({processing_time}ms)"
                )
                
                return FinancialAnalysisResponse(**cached_response)
        
        # Execute agent with timeout
        agent = FinancialAnalysisAgent()
        
        try:
            # Run with 30-second timeout
            output: FinancialAnalysisOutput = await asyncio.wait_for(
                agent.execute(analysis_request.target),
                timeout=30.0
            )
            
        except asyncio.TimeoutError:
            logger.error(f"Financial analysis timeout for {analysis_request.target}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Financial analysis request timed out (30s limit exceeded)"
            )
        
        # Calculate processing time
        processing_time = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000
        )
        
        # Handle errors from agent
        if output.errors:
            logger.warning(
                f"Financial analysis completed with errors: {output.errors}"
            )
            
            # If no data retrieved, return 404
            if output.periods_analyzed == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Financial data not found for {analysis_request.target}"
                )
        
        # Build successful response
        response_data = {
            "success": True,
            "target": output.target,
            "company_name": output.company_name,
            "periods_analyzed": output.periods_analyzed,
            "overall_score": output.health_score.overall_score if output.health_score else None,
            "risk_level": output.health_score.risk_level if output.health_score else None,
            "altman_z_score": output.health_score.altman_z_score if output.health_score else None,
            "bankruptcy_risk": output.health_score.bankruptcy_risk if output.health_score else None,
            "liquidity_score": output.health_score.liquidity_score if output.health_score else None,
            "profitability_score": output.health_score.profitability_score if output.health_score else None,
            "leverage_score": output.health_score.leverage_score if output.health_score else None,
            "cash_flow_score": getattr(output.health_score, 'cash_flow_score', None) if output.health_score else None,
            "industry_benchmark": output.industry_benchmark.dict() if output.industry_benchmark else None,
            "strengths": output.health_score.strengths if output.health_score else [],
            "weaknesses": output.health_score.weaknesses if output.health_score else [],
            "recommendations": output.health_score.recommendations if output.health_score else [],
            "data_sources": output.data_sources,
            "confidence_score": output.confidence_score,
            "cached": False,
            "processing_time_ms": processing_time
        }
        
        # Cache response if enabled
        if analysis_request.use_cache and redis_client:
            cache_key = generate_cache_key_financial(analysis_request)
            await set_cached_response(cache_key, response_data, redis_client, ttl_seconds=3600)
        
        logger.info(
            f"Financial analysis complete for {analysis_request.target}: "
            f"score={response_data['overall_score']}, "
            f"risk={response_data['risk_level']}, "
            f"time={processing_time}ms"
        )
        
        return FinancialAnalysisResponse(**response_data)
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Financial analysis error: {e}", exc_info=True)
        
        processing_time = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000
        )
        
        return FinancialAnalysisResponse(
            success=False,
            target=analysis_request.target,
            periods_analyzed=0,
            confidence_score=0.0,
            cached=False,
            processing_time_ms=processing_time,
            error=str(e)
        )

@router.delete(
    "/cache/{cache_key}",
    summary="Clear cache entry",
    description="Remove specific cache entry (admin only)",
    status_code=status.HTTP_204_NO_CONTENT
)
async def clear_cache_entry(
    cache_key: str,
    current_user: User = Depends(get_current_user)
):
    """
    Clear specific cache entry.

    Requires admin privileges.

    Args:
        cache_key: Cache key to clear
        current_user: Authenticated user

    Raises:
        HTTPException: 403 if not admin, 404 if cache not found
    """
    # Check admin privileges
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    redis_client = await get_redis_client()

    if not redis_client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cache not configured"
        )

    try:
        result = await redis_client.delete(cache_key)

        if result == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cache key not found: {cache_key}"
            )

        logger.info(f"Cache cleared by admin: {cache_key}")

        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache clear failed: {str(e)}"
        )


# ============================================================================
# DIGITAL PRESENCE ENDPOINT (Week 9)
# ============================================================================

@router.post(
    "/digital-presence",
    response_model=DigitalPresenceResponse,
    summary="Analyze digital presence",
    description="Comprehensive website and online presence analysis using autonomous agent (Week 9)",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Digital presence analysis completed successfully"},
        400: {"description": "Invalid request parameters"},
        404: {"description": "Website not accessible"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
        504: {"description": "Request timeout"}
    }
)
async def get_digital_presence(
    request: Request,
    presence_request: DigitalPresenceRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze website and online presence using DigitalPresenceAgent.

    **Features:**
    - Website crawling and parsing (Firecrawl/Jina)
    - Tech stack detection (frameworks, CMS, hosting)
    - Enhanced SEO analysis (meta tags, keywords, structure)
    - Social media presence mapping (8 platforms)
    - Contact information extraction with validation
    - Performance metrics analysis
    - Redis caching for performance
    - Rate limiting for stability
    - Timeout handling for reliability

    **Rate Limits:**
    - 10 requests per minute per IP address

    **Caching:**
    - Responses cached for 1 hour (3600 seconds)
    - Can be disabled with `use_cache=False`

    **Timeout:**
    - Maximum processing time: 30 seconds

    Args:
        request: FastAPI request object (for rate limiting)
        presence_request: Digital presence request parameters
        current_user: Authenticated user (from JWT token)

    Returns:
        DigitalPresenceResponse with comprehensive website analysis

    Raises:
        HTTPException: 400 for invalid input, 404 if website not accessible, 504 on timeout
    """
    start_time = datetime.utcnow()

    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 10 requests per minute."
        )

    logger.info(
        f"Digital presence request from user {current_user.id}: "
        f"target={presence_request.target}"
    )

    try:
        # Initialize Redis client
        redis_client = await get_redis_client()

        # Check cache if enabled
        cached_response = None
        if presence_request.use_cache and redis_client:
            cache_key = generate_cache_key_digital(presence_request)
            cached_response = await get_cached_response(cache_key, redis_client)

            if cached_response:
                # Return cached response
                processing_time = int(
                    (datetime.utcnow() - start_time).total_seconds() * 1000
                )

                cached_response['cached'] = True
                cached_response['processing_time_ms'] = processing_time

                logger.info(
                    f"Returning cached response for {presence_request.target} "
                    f"({processing_time}ms)"
                )

                return DigitalPresenceResponse(**cached_response)

        # Execute agent with timeout
        agent = DigitalPresenceAgent()

        try:
            # Set timeout to 30 seconds
            agent_result: DigitalPresenceOutput = await asyncio.wait_for(
                agent.execute(target=presence_request.target),
                timeout=30.0
            )

        except asyncio.TimeoutError:
            logger.error(f"Agent timeout for {presence_request.target}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request timeout - website analysis took too long"
            )

        # Build response
        processing_time = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000
        )

        # Convert Pydantic models to dicts/lists for response
        tech_stack_dict = None
        if agent_result.website_analysis.tech_stack:
            tech_stack = agent_result.website_analysis.tech_stack
            tech_stack_dict = {
                "frameworks": tech_stack.frameworks,
                "cms": tech_stack.cms,
                "hosting": tech_stack.hosting,
                "analytics": tech_stack.analytics,
                "cdn": tech_stack.cdn,
                "languages": tech_stack.languages,
                "libraries": tech_stack.libraries,
                "confidence_score": tech_stack.confidence_score
            }

        # Extract social media platforms list
        social_platforms = []
        if agent_result.website_analysis.contact_info and agent_result.website_analysis.contact_info.social_media:
            social_platforms = list(agent_result.website_analysis.contact_info.social_media.keys())

        # Extract contact info
        contact_emails = []
        contact_phones = []
        if agent_result.website_analysis.contact_info:
            contact_emails = agent_result.website_analysis.contact_info.emails or []
            contact_phones = agent_result.website_analysis.contact_info.phones or []

        response_data = {
            "success": True,
            "target": agent_result.target,
            "website_url": agent_result.website_url,
            "company_name": agent_result.company_name,
            "website_status": agent_result.website_analysis.status.value if agent_result.website_analysis.status else None,
            "response_time_ms": agent_result.website_analysis.response_time_ms,
            "tech_stack": tech_stack_dict,
            "seo_score": agent_result.website_analysis.seo.seo_score if agent_result.website_analysis.seo else None,
            "seo_quality": agent_result.website_analysis.seo.seo_quality.value if agent_result.website_analysis.seo and agent_result.website_analysis.seo.seo_quality else None,
            "is_mobile_friendly": agent_result.website_analysis.seo.is_mobile_friendly if agent_result.website_analysis.seo else None,
            "page_speed_score": agent_result.website_analysis.seo.page_speed_score if agent_result.website_analysis.seo else None,
            "social_media_platforms": social_platforms,
            "contact_emails": contact_emails,
            "contact_phones": contact_phones,
            "online_presence_score": agent_result.online_presence_score,
            "strengths": agent_result.strengths,
            "weaknesses": agent_result.weaknesses,
            "recommendations": agent_result.recommendations,
            "data_sources": agent_result.data_sources,
            "confidence_score": agent_result.confidence_score,
            "cached": False,
            "processing_time_ms": processing_time
        }

        # Cache response
        if presence_request.use_cache and redis_client:
            cache_key = generate_cache_key_digital(presence_request)
            await set_cached_response(
                cache_key,
                response_data,
                redis_client,
                ttl_seconds=3600  # 1 hour
            )

        logger.info(
            f"Digital presence analyzed: {agent_result.website_url} "
            f"(score: {agent_result.online_presence_score:.1f}, {processing_time}ms)"
        )

        return DigitalPresenceResponse(**response_data)

    except HTTPException:
        # Re-raise HTTP exceptions (already handled)
        raise

    except Exception as e:
        logger.error(
            f"Error analyzing digital presence for {presence_request.target}: {e}",
            exc_info=True
        )

        return DigitalPresenceResponse(
            success=False,
            target=presence_request.target,
            error=f"Internal error: {str(e)}",
            cached=False,
            processing_time_ms=int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )
        )


# ============================================================================
# COMPETITOR MAPPING ENDPOINT (Week 12)
# ============================================================================

@router.post(
    "/competitor-mapping",
    response_model=CompetitorMappingResponse,
    summary="Analyze competitive landscape",
    description="Comprehensive competitor mapping and market positioning analysis using autonomous agent (Week 12)",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Competitor mapping completed successfully"},
        400: {"description": "Invalid request parameters"},
        404: {"description": "Company not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
        504: {"description": "Request timeout"}
    }
)
async def get_competitor_mapping(
    request: Request,
    mapping_request: CompetitorMappingRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze competitive landscape using CompetitorMappingAgent.

    **Features:**
    - Competitor discovery and identification
    - Market position analysis (leader/challenger/follower/niche)
    - AI-powered SWOT analysis (Claude integration with fallback)
    - Porter's Five Forces framework
    - Competitive advantage identification
    - Market gap detection
    - Redis caching for performance
    - Rate limiting for stability
    - Timeout handling for reliability

    **Rate Limits:**
    - 10 requests per minute per IP address

    **Caching:**
    - Responses cached for 1 hour (3600 seconds)
    - Can be disabled with `use_cache=False`

    **Timeout:**
    - Maximum processing time: 30 seconds

    Args:
        request: FastAPI request object (for rate limiting)
        mapping_request: Competitor mapping request parameters
        current_user: Authenticated user (from JWT token)

    Returns:
        CompetitorMappingResponse with comprehensive competitive analysis

    Raises:
        HTTPException: 400 for invalid input, 404 if company not found, 504 on timeout
    """
    start_time = datetime.utcnow()

    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 10 requests per minute."
        )

    logger.info(
        f"Competitor mapping request from user {current_user.id}: "
        f"target={mapping_request.target}"
    )

    try:
        # Initialize Redis client
        redis_client = await get_redis_client()

        # Check cache if enabled
        cached_response = None
        if mapping_request.use_cache and redis_client:
            cache_key = generate_cache_key_competitor(mapping_request)
            cached_response = await get_cached_response(cache_key, redis_client)

            if cached_response:
                # Return cached response
                processing_time = int(
                    (datetime.utcnow() - start_time).total_seconds() * 1000
                )

                cached_response['cached'] = True
                cached_response['processing_time_ms'] = processing_time

                logger.info(
                    f"Returning cached response for {mapping_request.target} "
                    f"({processing_time}ms)"
                )

                return CompetitorMappingResponse(**cached_response)

        # Execute agent with timeout
        agent = CompetitorMappingAgent()

        # Prepare context for agent
        context = {
            "max_competitors": mapping_request.max_competitors,
            "include_swot": mapping_request.include_swot,
            "include_porter": mapping_request.include_porter,
            "include_advantages": mapping_request.include_advantages
        }

        try:
            # Set timeout to 30 seconds
            agent_result: CompetitorMappingOutput = await asyncio.wait_for(
                agent.execute(
                    query=mapping_request.target,
                    context=context
                ),
                timeout=30.0
            )

        except asyncio.TimeoutError:
            logger.error(f"Agent timeout for {mapping_request.target}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request timeout - competitive analysis took too long"
            )

        # Build response
        processing_time = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000
        )

        # Convert Pydantic models to dicts for response
        direct_competitors = []
        indirect_competitors = []

        for competitor in agent_result.competitors:
            competitor_dict = {
                "company_name": competitor.company_name,
                "krs_number": competitor.krs_number,
                "nip_number": competitor.nip_number,
                "competitor_type": competitor.competitor_type,
                "similarity_score": competitor.similarity_score,
                "estimated_market_share": competitor.estimated_market_share,
                "estimated_revenue": competitor.estimated_revenue,
                "employee_count": competitor.employee_count,
                "key_products": competitor.key_products,
                "key_markets": competitor.key_markets,
                "competitive_advantages": competitor.competitive_advantages
            }

            if competitor.competitor_type == "direct":
                direct_competitors.append(competitor_dict)
            else:
                indirect_competitors.append(competitor_dict)

        # Convert SWOT analysis if present
        swot_dict = None
        if mapping_request.include_swot and agent_result.swot_analysis:
            swot = agent_result.swot_analysis
            swot_dict = {
                "strengths": [
                    {"description": item.description, "impact_level": item.impact_level}
                    for item in swot.strengths
                ],
                "weaknesses": [
                    {"description": item.description, "impact_level": item.impact_level}
                    for item in swot.weaknesses
                ],
                "opportunities": [
                    {"description": item.description, "impact_level": item.impact_level}
                    for item in swot.opportunities
                ],
                "threats": [
                    {"description": item.description, "impact_level": item.impact_level}
                    for item in swot.threats
                ],
                "overall_strategic_position": swot.overall_strategic_position,
                "total_strengths": swot.total_strengths,
                "total_weaknesses": swot.total_weaknesses,
                "total_opportunities": swot.total_opportunities,
                "total_threats": swot.total_threats
            }

        # Convert Porter's Five Forces if present
        porter_dict = None
        if mapping_request.include_porter and agent_result.porter_analysis:
            porter = agent_result.porter_analysis
            porter_dict = {
                "threat_of_new_entrants": {
                    "strength": porter.threat_of_new_entrants.strength,
                    "description": porter.threat_of_new_entrants.description,
                    "key_factors": porter.threat_of_new_entrants.key_factors
                },
                "bargaining_power_of_suppliers": {
                    "strength": porter.bargaining_power_of_suppliers.strength,
                    "description": porter.bargaining_power_of_suppliers.description,
                    "key_factors": porter.bargaining_power_of_suppliers.key_factors
                },
                "bargaining_power_of_buyers": {
                    "strength": porter.bargaining_power_of_buyers.strength,
                    "description": porter.bargaining_power_of_buyers.description,
                    "key_factors": porter.bargaining_power_of_buyers.key_factors
                },
                "threat_of_substitutes": {
                    "strength": porter.threat_of_substitutes.strength,
                    "description": porter.threat_of_substitutes.description,
                    "key_factors": porter.threat_of_substitutes.key_factors
                },
                "competitive_rivalry": {
                    "strength": porter.competitive_rivalry.strength,
                    "description": porter.competitive_rivalry.description,
                    "key_factors": porter.competitive_rivalry.key_factors
                },
                "industry_attractiveness": porter.industry_attractiveness,
                "overall_profitability_outlook": porter.overall_profitability_outlook,
                "strategic_recommendations": porter.strategic_recommendations
            }

        # Convert competitive advantages if present
        advantages_list = []
        if mapping_request.include_advantages and agent_result.competitive_advantages:
            for advantage in agent_result.competitive_advantages:
                advantages_list.append({
                    "advantage_type": advantage.advantage_type,
                    "strength": advantage.strength,
                    "description": advantage.description,
                    "sustainability": advantage.sustainability,
                    "supporting_evidence": advantage.supporting_evidence
                })

        # Convert competitive insights
        insights_list = []
        if agent_result.competitive_insights:
            for insight in agent_result.competitive_insights:
                insights_list.append({
                    "type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "priority": insight.priority,
                    "recommended_actions": insight.recommended_actions
                })

        response_data = {
            "success": True,
            "target_company": agent_result.target_company_name,
            "market_position": agent_result.market_position.position if agent_result.market_position else None,
            "market_share_percentage": agent_result.market_position.market_share_percentage if agent_result.market_position else None,
            "rank_in_industry": agent_result.market_position.rank_in_industry if agent_result.market_position else None,
            "total_competitors": len(agent_result.competitors),
            "direct_competitors": direct_competitors,
            "indirect_competitors": indirect_competitors,
            "swot_analysis": swot_dict,
            "porter_analysis": porter_dict,
            "competitive_advantages": advantages_list,
            "competitive_insights": insights_list,
            "market_gaps": agent_result.market_gaps_identified,
            "strategic_recommendations": agent_result.strategic_recommendations,
            "data_sources": agent_result.data_sources,
            "confidence_score": agent_result.confidence_score,
            "cached": False,
            "processing_time_ms": processing_time
        }

        # Cache response
        if mapping_request.use_cache and redis_client:
            cache_key = generate_cache_key_competitor(mapping_request)
            await set_cached_response(
                cache_key,
                response_data,
                redis_client,
                ttl_seconds=3600  # 1 hour
            )

        logger.info(
            f"Competitor mapping completed: {agent_result.target_company_name} "
            f"(position: {agent_result.market_position.position if agent_result.market_position else 'unknown'}, "
            f"{len(agent_result.competitors)} competitors, {processing_time}ms)"
        )

        return CompetitorMappingResponse(**response_data)

    except HTTPException:
        # Re-raise HTTP exceptions (already handled)
        raise

    except Exception as e:
        logger.error(
            f"Error analyzing competitors for {mapping_request.target}: {e}",
            exc_info=True
        )

        return CompetitorMappingResponse(
            success=False,
            target_company=mapping_request.target,
            total_competitors=0,
            confidence_score=0.0,
            error=f"Internal error: {str(e)}",
            cached=False,
            processing_time_ms=int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )
        )


# ============================================================================
# WEEK 15: FACT CHECKER AGENT ENDPOINT
# ============================================================================

@router.post(
    "/fact-checker",
    response_model=FactCheckerResponse,
    summary="Verify claims with fact checker",
    description="Verify claims using multi-source fact checker agent with citation tracking",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Fact checking completed successfully"},
        400: {"description": "Invalid request parameters"},
        404: {"description": "Target not found"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
        504: {"description": "Request timeout"}
    }
)
async def check_facts(
    request: Request,
    fact_check_request: FactCheckerRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Verify claims using FactCheckerAgent (Week 15).

    **Features:**
    - Multi-source claim verification (KRS, GUS, websites, news)
    - Source credibility assessment
    - Contradiction detection
    - Citation generation
    - Cross-reference validation (Week 14)
    - Temporal consistency checking (Week 14)
    - Enhanced confidence scoring (Week 14)
    - Redis caching for performance
    - Rate limiting for stability
    - Timeout handling for reliability

    **Rate Limits:**
    - 10 requests per minute per IP address

    **Caching:**
    - Responses cached for 1 hour (3600 seconds)
    - Can be disabled with `use_cache=False`

    **Timeout:**
    - Maximum processing time: 30 seconds

    **Week 15 Enhancements:**
    - Citation tracking and formatting
    - APA-style citation generation
    - Source URL preservation

    Args:
        request: FastAPI request object (for rate limiting)
        fact_check_request: Fact checker request parameters
        current_user: Authenticated user (from JWT token)

    Returns:
        FactCheckerResponse with verification results and citations

    Raises:
        HTTPException: 400 for invalid input, 404 if not found, 504 on timeout
    """
    start_time = datetime.utcnow()

    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 10 requests per minute."
        )

    logger.info(
        f"Fact check request from user {current_user.id}: "
        f"target={fact_check_request.target}, "
        f"claims={len(fact_check_request.claims or [])}"
    )

    try:
        # Initialize Redis client
        redis_client = await get_redis_client()

        # Check cache if enabled
        cached_response = None
        if fact_check_request.use_cache and redis_client:
            cache_key = generate_cache_key_fact_checker(fact_check_request)
            cached_response = await get_cached_response(cache_key, redis_client)

            if cached_response:
                # Return cached response
                processing_time = int(
                    (datetime.utcnow() - start_time).total_seconds() * 1000
                )

                cached_response['cached'] = True
                cached_response['processing_time_ms'] = processing_time

                logger.info(
                    f"Returning cached fact check response for {fact_check_request.target} "
                    f"({processing_time}ms)"
                )

                return FactCheckerResponse(**cached_response)

        # Execute agent with timeout
        agent = FactCheckerAgent()

        try:
            # Set timeout to 30 seconds
            context = {
                "claims": fact_check_request.claims or []
            }

            result: FactCheckerOutput = await asyncio.wait_for(
                agent.execute(
                    query=fact_check_request.target,
                    context=context
                ),
                timeout=30.0
            )

        except asyncio.TimeoutError:
            logger.error(f"Fact check timeout for {fact_check_request.target}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request timeout - fact checking took too long"
            )

        # Calculate processing time
        processing_time = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000
        )

        # Generate citations (Week 15 feature)
        citations = []
        if fact_check_request.include_citations:
            citations = generate_citations(result)

        # Convert verifications to dicts
        verifications_data = []
        for verification in result.verifications:
            ver_dict = {
                "claim_text": verification.claim_text,
                "claim_type": verification.claim_type.value,
                "verification_status": verification.verification_status.value,
                "confidence_score": verification.confidence_score,
                "supporting_sources": [s.source_name for s in verification.supporting_sources],
                "contradicting_sources": [s.source_name for s in verification.contradicting_sources],
                "total_sources_checked": verification.total_sources_checked,
                "reliability_assessment": verification.reliability_assessment,
                "recommended_action": verification.recommended_action,
                "discrepancies": verification.discrepancies,
                "notes": verification.notes
            }
            verifications_data.append(ver_dict)

        # Build response
        response_data = {
            "success": True,
            "target": result.target,
            "total_claims_checked": result.total_claims_checked,
            "verified_claims_count": result.verified_claims_count,
            "contradicted_claims_count": result.contradicted_claims_count,
            "unverified_claims_count": result.unverified_claims_count,
            "verifications": verifications_data,
            "data_sources": result.data_sources,
            "primary_sources_used": result.primary_sources_used,
            "average_source_credibility": result.average_source_credibility,
            "citations": citations if fact_check_request.include_citations else None,
            "overall_confidence_score": result.overall_confidence_score,
            "data_freshness_score": result.data_freshness_score,
            "critical_issues": result.critical_issues,
            "warnings": result.warnings,
            "errors": result.errors,
            "cached": False,
            "processing_time_ms": processing_time
        }

        # Cache response
        if fact_check_request.use_cache and redis_client:
            cache_key = generate_cache_key_fact_checker(fact_check_request)
            await set_cached_response(cache_key, response_data, redis_client, ttl_seconds=3600)

        logger.info(
            f"Fact check completed for {fact_check_request.target}: "
            f"{result.verified_claims_count}/{result.total_claims_checked} verified, "
            f"confidence {result.overall_confidence_score:.1f}%, "
            f"{processing_time}ms"
        )

        return FactCheckerResponse(**response_data)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(
            f"Fact check failed for {fact_check_request.target}: {str(e)}",
            exc_info=True
        )

        return FactCheckerResponse(
            success=False,
            target=fact_check_request.target,
            total_claims_checked=0,
            verified_claims_count=0,
            contradicted_claims_count=0,
            unverified_claims_count=0,
            overall_confidence_score=0.0,
            error=f"Internal error: {str(e)}",
            cached=False,
            processing_time_ms=int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )
        )


# ============================================================================
# WEEK 18: INSIGHT GENERATOR AGENT ENDPOINT
# ============================================================================

@router.post(
    "/insight-generator",
    response_model=InsightGeneratorResponse,
    summary="Generate insights from company data",
    description="Generate patterns, predictions, risks, and opportunities using AI-powered insight generator",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Insights generated successfully"},
        400: {"description": "Invalid request parameters"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
        504: {"description": "Request timeout"}
    }
)
async def generate_insights(
    request: Request,
    insight_request: InsightGeneratorRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate insights using InsightGeneratorAgent (Week 18).

    **Features:**
    - Pattern detection in time-series data
    - Trend analysis and predictions
    - Risk identification and assessment
    - Opportunity detection
    - Anomaly detection (Week 17)
    - Correlation analysis (Week 17)
    - Scenario analysis (best/worst/likely) (Week 17)
    - Advanced forecasting with exponential smoothing (Week 17)
    - Natural language insights with Claude AI
    - Redis caching for performance
    - Rate limiting for stability
    - Timeout handling for reliability

    **Rate Limits:**
    - 10 requests per minute per IP address

    **Caching:**
    - Responses cached for 1 hour (3600 seconds)
    - Can be disabled with `use_cache=False`

    **Timeout:**
    - Maximum processing time: 30 seconds

    **Week 18 Features:**
    - Insight prioritization based on relevance and actionability
    - Multi-dimensional analysis (financial, market, competitor, digital)
    - Confidence scoring and data quality assessment

    Args:
        request: FastAPI request object (for rate limiting)
        insight_request: Insight generator request parameters
        current_user: Authenticated user (from JWT token)

    Returns:
        InsightGeneratorResponse with insights, patterns, predictions, risks, opportunities

    Raises:
        HTTPException: 400 for invalid input, 504 on timeout
    """
    start_time = datetime.utcnow()

    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 10 requests per minute."
        )

    logger.info(
        f"Insight generation request from user {current_user.id}: "
        f"target={insight_request.target}"
    )

    try:
        # Initialize Redis client
        redis_client = await get_redis_client()

        # Check cache if enabled
        cached_response = None
        if insight_request.use_cache and redis_client:
            cache_key = generate_cache_key_insight_generator(insight_request)
            cached_response = await get_cached_response(cache_key, redis_client)

            if cached_response:
                # Return cached response
                processing_time = int(
                    (datetime.utcnow() - start_time).total_seconds() * 1000
                )

                cached_response['cached'] = True
                cached_response['processing_time_ms'] = processing_time

                logger.info(
                    f"Returning cached insight response for {insight_request.target} "
                    f"({processing_time}ms)"
                )

                return InsightGeneratorResponse(**cached_response)

        # Execute agent with timeout
        agent = InsightGeneratorAgent()

        try:
            # Build context from request
            context = {}

            if insight_request.financial_data:
                context["financial_data"] = insight_request.financial_data

            if insight_request.market_data:
                context["market_data"] = insight_request.market_data

            if insight_request.competitor_data:
                context["competitor_data"] = insight_request.competitor_data

            if insight_request.digital_presence:
                context["digital_presence"] = insight_request.digital_presence

            # Set timeout to 30 seconds
            result: InsightGeneratorOutput = await asyncio.wait_for(
                agent.execute(
                    query=insight_request.target,
                    context=context
                ),
                timeout=30.0
            )

        except asyncio.TimeoutError:
            logger.error(f"Insight generation timeout for {insight_request.target}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request timeout - insight generation took too long"
            )

        # Calculate processing time
        processing_time = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000
        )

        # Convert insights to dicts with prioritization (Week 18)
        insights_data = []
        for insight in result.insights:
            insight_dict = {
                "insight_id": insight.insight_id,
                "insight_type": insight.insight_type.value,
                "insight_text": insight.insight_text,
                "priority": insight.priority,
                "relevance_score": insight.relevance_score,
                "is_actionable": insight.is_actionable,
                "recommended_actions": insight.recommended_actions,
                "supporting_evidence": insight.supporting_evidence,
                "related_patterns": insight.related_patterns,
                "related_predictions": insight.related_predictions
            }
            insights_data.append(insight_dict)

        # Prioritize insights based on relevance and actionability (Week 18)
        insights_data.sort(
            key=lambda x: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(x["priority"], 0),
                x["relevance_score"],
                1 if x["is_actionable"] else 0
            ),
            reverse=True
        )

        # Limit to max_insights (Week 18)
        if len(insights_data) > insight_request.max_insights:
            insights_data = insights_data[:insight_request.max_insights]

        # Filter insights by minimum confidence (Week 18)
        insights_data = [
            i for i in insights_data
            if i["relevance_score"] >= insight_request.min_confidence
        ]

        # Convert patterns to dicts
        patterns_data = []
        for pattern in result.patterns_detected:
            pattern_dict = {
                "pattern_id": pattern.pattern_id,
                "pattern_type": pattern.pattern_type.value,
                "pattern_description": pattern.pattern_description,
                "confidence_score": pattern.confidence_score,
                "strength": pattern.strength,
                "data_points": pattern.data_points,
                "time_period": pattern.time_period,
                "volatility_score": pattern.volatility_score,
                "affected_metrics": pattern.affected_metrics,
                "contributing_factors": pattern.contributing_factors
            }
            patterns_data.append(pattern_dict)

        # Convert predictions to dicts
        predictions_data = []
        for prediction in result.predictions:
            prediction_dict = {
                "prediction_id": prediction.prediction_id,
                "prediction_text": prediction.prediction_text,
                "predicted_value": prediction.predicted_value,
                "prediction_confidence": prediction.prediction_confidence.value,
                "confidence_score": prediction.confidence_score,
                "time_horizon": prediction.time_horizon,
                "supporting_factors": prediction.supporting_factors,
                "risk_factors": prediction.risk_factors,
                "validation_metrics": prediction.validation_metrics
            }
            predictions_data.append(prediction_dict)

        # Convert risks to dicts
        risks_data = []
        for risk in result.risks_identified:
            risk_dict = {
                "risk_id": risk.risk_id,
                "risk_type": risk.risk_type.value,
                "risk_description": risk.risk_description,
                "risk_level": risk.risk_level.value,
                "severity_score": risk.severity_score,
                "probability": risk.probability,
                "potential_impact": risk.potential_impact,
                "mitigation_strategies": risk.mitigation_strategies,
                "early_warning_indicators": risk.early_warning_indicators,
                "related_patterns": risk.related_patterns
            }
            risks_data.append(risk_dict)

        # Convert opportunities to dicts
        opportunities_data = []
        for opportunity in result.opportunities:
            opportunity_dict = {
                "opportunity_id": opportunity.opportunity_id,
                "opportunity_type": opportunity.opportunity_type.value,
                "opportunity_description": opportunity.opportunity_description,
                "potential_impact": opportunity.potential_impact,
                "feasibility_score": opportunity.feasibility_score,
                "time_to_realize": opportunity.time_to_realize,
                "required_resources": opportunity.required_resources,
                "success_indicators": opportunity.success_indicators,
                "risks_to_consider": opportunity.risks_to_consider,
                "related_patterns": opportunity.related_patterns
            }
            opportunities_data.append(opportunity_dict)

        # Build response
        response_data = {
            "success": True,
            "target": insight_request.target,
            "total_insights": len(insights_data),
            "insights": insights_data,
            "total_patterns": result.total_patterns,
            "patterns_detected": patterns_data,
            "total_predictions": result.total_predictions,
            "predictions": predictions_data,
            "total_risks": result.total_risks,
            "risks_identified": risks_data,
            "total_opportunities": result.total_opportunities,
            "opportunities": opportunities_data,
            "overall_confidence_score": result.overall_confidence_score,
            "data_quality_score": result.data_quality_score,
            "analysis_depth": result.analysis_depth,
            "data_points_analyzed": result.data_points_analyzed,
            "warnings": result.warnings,
            "errors": result.errors,
            "cached": False,
            "processing_time_ms": processing_time
        }

        # Cache response (1 hour TTL for Week 18)
        if insight_request.use_cache and redis_client:
            cache_key = generate_cache_key_insight_generator(insight_request)
            await set_cached_response(cache_key, response_data, redis_client, ttl_seconds=3600)

        logger.info(
            f"Insight generation completed for {insight_request.target}: "
            f"{len(insights_data)} insights, {result.total_patterns} patterns, "
            f"{result.total_predictions} predictions, confidence {result.overall_confidence_score:.1f}%, "
            f"{processing_time}ms"
        )

        return InsightGeneratorResponse(**response_data)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(
            f"Insight generation failed for {insight_request.target}: {str(e)}",
            exc_info=True
        )

        return InsightGeneratorResponse(
            success=False,
            target=insight_request.target,
            total_insights=0,
            total_patterns=0,
            total_predictions=0,
            total_risks=0,
            total_opportunities=0,
            overall_confidence_score=0.0,
            data_points_analyzed=0,
            error=f"Internal error: {str(e)}",
            cached=False,
            processing_time_ms=int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )
        )
