#!/bin/bash

echo "=== Testing Feature #211: Usage Limit Enforcement ==="
echo ""

# Login and get token
echo "1. Login as test user..."
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test330@example.com","password":"Test1234!"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "Token obtained: ${TOKEN:0:50}..."
echo ""

# Try sending first message (should succeed - 1/2)
echo "2. Sending first message (should succeed - 1/2 limit)..."
RESPONSE1=$(curl -s -X POST http://127.0.0.1:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Test message 1","conversation_id":"test-conv-1"}')
echo "Response 1: $RESPONSE1"
echo ""

# Try sending second message (should succeed - 2/2)
echo "3. Sending second message (should succeed - 2/2 limit)..."
RESPONSE2=$(curl -s -X POST http://127.0.0.1:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Test message 2","conversation_id":"test-conv-1"}')
echo "Response 2: $RESPONSE2"
echo ""

# Try sending third message (should FAIL - exceeds limit)
echo "4. Sending third message (should FAIL - exceeds 2/2 limit)..."
RESPONSE3=$(curl -s -X POST http://127.0.0.1:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Test message 3","conversation_id":"test-conv-1"}')
echo "Response 3: $RESPONSE3"
echo ""

# Check if response contains error
if echo "$RESPONSE3" | grep -q "usage_limit_exceeded"; then
    echo "✅ SUCCESS: Usage limit enforcement working!"
    echo "✅ Error message contains 'usage_limit_exceeded'"
else
    echo "❌ FAIL: Usage limit not enforced"
fi

echo ""
echo "=== Test Complete ==="
