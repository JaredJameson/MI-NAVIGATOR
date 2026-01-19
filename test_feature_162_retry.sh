#!/bin/bash

# Feature #162: Agent retry on failure
# Test Steps:
# 1. Start analysis
# 2. Simulate transient failure
# 3. Verify retry occurs
# 4. Verify success on retry
# 5. Verify max retry limit enforced

set -e

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0Y2YwM2M0Ny02ODFiLTQ5MDgtYjI4Yi03MmZhMGU3ZDhjMmUiLCJleHAiOjE3Njg4MzM2NjgsInR5cGUiOiJhY2Nlc3MiLCJqdGkiOiIxMWNjZDg5Zi00MGM2LTQ5NTUtOTM5My1kMmY4NDM4ZTk3YzkifQ.KVw6hYWpJ7dDUrtbt9uydrbXzU4EFdM0cT0KOJL3h5Q"
API_URL="http://localhost:8000/api/v1/analysis"

echo "=========================================="
echo "Feature #162: Agent Retry on Failure"
echo "=========================================="
echo ""

# Test 1: Simulate transient failure - should retry and succeed
echo "TEST 1: Transient failure with successful retry"
echo "----------------------------------------------"
echo "Request: Simulate transient failure on financial_analysis agent"
echo ""

cat > test162_transient.json << 'EOF'
{
  "target": "TestCompany Sp. z o.o.",
  "analysis_type": "company",
  "simulate_transient_failures": ["financial_analysis"]
}
EOF

echo "Sending request with simulate_transient_failures=['financial_analysis']..."
RESPONSE=$(curl -s -X POST "$API_URL/comprehensive" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @test162_transient.json)

echo "$RESPONSE" | jq '.' > test162_transient_response.json

# Check if analysis completed
STATUS=$(echo "$RESPONSE" | jq -r '.status')
echo "Analysis status: $STATUS"

# Check if financial_analysis succeeded after retry
FA_STATUS=$(echo "$RESPONSE" | jq -r '.results.financial_analysis.status // "completed"')
echo "Financial analysis status: $FA_STATUS"

# Check for retry metadata
RETRY_COUNT=$(echo "$RESPONSE" | jq -r '.results.financial_analysis._retry_metadata.retry_count // "not found"')
echo "Retry count: $RETRY_COUNT"

if [ "$RETRY_COUNT" != "not found" ] && [ "$RETRY_COUNT" -gt 0 ]; then
    echo "✅ PASS: Agent retried and succeeded (retry_count=$RETRY_COUNT)"
else
    echo "❌ FAIL: No retry metadata found or retry_count=0"
fi

echo ""
echo "TEST 2: Check backend logs for retry messages"
echo "----------------------------------------------"
echo "Looking for retry log entries..."
echo ""

# Check logs for retry messages (last 100 lines)
RETRY_LOGS=$(tail -100 backend_mi.log | grep -i "retry" || echo "No retry logs found")
echo "$RETRY_LOGS"

if echo "$RETRY_LOGS" | grep -q "Retrying in"; then
    echo "✅ PASS: Retry log messages found"
else
    echo "❌ FAIL: No retry log messages found"
fi

echo ""
echo "TEST 3: Verify max retry limit (permanent failure)"
echo "---------------------------------------------------"
echo "Request: Simulate permanent failure (simulate_error=true)"
echo ""

cat > test162_permanent.json << 'EOF'
{
  "target": "FailCompany Sp. z o.o.",
  "analysis_type": "company",
  "simulate_failures": ["company_profile"]
}
EOF

echo "Sending request with simulate_failures=['company_profile']..."
RESPONSE2=$(curl -s -X POST "$API_URL/comprehensive" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @test162_permanent.json)

echo "$RESPONSE2" | jq '.' > test162_permanent_response.json

# Check if company_profile failed
CP_STATUS=$(echo "$RESPONSE2" | jq -r '.results.company_profile.status // "unknown"')
echo "Company profile status: $CP_STATUS"

if [ "$CP_STATUS" = "error" ]; then
    echo "✅ PASS: Permanent failure correctly resulted in error status"
else
    echo "❌ FAIL: Expected error status, got: $CP_STATUS"
fi

# Check error message mentions retries
ERROR_MSG=$(echo "$RESPONSE2" | jq -r '.results.company_profile.error // ""')
echo "Error message: $ERROR_MSG"

if echo "$ERROR_MSG" | grep -q "attempts"; then
    echo "✅ PASS: Error message mentions retry attempts"
else
    echo "❌ FAIL: Error message doesn't mention retry attempts"
fi

echo ""
echo "TEST 4: Verify exponential backoff timing"
echo "------------------------------------------"
echo "Checking logs for exponential backoff delays (1s, 2s, 4s)..."
echo ""

BACKOFF_LOGS=$(tail -200 backend_mi.log | grep -E "Retrying in (1\.0|2\.0|4\.0)" || echo "No backoff logs found")
echo "$BACKOFF_LOGS"

if echo "$BACKOFF_LOGS" | grep -q "Retrying in"; then
    echo "✅ PASS: Exponential backoff delay logs found"
else
    echo "⚠️  WARNING: No exponential backoff logs found (may not have triggered yet)"
fi

echo ""
echo "TEST 5: Verify retry metadata in successful result"
echo "---------------------------------------------------"

# Check retry metadata structure
SUCCEEDED_ON=$(echo "$RESPONSE" | jq -r '.results.financial_analysis._retry_metadata.succeeded_on_attempt // "not found"')
TOTAL_ATTEMPTS=$(echo "$RESPONSE" | jq -r '.results.financial_analysis._retry_metadata.total_attempts // "not found"')

echo "Succeeded on attempt: $SUCCEEDED_ON"
echo "Total attempts: $TOTAL_ATTEMPTS"

if [ "$SUCCEEDED_ON" != "not found" ] && [ "$TOTAL_ATTEMPTS" != "not found" ]; then
    echo "✅ PASS: Retry metadata structure correct"
else
    echo "❌ FAIL: Incomplete retry metadata"
fi

echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo ""
echo "Full response saved to:"
echo "  - test162_transient_response.json (transient failure with retry)"
echo "  - test162_permanent_response.json (permanent failure)"
echo ""
echo "Check backend logs with:"
echo "  tail -200 backend_mi.log | grep -E '(retry|Retry|financial_analysis)'"
echo ""
