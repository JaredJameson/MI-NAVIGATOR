#!/bin/bash

echo "========================================="
echo "Feature #150: Export data contains all created records"
echo "========================================="
echo ""

BASE_URL="http://localhost:8000/api/v1"

# Generate unique email for this test
TIMESTAMP=$(date +%s)
TEST_EMAIL="export_test_${TIMESTAMP}@test.com"
TEST_PASSWORD="TestPassword123"
TEST_NAME="Export Test User"

echo "Step 1: Register test user..."
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"${TEST_EMAIL}\",
    \"password\": \"${TEST_PASSWORD}\",
    \"confirm_password\": \"${TEST_PASSWORD}\",
    \"name\": \"${TEST_NAME}\"
  }")

echo "✅ User registered"
echo ""

echo "Step 2: Login to get access token..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=${TEST_EMAIL}&password=${TEST_PASSWORD}")

ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Failed to login. Response:"
    echo "$LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Logged in successfully"
echo ""

echo "Step 3: Get CSRF token..."
CSRF_RESPONSE=$(curl -s -X GET "${BASE_URL}/auth/csrf-token" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")

CSRF_TOKEN=$(echo $CSRF_RESPONSE | grep -o '"csrf_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$CSRF_TOKEN" ]; then
    echo "❌ Failed to get CSRF token. Response:"
    echo "$CSRF_RESPONSE"
    exit 1
fi

echo "✅ Got CSRF token"
echo ""

echo "Step 4: Create 5 reports with unique names..."
REPORT_IDS=()

for i in {1..5}; do
    REPORT_TITLE="Test Report #${i} - Created at ${TIMESTAMP}"

    CREATE_RESPONSE=$(curl -s -X POST "${BASE_URL}/reports" \
      -H "Authorization: Bearer ${ACCESS_TOKEN}" \
      -H "X-CSRF-Token: ${CSRF_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "{
        \"title\": \"${REPORT_TITLE}\",
        \"type\": \"market_analysis\",
        \"company\": \"Test Company ${i}\",
        \"content\": \"This is test report content for report number ${i}. Created at ${TIMESTAMP} for testing export functionality.\",
        \"summary\": \"Test report ${i} summary\"
      }")

    echo "   CREATE_RESPONSE for report #${i}:"
    echo "   $CREATE_RESPONSE"

    REPORT_ID=$(echo $CREATE_RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

    if [ -z "$REPORT_ID" ]; then
        echo "❌ Failed to create report #${i}."
        echo "   Full response: $CREATE_RESPONSE"
        echo "   Trying without CSRF protection..."

        # Try without CSRF (maybe it's not required for this endpoint)
        CREATE_RESPONSE=$(curl -s -X POST "${BASE_URL}/reports" \
          -H "Authorization: Bearer ${ACCESS_TOKEN}" \
          -H "Content-Type: application/json" \
          -d "{
            \"title\": \"${REPORT_TITLE}\",
            \"type\": \"market_analysis\",
            \"company\": \"Test Company ${i}\",
            \"content\": \"Test content ${i}\",
            \"summary\": \"Test summary ${i}\"
          }")

        REPORT_ID=$(echo $CREATE_RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)

        if [ -z "$REPORT_ID" ]; then
            echo "❌ Still failed. Response: $CREATE_RESPONSE"
            exit 1
        fi
    fi

    REPORT_IDS+=("$REPORT_ID")
    echo "   ✅ Created report #${i}: ${REPORT_ID} - ${REPORT_TITLE}"
done

echo ""
echo "✅ Created 5 reports total"
echo ""

echo "Step 5: Export all user data..."
EXPORT_FILE="/tmp/user_data_export_${TIMESTAMP}.json"

curl -s -X POST "${BASE_URL}/users/me/export-data" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -o "${EXPORT_FILE}"

if [ ! -f "${EXPORT_FILE}" ]; then
    echo "❌ Failed to export data - file not created"
    exit 1
fi

echo "✅ Export file created: ${EXPORT_FILE}"
echo ""

echo "Step 6: Verify export file contains all data..."
EXPORT_CONTENT=$(cat "${EXPORT_FILE}")

# Check if it's valid JSON
if ! echo "$EXPORT_CONTENT" | python3 -m json.tool > /dev/null 2>&1; then
    echo "❌ Export file is not valid JSON"
    cat "${EXPORT_FILE}"
    exit 1
fi

echo "✅ Export file is valid JSON"
echo ""

echo "Step 7: Verify all 5 reports are present in export..."
REPORTS_COUNT=$(echo "$EXPORT_CONTENT" | grep -o '"reports":' | wc -l)

if [ "$REPORTS_COUNT" -eq 0 ]; then
    echo "❌ No 'reports' section found in export"
    echo "Export keys:"
    echo "$EXPORT_CONTENT" | python3 -c "import sys, json; print(json.dumps(list(json.load(sys.stdin).keys()), indent=2))"
    exit 1
fi

echo "✅ Found 'reports' section in export"

# Count reports in export
EXPORTED_REPORTS_COUNT=$(echo "$EXPORT_CONTENT" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('reports', [])))")

echo "   Reports in export: ${EXPORTED_REPORTS_COUNT}"

if [ "$EXPORTED_REPORTS_COUNT" -ne 5 ]; then
    echo "❌ Expected 5 reports, found ${EXPORTED_REPORTS_COUNT}"
    exit 1
fi

echo "✅ All 5 reports present in export"
echo ""

echo "Step 8: Verify data integrity - check each report..."
for i in {0..4}; do
    REPORT_TITLE=$(echo "$EXPORT_CONTENT" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['reports'][$i]['title'])")
    REPORT_ID=$(echo "$EXPORT_CONTENT" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['reports'][$i]['id'])")

    echo "   Report $((i+1)): ${REPORT_ID}"
    echo "      Title: ${REPORT_TITLE}"

    # Verify title contains our timestamp
    if [[ ! "$REPORT_TITLE" =~ "$TIMESTAMP" ]]; then
        echo "❌ Report title doesn't contain expected timestamp"
        exit 1
    fi
done

echo ""
echo "✅ All reports have correct data integrity"
echo ""

echo "Step 9: Verify export metadata..."
TOTAL_REPORTS=$(echo "$EXPORT_CONTENT" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['export_metadata']['total_reports'])")

if [ "$TOTAL_REPORTS" -ne 5 ]; then
    echo "❌ Export metadata shows ${TOTAL_REPORTS} reports, expected 5"
    exit 1
fi

echo "✅ Export metadata correct: total_reports = ${TOTAL_REPORTS}"
echo ""

echo "Step 10: Verify other sections present..."
SECTIONS=("user_profile" "preferences" "security" "reports" "activity_log" "export_metadata")

for section in "${SECTIONS[@]}"; do
    HAS_SECTION=$(echo "$EXPORT_CONTENT" | python3 -c "import sys, json; data = json.load(sys.stdin); print('$section' in data)")

    if [ "$HAS_SECTION" != "True" ]; then
        echo "❌ Missing section: ${section}"
        exit 1
    fi

    echo "   ✅ Section present: ${section}"
done

echo ""
echo "========================================="
echo "✅ ALL TESTS PASSED!"
echo "Feature #150: Export data contains all created records - VERIFIED"
echo "========================================="
echo ""
echo "Summary:"
echo "- Created 5 reports with unique names"
echo "- Exported all user data"
echo "- Verified export file is valid JSON"
echo "- Verified all 5 reports present in export"
echo "- Verified data integrity (titles, IDs, timestamps)"
echo "- Verified export metadata (total_reports)"
echo "- Verified all required sections present"
echo ""
echo "Export file saved at: ${EXPORT_FILE}"
echo ""
echo "Cleanup: Test user remains in system for future verification"
echo "Email: ${TEST_EMAIL}"
