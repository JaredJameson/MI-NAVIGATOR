#!/bin/bash

# Feature #153: Test case-insensitive duplicate detection

set -e

API_URL="http://localhost:8000/api/v1"
TEST_USER="casetest_$(date +%s)@test.com"
TEST_PASSWORD="TestPass123!@#"

echo "========================================"
echo "Feature #153: Case-Insensitive Test"
echo "========================================"
echo ""

# Create test user and login
echo "Creating test user and logging in..."
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_USER}\",
    \"password\": \"${TEST_PASSWORD}\",
    \"confirm_password\": \"${TEST_PASSWORD}\",
    \"full_name\": \"Case Test User\",
    \"company\": \"Test Corp\"
  }")

LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${TEST_USER}&password=${TEST_PASSWORD}")

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Failed to get access token"
  exit 1
fi

echo "✅ Logged in successfully"
echo ""

# Create first CSV with lowercase
echo "Creating CSV with lowercase title..."
cat > /tmp/test_case_lower.csv << 'EOF'
title,type,company,summary,status
test report delta,company_profile,Delta Corp,Test report,draft
EOF

# Import lowercase version
echo "Importing lowercase version..."
IMPORT1=$(curl -s -X POST "${API_URL}/reports/bulk-import" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -F "file=@/tmp/test_case_lower.csv")

IMPORT1_COUNT=$(echo $IMPORT1 | grep -o '"imported_count":[0-9]*' | cut -d':' -f2)

if [ "$IMPORT1_COUNT" != "1" ]; then
  echo "❌ Expected 1 import, got $IMPORT1_COUNT"
  exit 1
fi

echo "✅ Lowercase version imported"
echo ""

# Create second CSV with UPPERCASE
echo "Creating CSV with UPPERCASE title..."
cat > /tmp/test_case_upper.csv << 'EOF'
title,type,company,summary,status
TEST REPORT DELTA,company_profile,DELTA CORP,Test report,draft
EOF

# Try to import UPPERCASE version (should be detected as duplicate)
echo "Importing UPPERCASE version (should be skipped as duplicate)..."
IMPORT2=$(curl -s -X POST "${API_URL}/reports/bulk-import" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -F "file=@/tmp/test_case_upper.csv")

IMPORT2_COUNT=$(echo $IMPORT2 | grep -o '"imported_count":[0-9]*' | cut -d':' -f2)
IMPORT2_SKIPPED=$(echo $IMPORT2 | grep -o '"skipped_count":[0-9]*' | cut -d':' -f2)

echo "Import 2 Results:"
echo "  - Imported: $IMPORT2_COUNT"
echo "  - Skipped: $IMPORT2_SKIPPED"

if [ "$IMPORT2_COUNT" != "0" ]; then
  echo "❌ Expected 0 imports (duplicate), got $IMPORT2_COUNT"
  exit 1
fi

if [ "$IMPORT2_SKIPPED" != "1" ]; then
  echo "❌ Expected 1 skipped (duplicate), got $IMPORT2_SKIPPED"
  exit 1
fi

echo "✅ UPPERCASE version correctly detected as duplicate"
echo ""

# Cleanup
rm -f /tmp/test_case_lower.csv /tmp/test_case_upper.csv

echo "========================================"
echo "✅ CASE-INSENSITIVE TEST PASSED!"
echo "========================================"
