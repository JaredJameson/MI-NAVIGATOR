#!/bin/bash
# Simple test to verify report creation works

curl -s -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"quicktest@test.com","password":"Test123","confirm_password":"Test123","name":"Test"}' 2>&1

echo ""
echo "---"

curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=quicktest@test.com&password=Test123" 2>&1 | head -5
