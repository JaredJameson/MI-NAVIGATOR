#!/bin/bash

# Feature #153: Import duplicate handling test
# Tests how bulk import handles duplicate entries

set -e

API_URL="http://localhost:8000/api/v1"
TEST_USER="duptest_$(date +%s)@test.com"
TEST_PASSWORD="TestPass123!@#"

echo "========================================"
echo "Feature #153: Import Duplicate Handling"
echo "========================================"
echo ""

# Step 0: Create test user and login
echo "Step 0: Creating test user and logging in..."
REGISTER_RESPONSE=$(curl -s -X POST "${API_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_USER}\",
    \"password\": \"${TEST_PASSWORD}\",
    \"confirm_password\": \"${TEST_PASSWORD}\",
    \"full_name\": \"Duplicate Test User\",
    \"company\": \"Test Corp\"
  }")

echo "Register response: $REGISTER_RESPONSE"

# Login
LOGIN_RESPONSE=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${TEST_USER}&password=${TEST_PASSWORD}")

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Failed to get access token"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Logged in successfully"
echo ""

# Create test CSV file with data set A
echo "Creating test CSV file (data set A)..."
cat > /tmp/test_dataset_a.csv << 'EOF'
title,type,company,summary,status
Test Report Alpha,company_profile,ACME Corp,First test report,draft
Test Report Beta,market_analysis,Beta Inc,Second test report,in_progress
Test Report Gamma,due_diligence,Gamma LLC,Third test report,completed
EOF

echo "✅ Test CSV created"
echo ""

# Step 1: Import data set A
echo "========================================"
echo "Step 1: Import data set A (first time)"
echo "========================================"

IMPORT1_RESPONSE=$(curl -s -X POST "${API_URL}/reports/bulk-import" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -F "file=@/tmp/test_dataset_a.csv")

echo "Import 1 response:"
echo "$IMPORT1_RESPONSE" | python3 -m json.tool

IMPORT1_COUNT=$(echo $IMPORT1_RESPONSE | grep -o '"imported_count":[0-9]*' | cut -d':' -f2)
IMPORT1_SKIPPED=$(echo $IMPORT1_RESPONSE | grep -o '"skipped_count":[0-9]*' | cut -d':' -f2)

echo ""
echo "Import 1 Results:"
echo "  - Imported: $IMPORT1_COUNT reports"
echo "  - Skipped: $IMPORT1_SKIPPED duplicates"

if [ "$IMPORT1_COUNT" != "3" ]; then
  echo "❌ Expected 3 imports, got $IMPORT1_COUNT"
  exit 1
fi

if [ "$IMPORT1_SKIPPED" != "0" ]; then
  echo "❌ Expected 0 skipped on first import, got $IMPORT1_SKIPPED"
  exit 1
fi

echo "✅ Step 1 PASSED: First import created 3 reports"
echo ""

# Step 2: Import data set A again (should detect duplicates)
echo "========================================"
echo "Step 2: Import data set A again"
echo "========================================"

sleep 1  # Brief pause

IMPORT2_RESPONSE=$(curl -s -X POST "${API_URL}/reports/bulk-import" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -F "file=@/tmp/test_dataset_a.csv")

echo "Import 2 response:"
echo "$IMPORT2_RESPONSE" | python3 -m json.tool

IMPORT2_COUNT=$(echo $IMPORT2_RESPONSE | grep -o '"imported_count":[0-9]*' | cut -d':' -f2)
IMPORT2_SKIPPED=$(echo $IMPORT2_RESPONSE | grep -o '"skipped_count":[0-9]*' | cut -d':' -f2)
IMPORT2_TOTAL=$(echo $IMPORT2_RESPONSE | grep -o '"total_rows":[0-9]*' | cut -d':' -f2)

echo ""
echo "Import 2 Results:"
echo "  - Total rows: $IMPORT2_TOTAL"
echo "  - Imported: $IMPORT2_COUNT reports"
echo "  - Skipped: $IMPORT2_SKIPPED duplicates"

# Step 3: Verify duplicate handling (all should be skipped)
echo ""
echo "========================================"
echo "Step 3: Verify duplicate handling"
echo "========================================"

if [ "$IMPORT2_COUNT" != "0" ]; then
  echo "❌ Expected 0 new imports (all duplicates), got $IMPORT2_COUNT"
  exit 1
fi

if [ "$IMPORT2_SKIPPED" != "3" ]; then
  echo "❌ Expected 3 skipped duplicates, got $IMPORT2_SKIPPED"
  exit 1
fi

echo "✅ Step 3 PASSED: All 3 duplicates correctly skipped"
echo ""

# Step 4: Verify no unintended duplicates in database
echo "========================================"
echo "Step 4: Verify no unintended duplicates"
echo "========================================"

# Get all reports for this user
REPORTS_RESPONSE=$(curl -s -X GET "${API_URL}/reports/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

# Count reports with our test titles
ALPHA_COUNT=$(echo "$REPORTS_RESPONSE" | grep -o '"title":"Test Report Alpha"' | wc -l)
BETA_COUNT=$(echo "$REPORTS_RESPONSE" | grep -o '"title":"Test Report Beta"' | wc -l)
GAMMA_COUNT=$(echo "$REPORTS_RESPONSE" | grep -o '"title":"Test Report Gamma"' | wc -l)

echo "Report counts in database:"
echo "  - Test Report Alpha: $ALPHA_COUNT (expected: 1)"
echo "  - Test Report Beta: $BETA_COUNT (expected: 1)"
echo "  - Test Report Gamma: $GAMMA_COUNT (expected: 1)"

if [ "$ALPHA_COUNT" != "1" ] || [ "$BETA_COUNT" != "1" ] || [ "$GAMMA_COUNT" != "1" ]; then
  echo "❌ Found unintended duplicates in database!"
  exit 1
fi

echo "✅ Step 4 PASSED: No unintended duplicates found"
echo ""

# Cleanup
rm -f /tmp/test_dataset_a.csv

echo "========================================"
echo "✅ ALL TESTS PASSED!"
echo "Feature #153: Import duplicate handling - VERIFIED"
echo "========================================"
echo ""
echo "Summary:"
echo "  - First import: 3 reports created ✅"
echo "  - Second import: 3 duplicates skipped ✅"
echo "  - No unintended duplicates in database ✅"
echo "  - Duplicate detection strategy: SKIP ✅"
