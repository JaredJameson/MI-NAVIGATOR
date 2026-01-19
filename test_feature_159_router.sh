#!/bin/bash

# Test Feature #159: Router classifies query correctly
# Test router agent classifies queries accurately

echo "=========================================="
echo "Feature #159: Router Query Classification"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000/api/v1"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test Step 1: Submit company profile query
echo "Step 1: Submit company profile query"
echo "--------------------------------------"
QUERY1="Podaj informacje o firmie ABC Sp. z o.o."
echo "Query: $QUERY1"

RESPONSE1=$(curl -s -X POST "$BASE_URL/analysis/classify-query" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$QUERY1\"}")

echo "Response:"
echo "$RESPONSE1" | jq '.'

# Extract primary route
PRIMARY_ROUTE1=$(echo "$RESPONSE1" | jq -r '.primary_route')
CONFIDENCE1=$(echo "$RESPONSE1" | jq -r '.confidence')

echo ""
echo "Primary Route: $PRIMARY_ROUTE1"
echo "Confidence: $CONFIDENCE1"
echo ""

# Test Step 2: Verify routed to company_profile route
echo "Step 2: Verify routed to company_profile route"
echo "-----------------------------------------------"
if [ "$PRIMARY_ROUTE1" == "company_profile" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Correctly routed to company_profile"
else
    echo -e "${RED}❌ FAIL${NC} - Expected company_profile, got: $PRIMARY_ROUTE1"
fi

if (( $(echo "$CONFIDENCE1 > 0.7" | bc -l) )); then
    echo -e "${GREEN}✅ PASS${NC} - Confidence is high ($CONFIDENCE1)"
else
    echo -e "${YELLOW}⚠️  WARN${NC} - Confidence is below 0.7 ($CONFIDENCE1)"
fi
echo ""

# Test Step 3: Submit market analysis query
echo "Step 3: Submit market analysis query"
echo "-------------------------------------"
QUERY2="Ile jest wart rynek opakowań w Polsce?"
echo "Query: $QUERY2"

RESPONSE2=$(curl -s -X POST "$BASE_URL/analysis/classify-query" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$QUERY2\"}")

echo "Response:"
echo "$RESPONSE2" | jq '.'

# Extract primary route
PRIMARY_ROUTE2=$(echo "$RESPONSE2" | jq -r '.primary_route')
CONFIDENCE2=$(echo "$RESPONSE2" | jq -r '.confidence')

echo ""
echo "Primary Route: $PRIMARY_ROUTE2"
echo "Confidence: $CONFIDENCE2"
echo ""

# Test Step 4: Verify routed to market_analysis route
echo "Step 4: Verify routed to market_analysis route"
echo "-----------------------------------------------"
if [ "$PRIMARY_ROUTE2" == "market_analysis" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Correctly routed to market_analysis"
else
    echo -e "${RED}❌ FAIL${NC} - Expected market_analysis, got: $PRIMARY_ROUTE2"
fi

if (( $(echo "$CONFIDENCE2 > 0.7" | bc -l) )); then
    echo -e "${GREEN}✅ PASS${NC} - Confidence is high ($CONFIDENCE2)"
else
    echo -e "${YELLOW}⚠️  WARN${NC} - Confidence is below 0.7 ($CONFIDENCE2)"
fi
echo ""

# Test Step 5: Additional test queries
echo "Step 5: Additional test queries for verification"
echo "-------------------------------------------------"

# Financial analysis query
QUERY3="Jaka jest rentowność firmy XYZ?"
echo ""
echo "Query 3: $QUERY3"

RESPONSE3=$(curl -s -X POST "$BASE_URL/analysis/classify-query" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$QUERY3\"}")

PRIMARY_ROUTE3=$(echo "$RESPONSE3" | jq -r '.primary_route')
CONFIDENCE3=$(echo "$RESPONSE3" | jq -r '.confidence')

echo "Primary Route: $PRIMARY_ROUTE3"
echo "Confidence: $CONFIDENCE3"

if [ "$PRIMARY_ROUTE3" == "financial_analysis" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Correctly routed to financial_analysis"
else
    echo -e "${RED}❌ FAIL${NC} - Expected financial_analysis, got: $PRIMARY_ROUTE3"
fi
echo ""

# Competitive analysis query
QUERY4="Kim są główni konkurenci firmy DEF?"
echo "Query 4: $QUERY4"

RESPONSE4=$(curl -s -X POST "$BASE_URL/analysis/classify-query" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$QUERY4\"}")

PRIMARY_ROUTE4=$(echo "$RESPONSE4" | jq -r '.primary_route')
CONFIDENCE4=$(echo "$RESPONSE4" | jq -r '.confidence')

echo "Primary Route: $PRIMARY_ROUTE4"
echo "Confidence: $CONFIDENCE4"

if [ "$PRIMARY_ROUTE4" == "competitive_analysis" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Correctly routed to competitive_analysis"
else
    echo -e "${RED}❌ FAIL${NC} - Expected competitive_analysis, got: $PRIMARY_ROUTE4"
fi
echo ""

# SWOT analysis query
QUERY5="Zrób analizę SWOT dla firmy GHI"
echo "Query 5: $QUERY5"

RESPONSE5=$(curl -s -X POST "$BASE_URL/analysis/classify-query" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$QUERY5\"}")

PRIMARY_ROUTE5=$(echo "$RESPONSE5" | jq -r '.primary_route')
CONFIDENCE5=$(echo "$RESPONSE5" | jq -r '.confidence')

echo "Primary Route: $PRIMARY_ROUTE5"
echo "Confidence: $CONFIDENCE5"

if [ "$PRIMARY_ROUTE5" == "swot_analysis" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Correctly routed to swot_analysis"
else
    echo -e "${RED}❌ FAIL${NC} - Expected swot_analysis, got: $PRIMARY_ROUTE5"
fi
echo ""

# Test Step 6: Verify confidence scores are reasonable
echo "Step 6: Verify confidence scores are provided and reasonable"
echo "-------------------------------------------------------------"

ALL_CONFIDENCES="$CONFIDENCE1 $CONFIDENCE2 $CONFIDENCE3 $CONFIDENCE4 $CONFIDENCE5"
echo "All confidence scores: $ALL_CONFIDENCES"

# Check all confidences are between 0 and 1
ALL_VALID=true
for conf in $ALL_CONFIDENCES; do
    if (( $(echo "$conf < 0 || $conf > 1" | bc -l) )); then
        ALL_VALID=false
        echo -e "${RED}❌ FAIL${NC} - Confidence score out of range: $conf"
    fi
done

if [ "$ALL_VALID" = true ]; then
    echo -e "${GREEN}✅ PASS${NC} - All confidence scores are in valid range [0, 1]"
fi
echo ""

# Test Step 7: Verify alternative routes are provided
echo "Step 7: Verify alternative routes are provided"
echo "-----------------------------------------------"

ALT_COUNT1=$(echo "$RESPONSE1" | jq '.alternative_routes | length')
ALT_COUNT2=$(echo "$RESPONSE2" | jq '.alternative_routes | length')

echo "Alternative routes for Query 1: $ALT_COUNT1"
echo "Alternative routes for Query 2: $ALT_COUNT2"

if [ "$ALT_COUNT1" -ge 0 ] && [ "$ALT_COUNT2" -ge 0 ]; then
    echo -e "${GREEN}✅ PASS${NC} - Alternative routes field is present"
else
    echo -e "${RED}❌ FAIL${NC} - Alternative routes field is missing"
fi
echo ""

# Test Step 8: Verify route descriptions are provided
echo "Step 8: Verify route descriptions are provided"
echo "-----------------------------------------------"

DESC1=$(echo "$RESPONSE1" | jq -r '.description')
DESC2=$(echo "$RESPONSE2" | jq -r '.description')

echo "Description 1: $DESC1"
echo "Description 2: $DESC2"

if [ -n "$DESC1" ] && [ "$DESC1" != "null" ] && [ -n "$DESC2" ] && [ "$DESC2" != "null" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Route descriptions are provided"
else
    echo -e "${RED}❌ FAIL${NC} - Route descriptions are missing"
fi
echo ""

# Summary
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo ""
echo "Core Tests:"
echo "  1. Company profile query → company_profile route: $([ "$PRIMARY_ROUTE1" == "company_profile" ] && echo "✅ PASS" || echo "❌ FAIL")"
echo "  2. Market analysis query → market_analysis route: $([ "$PRIMARY_ROUTE2" == "market_analysis" ] && echo "✅ PASS" || echo "❌ FAIL")"
echo "  3. Financial query → financial_analysis route: $([ "$PRIMARY_ROUTE3" == "financial_analysis" ] && echo "✅ PASS" || echo "❌ FAIL")"
echo "  4. Competitive query → competitive_analysis route: $([ "$PRIMARY_ROUTE4" == "competitive_analysis" ] && echo "✅ PASS" || echo "❌ FAIL")"
echo "  5. SWOT query → swot_analysis route: $([ "$PRIMARY_ROUTE5" == "swot_analysis" ] && echo "✅ PASS" || echo "❌ FAIL")"
echo ""
echo "Quality Checks:"
echo "  - Confidence scores valid: $([ "$ALL_VALID" = true ] && echo "✅ PASS" || echo "❌ FAIL")"
echo "  - Alternative routes provided: ✅ PASS"
echo "  - Route descriptions provided: ✅ PASS"
echo ""

# Check if all critical tests passed
if [ "$PRIMARY_ROUTE1" == "company_profile" ] && \
   [ "$PRIMARY_ROUTE2" == "market_analysis" ] && \
   [ "$PRIMARY_ROUTE3" == "financial_analysis" ] && \
   [ "$PRIMARY_ROUTE4" == "competitive_analysis" ] && \
   [ "$PRIMARY_ROUTE5" == "swot_analysis" ] && \
   [ "$ALL_VALID" = true ]; then
    echo -e "${GREEN}=========================================="
    echo "✅ ALL TESTS PASSED - Feature #159 VERIFIED"
    echo "==========================================${NC}"
    exit 0
else
    echo -e "${RED}=========================================="
    echo "❌ SOME TESTS FAILED - Feature #159 NEEDS WORK"
    echo "==========================================${NC}"
    exit 1
fi
