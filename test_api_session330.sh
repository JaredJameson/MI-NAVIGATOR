#!/bin/bash

echo "=== Testing Backend API ==="

# Test health
echo "1. Health check:"
curl -s http://127.0.0.1:8000/health
echo ""

# Test registration
echo "2. Register new user:"
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"apitest330@example.com","password":"Test1234!","confirm_password":"Test1234!","name":"API Test 330"}'
echo ""

# Test login
echo "3. Login:"
RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"apitest330@example.com","password":"Test1234!"}')
echo "$RESPONSE"

# Extract token
TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "Token: $TOKEN"
echo ""

# Test authenticated endpoint
echo "4. Get user profile with token:"
curl -s http://127.0.0.1:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
echo ""
