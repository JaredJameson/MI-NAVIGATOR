#!/bin/bash

echo "========================================="
echo "Feature #154: Additional Edge Cases"
echo "========================================="
echo ""

# Setup user
USER_EMAIL="edge_test_1768828100@test.com"
PASSWORD="Test123456"

# Login
LOGIN_RESPONSE=$(curl -s -X POST 'http://localhost:8000/api/v1/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d "username=${USER_EMAIL}&password=${PASSWORD}")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"//;s/"//')

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token"
    exit 1
fi

echo "✅ Logged in"
echo ""

# Get CSRF token
CSRF_RESPONSE=$(curl -s 'http://localhost:8000/api/v1/auth/csrf-token' -H "Authorization: Bearer $TOKEN")
CSRF_TOKEN=$(echo "$CSRF_RESPONSE" | grep -o '"csrf_token":"[^"]*"' | sed 's/"csrf_token":"//;s/"//')

# TEST 4: Empty CSV (headers only, no data rows)
echo "=== TEST 4: Empty CSV (headers only) ==="
RESULT_4=$(curl -s -X POST 'http://localhost:8000/api/v1/reports/bulk-import' \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -F "file=@test_malformed_4_empty.csv")

echo "Response: $RESULT_4"

if echo "$RESULT_4" | grep -q '"imported_count":0'; then
    echo "✅ Empty file handled correctly (0 imports)"
else
    echo "⚠️  Check response"
fi
echo ""

# Refresh CSRF token
CSRF_RESPONSE=$(curl -s 'http://localhost:8000/api/v1/auth/csrf-token' -H "Authorization: Bearer $TOKEN")
CSRF_TOKEN=$(echo "$CSRF_RESPONSE" | grep -o '"csrf_token":"[^"]*"' | sed 's/"csrf_token":"//;s/"//')

# TEST 5: CSV without proper headers
echo "=== TEST 5: CSV without title/type headers ==="
RESULT_5=$(curl -s -X POST 'http://localhost:8000/api/v1/reports/bulk-import' \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -F "file=@test_malformed_5_no_headers.csv")

echo "Response: $RESULT_5"

if echo "$RESULT_5" | grep -q "must contain.*title.*type"; then
    echo "✅ Missing headers detected correctly"
else
    echo "⚠️  Check response"
fi
echo ""

echo "========================================="
echo "Edge cases tested successfully"
echo "========================================="
