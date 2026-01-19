#!/bin/bash

# Test Feature #148: Deleted item viewed by another user
# This test verifies graceful handling when one user views a report that another user deletes

set -e

API_BASE="http://localhost:8000/api/v1"

echo "===================================="
echo "Feature #148: Deleted item viewed by another user"
echo "===================================="
echo ""

# Helper function to get CSRF token
get_csrf_token() {
  curl -s "${API_BASE}/auth/csrf-token" | grep -o '"csrf_token":"[^"]*"' | cut -d'"' -f4
}

# Step 1: Create two test users (User A and User B)
echo "Step 1: Creating two test users..."
TIMESTAMP=$(date +%s)

# User A
USER_A_EMAIL="user_a_${TIMESTAMP}@test.com"
USER_A_PASSWORD="TestPass123!"
USER_A_NAME="User A Test"

curl -s -X POST "${API_BASE}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${USER_A_EMAIL}\",
    \"password\": \"${USER_A_PASSWORD}\",
    \"confirm_password\": \"${USER_A_PASSWORD}\",
    \"full_name\": \"${USER_A_NAME}\"
  }" > /dev/null

# User B
USER_B_EMAIL="user_b_${TIMESTAMP}@test.com"
USER_B_PASSWORD="TestPass123!"
USER_B_NAME="User B Test"

curl -s -X POST "${API_BASE}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${USER_B_EMAIL}\",
    \"password\": \"${USER_B_PASSWORD}\",
    \"confirm_password\": \"${USER_B_PASSWORD}\",
    \"full_name\": \"${USER_B_NAME}\"
  }" > /dev/null

echo "✅ User A created: ${USER_A_EMAIL}"
echo "✅ User B created: ${USER_B_EMAIL}"
echo ""

# Login User A
echo "Logging in User A..."
USER_A_RESPONSE=$(curl -s -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${USER_A_EMAIL}&password=${USER_A_PASSWORD}")

USER_A_TOKEN=$(echo "$USER_A_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$USER_A_TOKEN" ]; then
  echo "❌ Failed to login User A"
  echo "Response: $USER_A_RESPONSE"
  exit 1
fi

echo "✅ User A logged in successfully"
echo ""

# Login User B
echo "Logging in User B..."
USER_B_RESPONSE=$(curl -s -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${USER_B_EMAIL}&password=${USER_B_PASSWORD}")

USER_B_TOKEN=$(echo "$USER_B_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$USER_B_TOKEN" ]; then
  echo "❌ Failed to login User B"
  echo "Response: $USER_B_RESPONSE"
  exit 1
fi

echo "✅ User B logged in successfully"
echo ""

# Step 2: User B creates a report
echo "Step 2: User B creates a report..."
CSRF_TOKEN=$(get_csrf_token)

CREATE_RESPONSE=$(curl -s -X POST "${API_BASE}/reports" \
  -H "Authorization: Bearer ${USER_B_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: ${CSRF_TOKEN}" \
  -d '{
    "title": "Test Report for Deletion Scenario",
    "type": "market_analysis",
    "content": "This report will be deleted to test graceful error handling.",
    "summary": "Test report for Feature 148"
  }')

REPORT_ID=$(echo "$CREATE_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$REPORT_ID" ]; then
  echo "❌ Failed to create report"
  echo "Response: $CREATE_RESPONSE"
  exit 1
fi

echo "✅ Report created: ${REPORT_ID}"
echo ""

# Step 3: User A views the report (simulates opening the report)
echo "Step 3: User A views the report..."
VIEW_RESPONSE=$(curl -s -w "\n%{http_code}" "${API_BASE}/reports/${REPORT_ID}" \
  -H "Authorization: Bearer ${USER_A_TOKEN}")

HTTP_CODE=$(echo "$VIEW_RESPONSE" | tail -n1)
VIEW_DATA=$(echo "$VIEW_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo "❌ User A failed to view report (Expected 200, got ${HTTP_CODE})"
  echo "Response: $VIEW_DATA"
  exit 1
fi

REPORT_TITLE=$(echo "$VIEW_DATA" | grep -o '"title":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "✅ User A successfully viewed report: ${REPORT_TITLE}"
echo ""

# Step 4: User B deletes the report (while User A still has it open)
echo "Step 4: User B deletes the report..."
CSRF_TOKEN=$(get_csrf_token)

DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "${API_BASE}/reports/${REPORT_ID}" \
  -H "Authorization: Bearer ${USER_B_TOKEN}" \
  -H "X-CSRF-Token: ${CSRF_TOKEN}")

HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)
DELETE_DATA=$(echo "$DELETE_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo "❌ User B failed to delete report (Expected 200, got ${HTTP_CODE})"
  echo "Response: $DELETE_DATA"
  exit 1
fi

echo "✅ User B successfully deleted the report"
echo ""

# Step 5: User A tries to interact with the deleted report (refresh/reload)
echo "Step 5: User A tries to reload the deleted report..."
RELOAD_RESPONSE=$(curl -s -w "\n%{http_code}" "${API_BASE}/reports/${REPORT_ID}" \
  -H "Authorization: Bearer ${USER_A_TOKEN}")

HTTP_CODE=$(echo "$RELOAD_RESPONSE" | tail -n1)
RELOAD_DATA=$(echo "$RELOAD_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "404" ]; then
  echo "❌ Expected 404 Not Found, got ${HTTP_CODE}"
  echo "Response: $RELOAD_DATA"
  exit 1
fi

echo "✅ Server returned 404 (as expected)"
echo ""

# Step 6: Verify the error message is user-friendly
echo "Step 6: Verifying user-friendly error message..."
ERROR_MESSAGE=$(echo "$RELOAD_DATA" | grep -o '"detail":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ERROR_MESSAGE" ]; then
  echo "❌ No error message found in response"
  echo "Response: $RELOAD_DATA"
  exit 1
fi

echo "Error message: ${ERROR_MESSAGE}"

# Check if message is in Polish and user-friendly (not stack trace)
if echo "$ERROR_MESSAGE" | grep -iq "raport\|znaleziony\|not found"; then
  echo "✅ Error message is user-friendly: ${ERROR_MESSAGE}"
else
  echo "❌ Error message is not user-friendly"
  exit 1
fi

echo ""
echo "===================================="
echo "✅ ALL TESTS PASSED!"
echo "Feature #148: Deleted item viewed by another user - VERIFIED"
echo "===================================="
echo ""
echo "Summary:"
echo "- User A successfully viewed the report before deletion"
echo "- User B successfully deleted the report"
echo "- User A received 404 error when trying to reload deleted report"
echo "- Error message is user-friendly and appropriate"
echo "- Graceful error handling confirmed ✅"
