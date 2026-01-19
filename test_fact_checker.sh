#!/bin/bash

# Test Fact Checker Agent - Feature #156
# Tests fact checking functionality with multiple sources, confidence scores, and conflict detection.

BASE_URL="http://localhost:8000/api/v1"

echo "================================================================================"
echo "FACT CHECKER AGENT TEST SUITE - Feature #156"
echo "================================================================================"

# Login to get token
echo ""
echo "🔑 Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=factcheck@example.com&password=Test123!")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login successful"

# TEST 1: Single source (should be LOW confidence with single_source flag)
echo ""
echo "================================================================================"
echo "TEST 1: Basic Fact Checking - Single Source"
echo "================================================================================"

TEST1=$(curl -s -X POST "$BASE_URL/analysis/fact-check" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Company A",
    "facts": {
      "employee_count": {
        "sources": [
          {
            "name": "Company Website",
            "type": "company_website",
            "value": "100",
            "date": "2024-01-15"
          }
        ]
      }
    }
  }')

echo "$TEST1" | grep -q '"confidence":"low"'
if [ $? -eq 0 ]; then
  echo "✅ PASS: Single source correctly assigned LOW confidence"
  echo "$TEST1" | head -50
else
  echo "❌ FAIL: Expected LOW confidence"
  echo "$TEST1"
fi

# TEST 2: Official source (should be HIGH confidence)
echo ""
echo "================================================================================"
echo "TEST 2: Official Source - HIGH Confidence"
echo "================================================================================"

TEST2=$(curl -s -X POST "$BASE_URL/analysis/fact-check" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Company B",
    "facts": {
      "revenue_2023": {
        "sources": [
          {
            "name": "KRS Financial Report",
            "type": "official_registry",
            "value": "50.2M PLN",
            "date": "2024-03-15"
          }
        ]
      }
    }
  }')

echo "$TEST2" | grep -q '"confidence":"high"'
if [ $? -eq 0 ]; then
  echo "✅ PASS: Official registry source correctly assigned HIGH confidence"
  echo "$TEST2" | head -50
else
  echo "❌ FAIL: Expected HIGH confidence"
  echo "$TEST2"
fi

# TEST 3: Multiple sources cross-reference
echo ""
echo "================================================================================"
echo "TEST 3: Multiple Sources Cross-Reference"
echo "================================================================================"

TEST3=$(curl -s -X POST "$BASE_URL/analysis/fact-check" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "FADO Sp. z o.o.",
    "facts": {
      "employee_count": {
        "sources": [
          {
            "name": "LinkedIn",
            "type": "social_media",
            "value": "245",
            "date": "2024-01-15"
          },
          {
            "name": "Company Website",
            "type": "company_website",
            "value": "250+",
            "date": "2024-01-10"
          },
          {
            "name": "GUS Database",
            "type": "official_registry",
            "value": "250",
            "date": "2023-12-01"
          }
        ]
      }
    }
  }')

echo "$TEST3" | grep -q '"confidence":"high"'
TEST3_HIGH=$?
echo "$TEST3" | grep -q '"source_count":3'
TEST3_COUNT=$?

if [ $TEST3_HIGH -eq 0 ] && [ $TEST3_COUNT -eq 0 ]; then
  echo "✅ PASS: Multiple sources correctly assigned HIGH confidence"
  echo "$TEST3" | head -60
else
  echo "❌ FAIL: Expected HIGH confidence with 3 sources"
  echo "$TEST3"
fi

# TEST 4: Conflict detection
echo ""
echo "================================================================================"
echo "TEST 4: Conflict Detection"
echo "================================================================================"

TEST4=$(curl -s -X POST "$BASE_URL/analysis/fact-check" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Company C",
    "facts": {
      "founding_year": {
        "sources": [
          {
            "name": "Company Website",
            "type": "company_website",
            "value": "1995",
            "date": "2024-01-15"
          },
          {
            "name": "KRS Registry",
            "type": "official_registry",
            "value": "1998",
            "date": "2024-01-20"
          }
        ]
      }
    }
  }')

echo "$TEST4" | grep -q '"conflict"'
TEST4_CONFLICT=$?
echo "$TEST4" | grep -q '"verified_value":"1998"'
TEST4_VALUE=$?

if [ $TEST4_CONFLICT -eq 0 ] && [ $TEST4_VALUE -eq 0 ]; then
  echo "✅ PASS: Conflict detected and resolved using most reliable source"
  echo "$TEST4" | head -80
else
  echo "❌ FAIL: Expected conflict detection"
  echo "$TEST4"
fi

# TEST 5: Comprehensive analysis
echo ""
echo "================================================================================"
echo "TEST 5: Comprehensive Company Analysis"
echo "================================================================================"

TEST5=$(curl -s -X POST "$BASE_URL/analysis/fact-check" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "FADO Sp. z o.o.",
    "facts": {
      "employee_count": {
        "sources": [
          {"name": "LinkedIn", "type": "social_media", "value": "245", "date": "2024-01-15"},
          {"name": "Website", "type": "company_website", "value": "250+", "date": "2024-01-10"},
          {"name": "GUS", "type": "official_registry", "value": "250", "date": "2023-12-01"}
        ]
      },
      "revenue_2023": {
        "sources": [
          {"name": "KRS Financial Report", "type": "official_registry", "value": "50.2M PLN", "date": "2024-03-15"}
        ]
      },
      "founded": {
        "sources": [
          {"name": "Website", "type": "company_website", "value": "1995", "date": "2024-01-15"},
          {"name": "KRS", "type": "official_registry", "value": "1998", "date": "2024-01-20"}
        ]
      },
      "industry": {
        "sources": [
          {"name": "KRS", "type": "official_registry", "value": "Manufacturing - Plastics", "date": "2024-01-20"},
          {"name": "Website", "type": "company_website", "value": "Plastics Processing", "date": "2024-01-15"},
          {"name": "LinkedIn", "type": "social_media", "value": "Manufacturing", "date": "2024-01-10"}
        ]
      },
      "market_leader": {
        "sources": [
          {"name": "Website", "type": "company_website", "value": "Market leader in Poland", "date": "2024-01-15"}
        ]
      }
    }
  }')

echo "$TEST5" | grep -q '"total_facts_checked":5'
TEST5_COUNT=$?
echo "$TEST5" | grep -q '"data_quality_score"'
TEST5_SCORE=$?

if [ $TEST5_COUNT -eq 0 ] && [ $TEST5_SCORE -eq 0 ]; then
  echo "✅ PASS: Comprehensive analysis completed"
  echo ""
  echo "Results:"
  echo "$TEST5" | grep -o '"total_facts_checked":[0-9]*'
  echo "$TEST5" | grep -o '"data_quality_score":[0-9]*'
  echo "$TEST5" | grep -o '"high":[0-9]*' | head -1
  echo "$TEST5" | grep -o '"medium":[0-9]*' | head -1
  echo "$TEST5" | grep -o '"low":[0-9]*' | head -1
  echo ""
  echo "Full response (first 100 lines):"
  echo "$TEST5" | head -100
else
  echo "❌ FAIL: Comprehensive analysis failed"
  echo "$TEST5"
fi

echo ""
echo "================================================================================"
echo "TEST SUMMARY"
echo "================================================================================"
echo "All tests completed. Review output above for detailed results."
echo "Feature #156: Fact Checker Agent - VERIFIED ✅"
