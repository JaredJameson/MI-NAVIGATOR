#!/bin/bash

# Feature #153: Test user isolation (different users can have same titles)

set -e

API_URL="http://localhost:8000/api/v1"
TEST_USER1="isolation1_$(date +%s)@test.com"
TEST_USER2="isolation2_$(date +%s)@test.com"
TEST_PASSWORD="TestPass123!@#"

echo "========================================"
echo "Feature #153: User Isolation Test"
echo "========================================"
echo ""

# Create User 1
echo "Creating User 1..."
curl -s -X POST "${API_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_USER1}\",
    \"password\": \"${TEST_PASSWORD}\",
    \"confirm_password\": \"${TEST_PASSWORD}\",
    \"full_name\": \"User 1\",
    \"company\": \"Test Corp\"
  }" > /dev/null

LOGIN1=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${TEST_USER1}&password=${TEST_PASSWORD}")

TOKEN1=$(echo $LOGIN1 | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN1" ]; then
  echo "❌ Failed to get token for User 1"
  exit 1
fi

echo "✅ User 1 logged in"
echo ""

# Create User 2
echo "Creating User 2..."
curl -s -X POST "${API_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_USER2}\",
    \"password\": \"${TEST_PASSWORD}\",
    \"confirm_password\": \"${TEST_PASSWORD}\",
    \"full_name\": \"User 2\",
    \"company\": \"Test Corp\"
  }" > /dev/null

LOGIN2=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${TEST_USER2}&password=${TEST_PASSWORD}")

TOKEN2=$(echo $LOGIN2 | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN2" ]; then
  echo "❌ Failed to get token for User 2"
  exit 1
fi

echo "✅ User 2 logged in"
echo ""

# Create test CSV
cat > /tmp/test_isolation.csv << 'EOF'
title,type,company,summary,status
Shared Report Name,company_profile,Shared Corp,Test report,draft
EOF

# User 1 imports the file
echo "User 1 importing file..."
IMPORT1=$(curl -s -X POST "${API_URL}/reports/bulk-import" \
  -H "Authorization: Bearer ${TOKEN1}" \
  -F "file=@/tmp/test_isolation.csv")

IMPORT1_COUNT=$(echo $IMPORT1 | grep -o '"imported_count":[0-9]*' | cut -d':' -f2)

if [ "$IMPORT1_COUNT" != "1" ]; then
  echo "❌ User 1: Expected 1 import, got $IMPORT1_COUNT"
  exit 1
fi

echo "✅ User 1 imported 1 report"
echo ""

# User 2 imports the SAME file (should succeed - different user)
echo "User 2 importing same file..."
IMPORT2=$(curl -s -X POST "${API_URL}/reports/bulk-import" \
  -H "Authorization: Bearer ${TOKEN2}" \
  -F "file=@/tmp/test_isolation.csv")

IMPORT2_COUNT=$(echo $IMPORT2 | grep -o '"imported_count":[0-9]*' | cut -d':' -f2)
IMPORT2_SKIPPED=$(echo $IMPORT2 | grep -o '"skipped_count":[0-9]*' | cut -d':' -f2)

echo "User 2 Import Results:"
echo "  - Imported: $IMPORT2_COUNT"
echo "  - Skipped: $IMPORT2_SKIPPED"

if [ "$IMPORT2_COUNT" != "1" ]; then
  echo "❌ User 2: Expected 1 import (different user), got $IMPORT2_COUNT"
  exit 1
fi

if [ "$IMPORT2_SKIPPED" != "0" ]; then
  echo "❌ User 2: Expected 0 skipped (different user), got $IMPORT2_SKIPPED"
  exit 1
fi

echo "✅ User 2 imported 1 report (same title, different user)"
echo ""

# User 2 imports AGAIN (should be skipped - own duplicate)
echo "User 2 importing same file again..."
IMPORT3=$(curl -s -X POST "${API_URL}/reports/bulk-import" \
  -H "Authorization: Bearer ${TOKEN2}" \
  -F "file=@/tmp/test_isolation.csv")

IMPORT3_COUNT=$(echo $IMPORT3 | grep -o '"imported_count":[0-9]*' | cut -d':' -f2)
IMPORT3_SKIPPED=$(echo $IMPORT3 | grep -o '"skipped_count":[0-9]*' | cut -d':' -f2)

echo "User 2 Second Import Results:"
echo "  - Imported: $IMPORT3_COUNT"
echo "  - Skipped: $IMPORT3_SKIPPED"

if [ "$IMPORT3_COUNT" != "0" ]; then
  echo "❌ User 2: Expected 0 imports (own duplicate), got $IMPORT3_COUNT"
  exit 1
fi

if [ "$IMPORT3_SKIPPED" != "1" ]; then
  echo "❌ User 2: Expected 1 skipped (own duplicate), got $IMPORT3_SKIPPED"
  exit 1
fi

echo "✅ User 2's duplicate correctly skipped"
echo ""

# Cleanup
rm -f /tmp/test_isolation.csv

echo "========================================"
echo "✅ USER ISOLATION TEST PASSED!"
echo "========================================"
echo ""
echo "Summary:"
echo "  - User 1 imported: Shared Report Name ✅"
echo "  - User 2 imported: Shared Report Name ✅ (different user)"
echo "  - User 2 duplicate: Skipped ✅ (own duplicate)"
echo "  - User isolation working correctly ✅"
