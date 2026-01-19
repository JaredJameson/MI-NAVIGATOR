#!/bin/bash
# Feature #163: Agent timeout handling - QUICK TEST (10 seconds timeout)

echo "=========================================="
echo "Feature #163: Agent Timeout - Quick Test"
echo "=========================================="
echo ""

API_URL="http://localhost:8000/api/v1"

# Step 1: Register or login test user
echo "Step 1: Getting access token..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "timeout_test@example.com",
    "password": "TestPass123!"
  }')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# If login failed, try to register
if [ -z "$TOKEN" ]; then
  echo "Login failed, registering new user..."
  REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/auth/register" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "timeout_test@example.com",
      "password": "TestPass123!",
      "name": "Timeout Test User"
    }')

  TOKEN=$(echo "$REGISTER_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
fi

if [ -z "$TOKEN" ]; then
  echo "❌ ERROR: Failed to get token"
  exit 1
fi

echo "✅ Token received"
echo ""

# Step 2: Test analysis with short timeout
# We'll use "company" analysis type which has shorter execution plan
echo "Step 2: Testing timeout with slow agent..."
echo "⏱️  Starting analysis (timeout should trigger in ~10-15s)..."
echo ""

SLOW_START=$(date +%s)
SLOW_RESPONSE=$(curl -s -X POST "${API_URL}/analysis/comprehensive" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "target": "Timeout Test Company",
    "analysis_type": "company",
    "simulate_slow": ["company_profile"],
    "phase_timeout": 10
  }')
SLOW_END=$(date +%s)
SLOW_DURATION=$((SLOW_END - SLOW_START))

echo "✅ Analysis completed in ${SLOW_DURATION}s"
echo ""

# Save response
echo "$SLOW_RESPONSE" > test163_quick_response.json
echo "Response saved to: test163_quick_response.json"
echo ""

# Step 3: Verify results
echo "Step 3: Verifying timeout behavior..."
echo ""

# Check for timeout in response
if echo "$SLOW_RESPONSE" | grep -qi "timeout\|timed out"; then
  echo "✅ PASS: Timeout message found in response"
  echo "$SLOW_RESPONSE" | grep -i "timeout" | head -3
else
  echo "❌ FAIL: No timeout message in response"
fi
echo ""

# Check response structure
echo "Step 4: Checking response structure..."
STATUS=$(echo "$SLOW_RESPONSE" | grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "Overall status: $STATUS"

# Count errors
ERROR_COUNT=$(echo "$SLOW_RESPONSE" | grep -o '"status":"error"' | wc -l)
TIMEOUT_COUNT=$(echo "$SLOW_RESPONSE" | grep -o '"status":"timeout"' | wc -l)
echo "Agents with errors: $ERROR_COUNT"
echo "Agents with timeout: $TIMEOUT_COUNT"

if [ $TIMEOUT_COUNT -gt 0 ]; then
  echo "✅ PASS: At least one agent marked as timeout"
else
  echo "❌ FAIL: No agents marked as timeout"
fi

echo ""
echo "=========================================="
echo "Test Complete"
echo "=========================================="
echo "Duration: ${SLOW_DURATION}s"
echo ""
echo "View full response: cat test163_quick_response.json | jq ."
echo ""
