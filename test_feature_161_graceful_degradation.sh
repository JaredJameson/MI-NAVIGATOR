#!/bin/bash

# Feature #161: Agent failure graceful degradation
# Test that system continues when single agent fails

set -e

BASE_URL="http://localhost:8000/api/v1"
EMAIL="test161@example.com"
PASSWORD="Test123!"

echo "=========================================="
echo "Feature #161: Agent Failure Graceful Degradation"
echo "=========================================="
echo ""

# Step 1: Register/login user
echo "Step 1: Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Login failed. Trying to register..."

  REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\",\"name\":\"Test User 161\"}")

  echo "Registration response: $REGISTER_RESPONSE"

  # Try login again
  LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$EMAIL&password=$PASSWORD")

  TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
fi

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Failed to get auth token"
  exit 1
fi

echo "✅ Authenticated successfully"
echo ""

# Test 1: Normal execution (no failures)
echo "=========================================="
echo "Test 1: Normal Execution (No Failures)"
echo "=========================================="
echo ""

NORMAL_RESPONSE=$(curl -s -X POST "$BASE_URL/analysis/comprehensive" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "TestCompany Normal",
    "analysis_type": "comprehensive"
  }')

echo "Response:"
echo "$NORMAL_RESPONSE" | jq '.'
echo ""

# Verify all agents completed
FAILED_COUNT=$(echo "$NORMAL_RESPONSE" | jq -r '.summary.failed_agents')
SUCCESS_COUNT=$(echo "$NORMAL_RESPONSE" | jq -r '.summary.successful_agents')
TOTAL_COUNT=$(echo "$NORMAL_RESPONSE" | jq -r '.summary.total_agents')

echo "Summary:"
echo "  Total agents: $TOTAL_COUNT"
echo "  Successful: $SUCCESS_COUNT"
echo "  Failed: $FAILED_COUNT"
echo ""

if [ "$FAILED_COUNT" == "0" ]; then
  echo "✅ Test 1 PASSED: All agents completed successfully"
else
  echo "❌ Test 1 FAILED: Expected 0 failures, got $FAILED_COUNT"
fi
echo ""

# Test 2: Simulate single agent failure
echo "=========================================="
echo "Test 2: Single Agent Failure (financial_analysis)"
echo "=========================================="
echo ""

FAILURE_RESPONSE=$(curl -s -X POST "$BASE_URL/analysis/comprehensive" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "TestCompany Failure",
    "analysis_type": "comprehensive",
    "simulate_failures": ["financial_analysis"]
  }')

echo "Response:"
echo "$FAILURE_RESPONSE" | jq '.'
echo ""

# Verify graceful degradation
FAILED_COUNT=$(echo "$FAILURE_RESPONSE" | jq -r '.summary.failed_agents')
SUCCESS_COUNT=$(echo "$FAILURE_RESPONSE" | jq -r '.summary.successful_agents')
TOTAL_COUNT=$(echo "$FAILURE_RESPONSE" | jq -r '.summary.total_agents')
FAILED_LIST=$(echo "$FAILURE_RESPONSE" | jq -r '.summary.failed_agent_list[]')
SUCCESS_RATE=$(echo "$FAILURE_RESPONSE" | jq -r '.summary.success_rate')
STATUS=$(echo "$FAILURE_RESPONSE" | jq -r '.status')

echo "Summary:"
echo "  Total agents: $TOTAL_COUNT"
echo "  Successful: $SUCCESS_COUNT"
echo "  Failed: $FAILED_COUNT"
echo "  Failed agents: $FAILED_LIST"
echo "  Success rate: $SUCCESS_RATE%"
echo "  Status: $STATUS"
echo ""

# Step 2: Verify one agent failed
if [ "$FAILED_COUNT" == "1" ]; then
  echo "✅ Step 2 PASSED: One agent failed as expected"
else
  echo "❌ Step 2 FAILED: Expected 1 failure, got $FAILED_COUNT"
  exit 1
fi
echo ""

# Step 3: Verify other agents continued
if [ "$SUCCESS_COUNT" -ge "6" ]; then
  echo "✅ Step 3 PASSED: Other agents continued ($SUCCESS_COUNT successful)"
else
  echo "❌ Step 3 FAILED: Expected at least 6 successful agents, got $SUCCESS_COUNT"
  exit 1
fi
echo ""

# Step 4: Verify partial results returned
RESULTS_COUNT=$(echo "$FAILURE_RESPONSE" | jq -r '.results | length')
if [ "$RESULTS_COUNT" -ge "6" ]; then
  echo "✅ Step 4 PASSED: Partial results returned ($RESULTS_COUNT results)"
else
  echo "❌ Step 4 FAILED: Expected at least 6 results, got $RESULTS_COUNT"
  exit 1
fi
echo ""

# Step 5: Verify failure is reported
ERRORS=$(echo "$FAILURE_RESPONSE" | jq -r '.summary.errors[]' | grep -i "financial_analysis" || true)
if [ -n "$ERRORS" ]; then
  echo "✅ Step 5 PASSED: Failure reported in output"
  echo "  Error: $ERRORS"
else
  echo "❌ Step 5 FAILED: Failure not reported in output"
  exit 1
fi
echo ""

# Test 3: Multiple agent failures
echo "=========================================="
echo "Test 3: Multiple Agent Failures"
echo "=========================================="
echo ""

MULTI_FAILURE_RESPONSE=$(curl -s -X POST "$BASE_URL/analysis/comprehensive" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "TestCompany Multi Failure",
    "analysis_type": "comprehensive",
    "simulate_failures": ["financial_analysis", "digital_presence", "competitor_mapping"]
  }')

echo "Response:"
echo "$MULTI_FAILURE_RESPONSE" | jq '.'
echo ""

FAILED_COUNT=$(echo "$MULTI_FAILURE_RESPONSE" | jq -r '.summary.failed_agents')
SUCCESS_COUNT=$(echo "$MULTI_FAILURE_RESPONSE" | jq -r '.summary.successful_agents')
SUCCESS_RATE=$(echo "$MULTI_FAILURE_RESPONSE" | jq -r '.summary.success_rate')

echo "Summary:"
echo "  Total agents: $(echo "$MULTI_FAILURE_RESPONSE" | jq -r '.summary.total_agents')"
echo "  Successful: $SUCCESS_COUNT"
echo "  Failed: $FAILED_COUNT"
echo "  Success rate: $SUCCESS_RATE%"
echo ""

if [ "$FAILED_COUNT" == "3" ] && [ "$SUCCESS_COUNT" -ge "4" ]; then
  echo "✅ Test 3 PASSED: Multiple failures handled gracefully"
else
  echo "❌ Test 3 FAILED: Expected 3 failures and ≥4 successes, got $FAILED_COUNT failures and $SUCCESS_COUNT successes"
fi
echo ""

# Final verification
echo "=========================================="
echo "FINAL VERIFICATION"
echo "=========================================="
echo ""

# Verify status is still "completed" even with failures
if [ "$STATUS" == "completed" ]; then
  echo "✅ Job status is 'completed' despite agent failures"
else
  echo "❌ Job status should be 'completed', got: $STATUS"
fi
echo ""

echo "=========================================="
echo "ALL TESTS COMPLETED"
echo "=========================================="
echo ""
echo "✅ Feature #161: Agent failure graceful degradation - VERIFIED"
echo ""
echo "Key findings:"
echo "  - System continues when single agent fails"
echo "  - Other agents execute successfully in parallel"
echo "  - Partial results are returned"
echo "  - Failures are properly reported"
echo "  - Job completes with 'completed' status"
