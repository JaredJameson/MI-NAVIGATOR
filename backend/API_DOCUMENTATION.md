# MI-Navigator API Documentation

**Version**: 1.0.0
**Status**: Production Ready
**Base URL**: `http://localhost:8000/api/v1`
**Documentation**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Agent Endpoints](#agent-endpoints)
4. [Rate Limiting](#rate-limiting)
5. [Caching](#caching)
6. [Error Handling](#error-handling)
7. [Examples](#examples)
8. [Performance](#performance)

---

## 🔍 Overview

MI-Navigator is an AI-powered market intelligence platform featuring 6 autonomous agents that provide comprehensive business analysis.

### Available Agents

| Agent | Endpoint | Purpose |
|-------|----------|---------|
| Company Profile | `/agents/company-profile` | Multi-source company data aggregation |
| Financial Analysis | `/agents/financial-analysis` | Advanced financial metrics and trends |
| Digital Presence | `/agents/digital-presence` | Website and online presence assessment |
| Competitor Mapping | `/agents/competitor-mapping` | Competitive intelligence and SWOT |
| Fact Checker | `/agents/fact-checker` | Multi-source verification |
| Insight Generator | `/agents/insight-generator` | AI-powered insights and predictions |

### Key Features

- ✅ **Multi-Agent Orchestration**: Combine multiple agents for comprehensive analysis
- ✅ **Intelligent Caching**: Redis-based caching with 1-hour TTL
- ✅ **Rate Limiting**: 10 requests/min per IP
- ✅ **JWT Authentication**: Secure token-based authentication
- ✅ **Real-time Chat**: WebSocket support for interactive queries
- ✅ **Production Ready**: 236 tests passing, all agents operational

---

## 🔐 Authentication

All API endpoints (except `/auth/*` and `/health`) require JWT authentication.

### 1. Register a New User

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

### 2. Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

### 3. Using the Access Token

Include the access token in the `Authorization` header:

```http
GET /api/v1/agents/company-profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4. Refresh Token

When the access token expires (1 hour), use the refresh token:

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 🤖 Agent Endpoints

### 1. Company Profile Agent

**Endpoint**: `POST /api/v1/agents/company-profile`

**Purpose**: Retrieve comprehensive company information from KRS, GUS, and REGON registries.

**Request**:
```json
{
  "nip": "1234567890",
  "krs": null,
  "regon": null,
  "company_name": "Example Company Ltd."
}
```

**Response**:
```json
{
  "company_name": "Example Company Sp. z o.o.",
  "nip": "1234567890",
  "krs": "0000123456",
  "regon": "123456789",
  "legal_form": "Spółka z ograniczoną odpowiedzialnością",
  "pkd_code": "62.01.Z",
  "pkd_description": "Computer programming activities",
  "address": {
    "street": "ul. Marszałkowska 1",
    "city": "Warszawa",
    "postal_code": "00-001",
    "country": "Polska"
  },
  "ownership_structure": {
    "shareholders": [
      {
        "name": "John Doe",
        "shares_percentage": 100.0
      }
    ]
  },
  "board_members": [
    {
      "name": "Jane Smith",
      "position": "Prezes Zarządu"
    }
  ],
  "financial_summary": {
    "share_capital": "5000.00 PLN"
  },
  "registration_date": "2020-01-15",
  "status": "ACTIVE",
  "confidence_score": 95.0,
  "data_sources": ["KRS", "GUS", "REGON"],
  "metadata": {
    "cached": false,
    "processing_time_ms": 234
  }
}
```

**Parameters**:
- `nip` (string, optional): 10-digit tax identification number
- `krs` (string, optional): Court registration number
- `regon` (string, optional): National business registry number
- `company_name` (string, optional): Company name for fuzzy matching

**Notes**:
- At least one identifier (NIP, KRS, REGON, or company name) must be provided
- NIP validation includes checksum verification
- Cached for 1 hour for improved performance

---

### 2. Financial Analysis Agent

**Endpoint**: `POST /api/v1/agents/financial-analysis`

**Purpose**: Analyze financial statements with ratio calculations, trend analysis, and health scoring.

**Request**:
```json
{
  "nip": "1234567890",
  "analysis_type": "comprehensive"
}
```

**Response**:
```json
{
  "company_name": "Example Company Sp. z o.o.",
  "nip": "1234567890",
  "financial_statements": [
    {
      "period": "2023",
      "period_type": "annual",
      "total_assets": 5000000.0,
      "current_assets": 2000000.0,
      "revenue": 10000000.0,
      "net_profit": 500000.0,
      "operating_cash_flow": 600000.0
    }
  ],
  "liquidity_ratios": {
    "current_ratio": 2.5,
    "quick_ratio": 1.8,
    "current_ratio_status": "healthy"
  },
  "profitability_ratios": {
    "gross_margin": 45.0,
    "net_margin": 5.0,
    "roe": 12.5
  },
  "trend_analysis": [
    {
      "metric": "revenue",
      "avg_growth_rate": 15.2,
      "qoq_growth_rate": 3.5,
      "trend": "increasing"
    }
  ],
  "industry_benchmark": {
    "industry": "IT Services",
    "avg_net_margin": 8.0,
    "company_vs_industry": "Below Average"
  },
  "health_score": 75.5,
  "risk_level": "low",
  "confidence_score": 88.0
}
```

**Features**:
- YoY and QoQ trend analysis
- Industry benchmarking
- Z-score bankruptcy prediction
- 15+ financial ratios across 4 categories

---

### 3. Digital Presence Agent

**Endpoint**: `POST /api/v1/agents/digital-presence`

**Purpose**: Analyze website and online presence including tech stack, SEO, and social media.

**Request**:
```json
{
  "website_url": "https://example.com"
}
```

**Response**:
```json
{
  "website_url": "https://example.com",
  "tech_stack": {
    "frameworks": ["React", "Next.js"],
    "cms": "None",
    "hosting": "Vercel",
    "analytics": ["Google Analytics"]
  },
  "seo_analysis": {
    "title": "Example Company - IT Services",
    "meta_description": "Professional IT services...",
    "seo_score": 85.0,
    "mobile_friendly": true,
    "page_speed_score": 92.0
  },
  "social_media": {
    "linkedin": "https://linkedin.com/company/example",
    "twitter": "https://twitter.com/example",
    "facebook": null
  },
  "contact_info": {
    "email": "contact@example.com",
    "phone": "+48 22 123 4567"
  },
  "performance_score": 88.0,
  "confidence_score": 90.0
}
```

---

### 4. Competitor Mapping Agent

**Endpoint**: `POST /api/v1/agents/competitor-mapping`

**Purpose**: Identify competitors and analyze competitive landscape with SWOT and Porter's Five Forces.

**Request**:
```json
{
  "nip": "1234567890",
  "max_competitors": 5
}
```

**Response**:
```json
{
  "company_name": "Example Company Sp. z o.o.",
  "competitors": [
    {
      "company_name": "Competitor A Ltd.",
      "nip": "9876543210",
      "similarity_score": 0.85,
      "market_share_estimate": 15.0,
      "strengths": ["Strong brand", "Large customer base"]
    }
  ],
  "swot_analysis": {
    "strengths": [
      {
        "category": "product",
        "description": "Innovative product portfolio",
        "impact": "high"
      }
    ],
    "weaknesses": [
      {
        "category": "market",
        "description": "Limited geographic coverage",
        "impact": "medium"
      }
    ],
    "opportunities": [
      {
        "category": "growth",
        "description": "Expanding to new markets",
        "impact": "high"
      }
    ],
    "threats": [
      {
        "category": "competition",
        "description": "New market entrants",
        "impact": "medium"
      }
    ]
  },
  "porter_analysis": {
    "competitive_rivalry": {
      "strength": "high",
      "score": 8.0,
      "factors": ["Many competitors", "Price competition"]
    },
    "threat_of_new_entrants": {
      "strength": "medium",
      "score": 5.0
    },
    "industry_attractiveness": 6.5
  },
  "competitive_advantages": [
    {
      "strategy": "differentiation",
      "description": "Unique technology platform",
      "sustainability": "high"
    }
  ],
  "confidence_score": 82.0
}
```

---

### 5. Fact Checker Agent

**Endpoint**: `POST /api/v1/agents/fact-checker`

**Purpose**: Verify claims using multiple sources with credibility scoring.

**Request**:
```json
{
  "claims": [
    "Company X has 500 employees",
    "Company X revenue grew 20% in 2023"
  ],
  "nip": "1234567890"
}
```

**Response**:
```json
{
  "verified_claims": [
    {
      "claim": "Company X has 500 employees",
      "claim_type": "operational",
      "verification_status": "verified",
      "confidence_score": 0.95,
      "sources": [
        {
          "source_name": "KRS Registry",
          "credibility_score": 0.98,
          "evidence": "Company employment data: 500"
        }
      ],
      "contradictions": []
    },
    {
      "claim": "Company X revenue grew 20% in 2023",
      "claim_type": "financial",
      "verification_status": "partially_verified",
      "confidence_score": 0.75,
      "sources": [
        {
          "source_name": "Financial Reports",
          "credibility_score": 0.90,
          "evidence": "Revenue growth: 18.5%"
        }
      ],
      "contradictions": [
        "Actual growth rate 18.5%, not 20%"
      ]
    }
  ],
  "overall_credibility": 0.85
}
```

---

### 6. Insight Generator Agent

**Endpoint**: `POST /api/v1/agents/insight-generator`

**Purpose**: Generate AI-powered insights with pattern recognition and predictions.

**Request**:
```json
{
  "nip": "1234567890",
  "analysis_focus": "growth_opportunities"
}
```

**Response**:
```json
{
  "insights": [
    {
      "type": "opportunity",
      "title": "Market Expansion Potential",
      "description": "Analysis shows strong potential for geographic expansion to southern regions",
      "confidence_score": 0.88,
      "impact_score": 0.85,
      "priority": "high",
      "actionable_recommendations": [
        "Conduct market research in target regions",
        "Develop regional partnerships",
        "Allocate budget for expansion"
      ]
    },
    {
      "type": "trend",
      "title": "Revenue Growth Pattern",
      "description": "Consistent quarterly growth indicating sustainable business model",
      "pattern_type": "growth",
      "confidence_score": 0.92
    },
    {
      "type": "risk",
      "title": "Competitive Pressure Increasing",
      "description": "New entrants in the market may impact market share",
      "confidence_score": 0.75,
      "mitigation_strategies": [
        "Strengthen differentiation",
        "Enhance customer retention programs"
      ]
    }
  ],
  "patterns_detected": [
    {
      "pattern_type": "seasonal",
      "metric": "revenue",
      "description": "Q4 typically shows 20% higher revenue"
    }
  ],
  "predictions": [
    {
      "metric": "revenue",
      "prediction_horizon": "next_quarter",
      "predicted_value": 12500000.0,
      "confidence_score": 0.80
    }
  ]
}
```

---

## ⚡ Rate Limiting

All API endpoints are rate-limited to ensure fair usage and prevent abuse.

### Limits

- **Standard Endpoints**: 10 requests per minute per IP
- **Authentication Endpoints**: 5 requests per minute per IP
- **Agent Endpoints**: 10 requests per minute per IP

### Rate Limit Headers

Responses include rate limit information in headers:

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded Response

```json
{
  "detail": "Rate limit exceeded. Please try again in 45 seconds.",
  "status_code": 429,
  "retry_after": 45
}
```

---

## 💾 Caching

The API uses intelligent caching to improve performance.

### Cache Configuration

- **Cache Backend**: Redis
- **Default TTL**: 1 hour (3600 seconds)
- **Cache Hit Rate**: 90%+
- **Cache Key**: Based on endpoint, parameters, and user ID

### Cache Headers

Responses indicate cache status:

```json
{
  "metadata": {
    "cached": true,
    "processing_time_ms": 4.5,
    "cache_age_seconds": 1200
  }
}
```

### Cache Invalidation

Caches are automatically invalidated when:
- Data is updated via API
- TTL expires
- Manual cache clear (admin only)

---

## ❌ Error Handling

The API uses standard HTTP status codes and provides detailed error messages.

### Common Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid input parameters |
| 401 | Unauthorized | Missing or invalid authentication token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Response Format

```json
{
  "detail": "Invalid NIP format. Expected 10 digits.",
  "status_code": 400,
  "error_type": "ValidationError",
  "field": "nip",
  "timestamp": "2026-01-26T10:30:00Z"
}
```

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "nip"],
      "msg": "ensure this value has at least 10 characters",
      "type": "value_error.any_str.min_length"
    }
  ],
  "status_code": 422
}
```

---

## 📝 Examples

### Complete Workflow Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. Register and login
auth_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "user@example.com",
    "password": "SecurePassword123!"
})
token = auth_response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# 2. Get company profile
profile = requests.post(
    f"{BASE_URL}/agents/company-profile",
    headers=headers,
    json={"nip": "1234567890"}
).json()

print(f"Company: {profile['company_name']}")

# 3. Analyze finances
financial = requests.post(
    f"{BASE_URL}/agents/financial-analysis",
    headers=headers,
    json={"nip": "1234567890"}
).json()

print(f"Health Score: {financial['health_score']}")

# 4. Check digital presence
digital = requests.post(
    f"{BASE_URL}/agents/digital-presence",
    headers=headers,
    json={"website_url": profile.get('website')}
).json()

print(f"SEO Score: {digital['seo_analysis']['seo_score']}")

# 5. Identify competitors
competitors = requests.post(
    f"{BASE_URL}/agents/competitor-mapping",
    headers=headers,
    json={"nip": "1234567890", "max_competitors": 5}
).json()

print(f"Found {len(competitors['competitors'])} competitors")

# 6. Generate insights
insights = requests.post(
    f"{BASE_URL}/agents/insight-generator",
    headers=headers,
    json={"nip": "1234567890"}
).json()

print(f"Generated {len(insights['insights'])} insights")
```

### cURL Examples

```bash
# Get company profile
curl -X POST "http://localhost:8000/api/v1/agents/company-profile" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nip": "1234567890"}'

# Financial analysis
curl -X POST "http://localhost:8000/api/v1/agents/financial-analysis" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nip": "1234567890", "analysis_type": "comprehensive"}'
```

---

## ⚙️ Performance

### Response Times

| Endpoint | Cached | Uncached |
|----------|--------|----------|
| Company Profile | <5ms | <230ms |
| Financial Analysis | <5ms | <250ms |
| Digital Presence | <5ms | <300ms |
| Competitor Mapping | <5ms | <280ms |
| Fact Checker | <5ms | <200ms |
| Insight Generator | <5ms | <240ms |

### Throughput

- **Peak Throughput**: 40+ requests/second
- **Average Response Time**: <5ms (cached), <250ms (uncached)
- **Cache Hit Rate**: 90%+
- **Uptime**: 99.9% target

### Optimization Tips

1. **Use Caching**: Repeated requests for the same data are served from cache
2. **Batch Requests**: Use orchestration endpoints to combine multiple agents
3. **Pagination**: Use pagination for large result sets
4. **Compression**: API supports gzip compression (automatically handled)

---

## 🔒 Security

### Best Practices

1. **Never share access tokens**: Keep tokens confidential
2. **Use HTTPS in production**: Always use encrypted connections
3. **Rotate tokens regularly**: Refresh tokens have 7-day expiry
4. **Validate inputs**: API performs comprehensive input validation
5. **Monitor usage**: Check API usage dashboard regularly

### CSRF Protection

All mutating endpoints (POST, PUT, DELETE) require CSRF tokens. Get a CSRF token:

```http
GET /api/v1/csrf-token
Authorization: Bearer YOUR_TOKEN
```

Include in requests:

```http
POST /api/v1/agents/company-profile
Authorization: Bearer YOUR_TOKEN
X-CSRF-Token: YOUR_CSRF_TOKEN
```

---

## 📞 Support

- **Documentation**: http://localhost:8000/docs
- **Issues**: https://github.com/yourusername/mi-navigator/issues
- **Email**: support@mi-navigator.com

---

**Last Updated**: 2026-01-26
**API Version**: 1.0.0
**Status**: Production Ready ✅
