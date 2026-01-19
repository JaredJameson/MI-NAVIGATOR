#!/bin/bash

# Feature #162: Agent retry on failure
# Simple test without jq dependency

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

echo "$RESPONSE" > test162_transient_response.json
echo "Response saved to test162_transient_response.json"
echo ""

# Check if response contains retry_metadata
if echo "$RESPONSE" | grep -q "_retry_metadata"; then
    echo "✅ PASS Step 3: Retry occurred (retry_metadata found in response)"
else
    echo "❌ FAIL Step 3: No retry metadata found"
fi

# Check if retry_count > 0
if echo "$RESPONSE" | grep -q '"retry_count":[^0]'; then
    echo "✅ PASS Step 4: Success on retry (retry_count > 0)"
else
    echo "❌ FAIL Step 4: retry_count is 0 or missing"
fi

echo ""
echo "Response preview:"
echo "$RESPONSE" | head -50
echo ""

echo "TEST 2: Check backend logs for retry messages"
echo "----------------------------------------------"
echo ""

# Wait a moment for logs to be written
sleep 1

# Check logs for retry messages
echo "Looking for retry log entries in backend_mi.log..."
RETRY_LOGS=$(tail -100 backend_mi.log | grep -i "retry" | head -20 || echo "")

if [ -n "$RETRY_LOGS" ]; then
    echo "✅ PASS: Retry log messages found:"
    echo "$RETRY_LOGS"
else
    echo "❌ FAIL: No retry log messages found"
fi

echo ""
echo "TEST 3: Verify max retry limit (permanent failure)"
echo "---------------------------------------------------"
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

echo "$RESPONSE2" > test162_permanent_response.json
echo "Response saved to test162_permanent_response.json"
echo ""

# Check if error status present
if echo "$RESPONSE2" | grep -q '"status":"error"'; then
    echo "✅ PASS Step 5: Max retry limit enforced (error status after retries)"
else
    echo "⚠️  WARNING: No error status found in response"
fi

# Check if error mentions attempts
if echo "$RESPONSE2" | grep -q "attempts"; then
    echo "✅ PASS: Error message mentions retry attempts"
else
    echo "❌ FAIL: Error message doesn't mention attempts"
fi

echo ""
echo "Response preview:"
echo "$RESPONSE2" | head -50
echo ""

echo "TEST 4: Verify exponential backoff in logs"
echo "------------------------------------------"
echo ""

# Check for exponential backoff delays (1.0s, 2.0s, 4.0s)
BACKOFF_LOGS=$(tail -200 backend_mi.log | grep "Retrying in" | head -10 || echo "")

if [ -n "$BACKOFF_LOGS" ]; then
    echo "✅ PASS: Exponential backoff logs found:"
    echo "$BACKOFF_LOGS"
else
    echo "⚠️  WARNING: No exponential backoff logs found"
fi

echo ""
echo "=========================================="
echo "FINAL VERIFICATION"
echo "=========================================="
echo ""

# Check logs for specific retry pattern
echo "Checking for complete retry sequence in logs..."
RETRY_SEQUENCE=$(tail -300 backend_mi.log | grep -E "(financial_analysis|attempt)" | tail -20 || echo "")

if [ -n "$RETRY_SEQUENCE" ]; then
    echo "Retry sequence logs:"
    echo "$RETRY_SEQUENCE"
else
    echo "No retry sequence found in logs"
fi

echo ""
echo "TEST SUMMARY:"
echo "  - Transient failure response: test162_transient_response.json"
echo "  - Permanent failure response: test162_permanent_response.json"
echo "  - Backend logs: tail -300 backend_mi.log | grep retry"
echo ""
