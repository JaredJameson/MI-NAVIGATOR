#!/bin/bash

echo "=== Testing Feature #211: Usage Limit Enforcement (Analysis Endpoint) ==="
echo ""

# Login and get token
echo "1. Login as test user..."
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test330@example.com","password":"Test1234!"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "Token obtained: ${TOKEN:0:50}..."
echo ""

# Get CSRF token
echo "2. Get CSRF token..."
CSRF_TOKEN=$(curl -s http://127.0.0.1:8000/api/v1/csrf-token | grep -o '"csrf_token":"[^"]*"' | cut -d'"' -f4)
echo "CSRF token: ${CSRF_TOKEN:0:50}..."
echo ""

# Try first analysis (should succeed - 1/2)
echo "3. First analysis request (should succeed - 1/2 limit)..."
RESPONSE1=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST http://127.0.0.1:8000/api/v1/analysis \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"company_name":"Test Company 1","analysis_type":"basic"}')
HTTP_CODE1=$(echo "$RESPONSE1" | grep "HTTP_CODE:" | cut -d: -f2)
BODY1=$(echo "$RESPONSE1" | sed '/HTTP_CODE:/d')
echo "HTTP Code: $HTTP_CODE1"
echo "Response: ${BODY1:0:200}..."
echo ""

# Try second analysis (should succeed - 2/2)
echo "4. Second analysis request (should succeed - 2/2 limit)..."
RESPONSE2=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST http://127.0.0.1:8000/api/v1/analysis \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"company_name":"Test Company 2","analysis_type":"basic"}')
HTTP_CODE2=$(echo "$RESPONSE2" | grep "HTTP_CODE:" | cut -d: -f2)
BODY2=$(echo "$RESPONSE2" | sed '/HTTP_CODE:/d')
echo "HTTP Code: $HTTP_CODE2"
echo "Response: ${BODY2:0:200}..."
echo ""

# Try third analysis (should FAIL - exceeds limit)
echo "5. Third analysis request (should FAIL - exceeds 2/2 limit)..."
RESPONSE3=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST http://127.0.0.1:8000/api/v1/analysis \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"company_name":"Test Company 3","analysis_type":"basic"}')
HTTP_CODE3=$(echo "$RESPONSE3" | grep "HTTP_CODE:" | cut -d: -f2)
BODY3=$(echo "$RESPONSE3" | sed '/HTTP_CODE:/d')
echo "HTTP Code: $HTTP_CODE3"
echo "Response: $BODY3"
echo ""

# Verify results
echo "=== VERIFICATION ==="
if [ "$HTTP_CODE3" = "403" ] && echo "$BODY3" | grep -q "usage_limit_exceeded"; then
    echo "✅ SUCCESS: Usage limit enforcement working!"
    echo "✅ Third request blocked with HTTP 403"
    echo "✅ Error message contains 'usage_limit_exceeded'"
    echo "✅ Helpful error message provided to user"
else
    echo "❌ FAIL: Usage limit not properly enforced"
    echo "Expected HTTP 403 with 'usage_limit_exceeded' error"
    echo "Got HTTP $HTTP_CODE3"
fi

echo ""
echo "=== Test Complete ==="
