#!/bin/bash
# Test Feature #139: Dropdown selection persists
# This script tests that dropdown selections are saved and loaded correctly

API_BASE="http://localhost:8000/api/v1"

echo "=================================="
echo "Feature #139: Dropdown Persistence Test"
echo "=================================="
echo ""

# Step 1: Register a test user for this feature
echo "Step 1: Creating test user..."
TEST_EMAIL="test_feature_139_$(date +%s)@example.com"
TEST_PASSWORD="TestPass123!"

REGISTER_RESPONSE=$(curl -s -X POST "${API_BASE}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'$TEST_EMAIL'",
    "password": "'$TEST_PASSWORD'",
    "confirm_password": "'$TEST_PASSWORD'",
    "name": "Feature 139 Tester"
  }')

echo "Register response: $REGISTER_RESPONSE"
echo ""

# Step 1b: Login to get token
echo "Step 1b: Logging in to get token..."
LOGIN_RESPONSE=$(curl -s -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$TEST_EMAIL&password=$TEST_PASSWORD")

echo "Login response: $LOGIN_RESPONSE"
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get auth token"
  exit 1
fi

echo "✅ Test user created and logged in, token obtained"
echo ""

# Step 2: Get CSRF token
echo "Step 2: Getting CSRF token..."
CSRF_RESPONSE=$(curl -s "${API_BASE}/auth/csrf-token")
CSRF_TOKEN=$(echo $CSRF_RESPONSE | grep -o '"csrf_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$CSRF_TOKEN" ]; then
  echo "❌ Failed to get CSRF token"
  exit 1
fi

echo "✅ CSRF token obtained"
echo ""

# Step 3: Save dropdown selections
echo "Step 3: Saving dropdown selections..."
echo "  - Industry: technology"
echo "  - User Role: analyst"
echo "  - Language: en"
echo "  - Depth: deep"
echo "  - Format: docx"
echo "  - Currency: EUR"
echo "  - Timezone: Europe/London"
echo ""

# Save profile (industry, user_role)
PROFILE_SAVE=$(curl -s -X PUT "${API_BASE}/users/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -d '{
    "name": "Feature 139 Tester",
    "industry": "technology",
    "user_role": "analyst"
  }')

echo "Profile save response:"
echo "$PROFILE_SAVE" | head -c 500
echo ""

# Save preferences (language, depth, format, currency, timezone)
PREFS_SAVE=$(curl -s -X PUT "${API_BASE}/users/me/preferences" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -d '{
    "preferred_language": "en",
    "preferred_depth": "deep",
    "preferred_format": "docx",
    "preferred_currency": "EUR",
    "timezone": "Europe/London"
  }')

echo "Preferences save response:"
echo "$PREFS_SAVE"
echo ""

# Step 4: "Reopen form" - fetch profile again
echo "Step 4: Fetching profile to verify persistence..."
PROFILE_LOAD=$(curl -s "${API_BASE}/users/me" \
  -H "Authorization: Bearer $TOKEN")

echo "Profile load response:"
echo "$PROFILE_LOAD"
echo ""

# Step 5: Verify all selections are preserved
echo "Step 5: Verifying dropdown selections..."
echo ""

# Check industry
if echo "$PROFILE_LOAD" | grep -q '"industry":"technology"'; then
  echo "✅ Industry: technology (correct)"
else
  echo "❌ Industry: NOT preserved"
  exit 1
fi

# Check user_role
if echo "$PROFILE_LOAD" | grep -q '"user_role":"analyst"'; then
  echo "✅ User Role: analyst (correct)"
else
  echo "❌ User Role: NOT preserved"
  exit 1
fi

# Check language
if echo "$PROFILE_LOAD" | grep -q '"preferred_language":"en"'; then
  echo "✅ Language: en (correct)"
else
  echo "❌ Language: NOT preserved"
  exit 1
fi

# Check depth
if echo "$PROFILE_LOAD" | grep -q '"preferred_depth":"deep"'; then
  echo "✅ Depth: deep (correct)"
else
  echo "❌ Depth: NOT preserved"
  exit 1
fi

# Check format
if echo "$PROFILE_LOAD" | grep -q '"preferred_format":"docx"'; then
  echo "✅ Format: docx (correct)"
else
  echo "❌ Format: NOT preserved"
  exit 1
fi

# Check currency (THE BUG WE FIXED!)
if echo "$PROFILE_LOAD" | grep -q '"preferred_currency":"EUR"'; then
  echo "✅ Currency: EUR (correct) - BUG FIX VERIFIED!"
else
  echo "❌ Currency: NOT preserved - THIS WAS THE BUG!"
  exit 1
fi

# Check timezone
if echo "$PROFILE_LOAD" | grep -q '"timezone":"Europe/London"'; then
  echo "✅ Timezone: Europe/London (correct)"
else
  echo "❌ Timezone: NOT preserved"
  exit 1
fi

echo ""
echo "=================================="
echo "✅ ALL TESTS PASSED!"
echo "Feature #139: Dropdown selection persists - VERIFIED"
echo "=================================="
