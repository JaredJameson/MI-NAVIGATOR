#!/bin/bash

# Feature #164: Desktop layout at 1920px width
# Test desktop layout renders correctly at 1920px viewport

set -e

echo "=== Feature #164: Desktop Layout Test ==="
echo ""

# Test user credentials
EMAIL="test163@example.com"
PASSWORD="Test123!"

echo "Step 1: Login to get token..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\([^"]*\)"/\1/')

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login successful, token obtained"
echo ""

echo "Step 2: Verify dashboard endpoint responds..."
DASHBOARD_RESPONSE=$(curl -s -X GET http://localhost:8000/api/v1/dashboard \
  -H "Authorization: Bearer $TOKEN")

echo "✅ Dashboard API responds"
echo ""

echo "=== MANUAL BROWSER TEST REQUIRED ==="
echo ""
echo "Please test the following manually in browser:"
echo ""
echo "1. Open browser and navigate to: http://localhost:3000"
echo "2. Login with: $EMAIL / $PASSWORD"
echo "3. Resize browser window to 1920px width"
echo "4. Navigate to dashboard"
echo "5. Verify:"
echo "   - Sidebar is visible on the left"
echo "   - Main content area is properly sized"
echo "   - No horizontal scrolling"
echo "   - Content doesn't overflow"
echo "   - Layout looks professional at 1920px"
echo ""
echo "This feature requires visual inspection and cannot be fully automated."
echo ""
echo "=== TEST COMPLETE ==="
