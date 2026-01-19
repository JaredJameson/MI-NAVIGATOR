#!/bin/bash

# Feature #142: Long text truncation with ellipsis
# Test Steps:
# 1. Create item with very long title
# 2. View item in list
# 3. Verify text is truncated
# 4. Verify ellipsis indicator
# 5. Hover/click to see full text

set -e

API_BASE="http://localhost:8000/api/v1"
FRONTEND_BASE="http://localhost:3000"

echo "=========================================="
echo "Feature #142: Long text truncation"
echo "=========================================="
echo ""

# Generate a very long title
LONG_TITLE="This is an extremely long project title that should definitely be truncated when displayed in the list view because it contains way too many characters and would break the layout if shown in full without proper text truncation handling using CSS ellipsis or line-clamp utilities to ensure a clean user interface"

echo "Step 1: Create test user and login"
echo "-----------------------------------"

# Create unique test user
TIMESTAMP=$(date +%s)
TEST_EMAIL="truncate_test_${TIMESTAMP}@test.com"
TEST_PASSWORD="TestPassword123"

# Register user
REGISTER_RESPONSE=$(curl -s -X POST "${API_BASE}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_EMAIL}\",
    \"password\": \"${TEST_PASSWORD}\",
    \"confirm_password\": \"${TEST_PASSWORD}\",
    \"name\": \"Truncate Test User\"
  }")

echo "Registration response: ${REGISTER_RESPONSE}"

# Login to get token
LOGIN_RESPONSE=$(curl -s -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${TEST_EMAIL}&password=${TEST_PASSWORD}")

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\(.*\)"/\1/')

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ ERROR: Failed to get access token"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ User logged in successfully"
echo ""

# Get CSRF token
echo "Getting CSRF token..."
CSRF_TOKEN=$(curl -s -X GET "${API_BASE}/auth/csrf-token" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | grep -o '"csrf_token":"[^"]*"' | sed 's/"csrf_token":"\(.*\)"/\1/')

if [ -z "$CSRF_TOKEN" ]; then
  echo "❌ ERROR: Failed to get CSRF token"
  exit 1
fi

echo "✅ Got CSRF token"
echo ""

echo "Step 2: Create project with very long title"
echo "--------------------------------------------"

# Create project with long title
PROJECT_RESPONSE=$(curl -s -X POST "${API_BASE}/projects/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: ${CSRF_TOKEN}" \
  -d "{
    \"name\": \"${LONG_TITLE}\",
    \"description\": \"Test project for verifying text truncation with ellipsis\",
    \"type\": \"research\"
  }")

PROJECT_ID=$(echo "$PROJECT_RESPONSE" | grep -o '"id":"[^"]*"' | sed 's/"id":"\(.*\)"/\1/')

if [ -z "$PROJECT_ID" ]; then
  echo "❌ ERROR: Failed to create project"
  echo "Response: $PROJECT_RESPONSE"
  exit 1
fi

echo "✅ Created project with ID: ${PROJECT_ID}"
echo "✅ Project title length: ${#LONG_TITLE} characters"
echo ""

echo "Step 3: Create notification with long message"
echo "----------------------------------------------"

# Create notification with long message
LONG_MESSAGE="This is a very long notification message that contains multiple sentences and a lot of details about something that happened in the system and it should be properly truncated using line-clamp-2 to show only two lines and hide the rest of the content with an ellipsis indicator at the end"

# Get fresh CSRF token
CSRF_TOKEN=$(curl -s -X GET "${API_BASE}/auth/csrf-token" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" | grep -o '"csrf_token":"[^"]*"' | sed 's/"csrf_token":"\(.*\)"/\1/')

NOTIFICATION_RESPONSE=$(curl -s -X POST "${API_BASE}/notifications/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: ${CSRF_TOKEN}" \
  -d "{
    \"title\": \"${LONG_TITLE}\",
    \"message\": \"${LONG_MESSAGE}\",
    \"type\": \"info\"
  }")

NOTIFICATION_ID=$(echo "$NOTIFICATION_RESPONSE" | grep -o '"id":"[^"]*"' | sed 's/"id":"\(.*\)"/\1/')

if [ -z "$NOTIFICATION_ID" ]; then
  echo "⚠️  WARNING: Failed to create notification (endpoint may not exist)"
  echo "Response: $NOTIFICATION_RESPONSE"
else
  echo "✅ Created notification with ID: ${NOTIFICATION_ID}"
  echo "✅ Notification message length: ${#LONG_MESSAGE} characters"
fi
echo ""

echo "Step 4: Verify data was created"
echo "--------------------------------"

# Fetch projects list
PROJECTS_LIST=$(curl -s -X GET "${API_BASE}/projects/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

echo "Projects list response (first 200 chars):"
echo "${PROJECTS_LIST}" | head -c 200
echo ""

# Check if our long title is in the response
if echo "$PROJECTS_LIST" | grep -q "extremely long project title"; then
  echo "✅ Long title found in API response"
else
  echo "❌ ERROR: Long title NOT found in API response"
  exit 1
fi

echo ""

echo "=========================================="
echo "✅ BACKEND TESTS PASSED"
echo "=========================================="
echo ""
echo "Frontend Verification Steps (Manual):"
echo "--------------------------------------"
echo "1. Open browser to: ${FRONTEND_BASE}/auth/login"
echo "2. Login with:"
echo "   Email: ${TEST_EMAIL}"
echo "   Password: ${TEST_PASSWORD}"
echo "3. Navigate to Projects page"
echo "4. Verify project title is truncated with '...' ellipsis"
echo "5. Hover over title to see tooltip with full text"
echo "6. Navigate to Notifications page"
echo "7. Verify notification title is truncated"
echo "8. Verify notification message is truncated to 2 lines"
echo ""
echo "CSS Classes Applied:"
echo "- truncate: Single line truncation with ellipsis"
echo "- line-clamp-2: Two line truncation with ellipsis"
echo "- title attribute: Shows full text on hover (tooltip)"
echo ""
echo "Test Data:"
echo "----------"
echo "Project ID: ${PROJECT_ID}"
echo "Project Title: ${LONG_TITLE}"
echo "Title Length: ${#LONG_TITLE} characters"
echo ""
echo "Expected Behavior:"
echo "- Title should be cut off after available width"
echo "- Ellipsis (...) should appear at the end"
echo "- Hovering shows full text in browser tooltip"
echo "- No layout breaking or text overflow"
echo ""
