#!/bin/bash
# Feature #140 - Multi-select works correctly - Complete Test Script
# Tests all 5 steps through API calls

set -e

API="http://localhost:8000/api/v1"
EMAIL="multiselect_test_1768820333@test.com"
PASSWORD="Test1234!"

echo "=========================================="
echo "Feature #140: Multi-select Test"
echo "=========================================="
echo ""

# Step 0: Login
echo "=== Step 0: Login ==="
LOGIN_RESPONSE=$(curl -s -X POST "${API}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${EMAIL}&password=${PASSWORD}")

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "ERROR: Failed to login"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login successful"
echo "Token: ${ACCESS_TOKEN:0:30}..."
echo ""

# Get CSRF token
CSRF_TOKEN=$(curl -s "${API}/auth/csrf" | grep -o '"csrf_token":"[^"]*"' | cut -d'"' -f4)
echo "CSRF Token: ${CSRF_TOKEN:0:30}..."
echo ""

# Step 1: Create multiselect field definition (simulates "Navigate to form with multi-select")
echo "=== Step 1: Create multiselect custom field definition ==="
FIELD_RESPONSE=$(curl -s -X POST "${API}/custom-fields/definitions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -d '{
    "name": "Product Categories TEST_140",
    "field_type": "multiselect",
    "description": "Test multiselect field for Feature #140",
    "is_required": false,
    "options": ["Software", "Hardware", "Services", "Consulting", "Training"]
  }')

echo "$FIELD_RESPONSE"
FIELD_ID=$(echo "$FIELD_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$FIELD_ID" ]; then
  echo "ERROR: Failed to create field"
  exit 1
fi

echo "✅ Multiselect field created"
echo "Field ID: $FIELD_ID"
echo ""

# Step 2-3: Select multiple options and verify
echo "=== Step 2-3: Select multiple options ==="
COMPANY_ID="test_company_140"

# Save multi-select values
SET_VALUE_RESPONSE=$(curl -s -X POST "${API}/custom-fields/values/${COMPANY_ID}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -d "{
    \"field_definition_id\": \"$FIELD_ID\",
    \"value\": null,
    \"value_json\": [\"Software\", \"Hardware\", \"Services\"]
  }")

echo "$SET_VALUE_RESPONSE"

# Verify value was saved
echo ""
echo "=== Verifying values were saved ==="
GET_VALUES_RESPONSE=$(curl -s -X GET "${API}/custom-fields/values/${COMPANY_ID}" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$GET_VALUES_RESPONSE"

# Check if our field has the right values
if echo "$GET_VALUES_RESPONSE" | grep -q "Software" && \
   echo "$GET_VALUES_RESPONSE" | grep -q "Hardware" && \
   echo "$GET_VALUES_RESPONSE" | grep -q "Services"; then
  echo "✅ All 3 selections visible in response"
else
  echo "❌ ERROR: Not all selections found"
  exit 1
fi
echo ""

# Step 4: Remove one selection
echo "=== Step 4: Remove one selection (Hardware) ==="
UPDATE_VALUE_RESPONSE=$(curl -s -X POST "${API}/custom-fields/values/${COMPANY_ID}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -d "{
    \"field_definition_id\": \"$FIELD_ID\",
    \"value\": null,
    \"value_json\": [\"Software\", \"Services\"]
  }")

echo "$UPDATE_VALUE_RESPONSE"

# Verify Hardware was removed
echo ""
echo "=== Verifying Hardware was removed ==="
GET_VALUES_RESPONSE2=$(curl -s -X GET "${API}/custom-fields/values/${COMPANY_ID}" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$GET_VALUES_RESPONSE2"

if echo "$GET_VALUES_RESPONSE2" | grep -q "Hardware"; then
  echo "❌ ERROR: Hardware still present (should be removed)"
  exit 1
else
  echo "✅ Hardware successfully removed"
fi

if echo "$GET_VALUES_RESPONSE2" | grep -q "Software" && \
   echo "$GET_VALUES_RESPONSE2" | grep -q "Services"; then
  echo "✅ Software and Services still present"
else
  echo "❌ ERROR: Software or Services missing"
  exit 1
fi
echo ""

# Step 5: Verify persistence (reload data)
echo "=== Step 5: Verify persistence (reload) ==="
sleep 1  # Small delay to simulate page reload

GET_VALUES_RESPONSE3=$(curl -s -X GET "${API}/custom-fields/values/${COMPANY_ID}" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$GET_VALUES_RESPONSE3"

if echo "$GET_VALUES_RESPONSE3" | grep -q "Software" && \
   echo "$GET_VALUES_RESPONSE3" | grep -q "Services" && \
   ! echo "$GET_VALUES_RESPONSE3" | grep -q "Hardware"; then
  echo "✅ Data persisted correctly after reload"
else
  echo "❌ ERROR: Data persistence failed"
  exit 1
fi
echo ""

echo "=========================================="
echo "✅ ALL TESTS PASSED!"
echo "Feature #140: Multi-select works correctly - VERIFIED"
echo "=========================================="
echo ""
echo "Test Summary:"
echo "✅ Step 1: Navigate to form with multi-select"
echo "✅ Step 2: Select multiple options"
echo "✅ Step 3: Verify all selections visible"
echo "✅ Step 4: Remove one selection"
echo "✅ Step 5: Save and verify all selections saved"
echo ""
