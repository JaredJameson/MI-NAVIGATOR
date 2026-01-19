#!/bin/bash
# Simple test for Insight Generator - Feature #157

API_URL="http://localhost:8000/api/v1"

# Get token (assuming user exists from previous tests)
echo "Getting authentication token..."
TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=factcheck@example.com&password=Test123!" | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"//;s/"//')

if [ -z "$TOKEN" ]; then
    echo "Failed to get token, trying insight_test2@example.com..."
    TOKEN=$(curl -s -X POST "$API_URL/auth/login" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "username=insight_test2@example.com&password=Test123!" | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"//;s/"//')
fi

if [ -z "$TOKEN" ]; then
    echo "No token available. Please ensure test user exists."
    exit 1
fi

echo "Token obtained: ${TOKEN:0:20}..."

# Test 1: High-growth company
echo ""
echo "========================================="
echo "TEST 1: High-growth, profitable company"
echo "========================================="

curl -s -X POST "$API_URL/analysis/generate-insights" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d @- << 'EOF'
{
  "company_name": "TechGrowth Sp. z o.o.",
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
  }
}
EOF

echo ""
echo ""
echo "========================================="
echo "TEST 2: Struggling company"
echo "========================================="

curl -s -X POST "$API_URL/analysis/generate-insights" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d @- << 'EOF'
{
  "company_name": "Declining Corp",
  "financial_data": {
    "revenue": 10000000,
    "revenue_growth": -8.5,
    "profit_margin": 3.2,
    "debt_to_equity": 2.5,
    "liquidity_ratio": 0.8
  }
}
EOF

echo ""
echo ""
echo "Feature #157 manual verification completed."
echo "Check responses above for:"
echo "  1. Insights generated"
echo "  2. Data-backed with source metrics"
echo "  3. Specific recommendations"
echo "  4. Risks identified"
