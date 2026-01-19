#!/bin/bash
# Create test user without 2FA for Feature #155 testing

DB_PATH="mi_navigator.db"

# Generate UUID for user
USER_ID=$(cat /proc/sys/kernel/random/uuid 2>/dev/null || echo "test-user-155-$(date +%s)")

# Hash for password "Test123!" - this is bcrypt hash
# We'll use the backend to generate it properly
echo "Creating test user for Feature #155..."

# Use curl to register a new user if registration endpoint exists
REGISTER_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"test155@example.com\",
    \"password\": \"Test123!\",
    \"name\": \"Test User 155\"
  }")

echo "$REGISTER_RESPONSE"

# If registration succeeded, login
if echo "$REGISTER_RESPONSE" | grep -q "id"; then
  echo "✅ User created successfully"

  # Try to login
  LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=test155@example.com&password=Test123!")

  echo "Login response:"
  echo "$LOGIN_RESPONSE"

  TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

  if [ -n "$TOKEN" ]; then
    echo "✅ Login successful - token obtained"
    echo "TOKEN: $TOKEN"
    exit 0
  else
    echo "⚠️ Registration succeeded but login failed"
    exit 1
  fi
else
  echo "❌ Registration failed or endpoint doesn't exist"
  echo "Will try alternative method..."
  exit 1
fi
