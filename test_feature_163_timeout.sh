#!/bin/bash
# Feature #163: Agent timeout handling test

echo "=========================================="
echo "Feature #163: Agent Timeout Handling Test"
echo "=========================================="
echo ""

API_URL="http://localhost:8000/api/v1"

# Step 1: Register test user
echo "Step 1: Creating test user..."
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "timeout_test@example.com",
    "password": "TestPass123!",
    "name": "Timeout Test User"
  }')

echo "$REGISTER_RESPONSE" | head -c 200
echo ""
echo ""

# Step 2: Login to get token
echo "Step 2: Logging in to get access token..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "timeout_test@example.com",
    "password": "TestPass123!"
  }')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ ERROR: Failed to get token"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Token received: ${TOKEN:0:50}..."
echo ""

# Step 3: Test normal analysis (baseline)
echo "Step 3: Running normal analysis (baseline - should complete)..."
NORMAL_START=$(date +%s)
NORMAL_RESPONSE=$(curl -s -X POST "${API_URL}/analysis/comprehensive" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "target": "Test Company",
    "analysis_type": "comprehensive"
  }')
NORMAL_END=$(date +%s)
NORMAL_DURATION=$((NORMAL_END - NORMAL_START))

echo "⏱️  Normal analysis duration: ${NORMAL_DURATION}s"
echo "Status: $(echo "$NORMAL_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)"
echo ""

# Step 4: Test analysis with slow agent (should timeout)
echo "Step 4: Running analysis with slow agent (should timeout after 120s)..."
echo "⚠️  This will take ~2 minutes to test timeout..."
SLOW_START=$(date +%s)
SLOW_RESPONSE=$(curl -s -X POST "${API_URL}/analysis/comprehensive" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "target": "Test Company Slow",
    "analysis_type": "comprehensive",
    "simulate_slow": ["company_profile"]
  }')
SLOW_END=$(date +%s)
SLOW_DURATION=$((SLOW_END - SLOW_START))

echo ""
echo "⏱️  Slow analysis duration: ${SLOW_DURATION}s (expected: ~120s)"
echo ""

# Step 5: Verify timeout was enforced
echo "Step 5: Verifying timeout behavior..."
echo ""

# Check if timeout occurred
if echo "$SLOW_RESPONSE" | grep -q "timeout\|timed out"; then
  echo "✅ PASS: Timeout message found in response"
else
  echo "❌ FAIL: No timeout message in response"
fi

# Check execution time (should be close to 120s, not 150s)
if [ $SLOW_DURATION -ge 115 ] && [ $SLOW_DURATION -le 125 ]; then
  echo "✅ PASS: Timeout enforced (~120s, actual: ${SLOW_DURATION}s)"
else
  echo "❌ FAIL: Timeout not properly enforced (expected ~120s, got ${SLOW_DURATION}s)"
fi

# Step 6: Check for partial results
echo ""
echo "Step 6: Checking response structure..."
echo ""

# Save full response to file
echo "$SLOW_RESPONSE" > test163_timeout_response.json

# Check status
STATUS=$(echo "$SLOW_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
echo "Response status: $STATUS"

# Check for errors in summary
FAILED_AGENTS=$(echo "$SLOW_RESPONSE" | grep -o '"failed_agents":[0-9]*' | cut -d':' -f2)
echo "Failed agents: $FAILED_AGENTS"

# Check for company_profile timeout
if echo "$SLOW_RESPONSE" | grep -q '"company_profile"'; then
  echo "✅ PASS: company_profile present in results"

  # Check if it has timeout status
  if echo "$SLOW_RESPONSE" | grep -A5 '"company_profile"' | grep -q '"status":"timeout"'; then
    echo "✅ PASS: company_profile marked as timeout"
  else
    echo "⚠️  WARNING: company_profile not marked as timeout"
  fi
else
  echo "❌ FAIL: company_profile missing from results"
fi

# Check for other agents (should have completed)
if echo "$SLOW_RESPONSE" | grep -q '"financial_analysis"'; then
  echo "✅ PASS: Other agents (financial_analysis) present in results"
else
  echo "❌ FAIL: Other agents missing (no graceful continuation)"
fi

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Normal analysis: ${NORMAL_DURATION}s"
echo "Slow analysis: ${SLOW_DURATION}s"
echo "Full response saved to: test163_timeout_response.json"
echo ""
echo "Review the response file to verify:"
echo "  1. Timeout message is shown"
echo "  2. Partial results are included"
echo "  3. No hung processes (execution completed)"
echo ""
