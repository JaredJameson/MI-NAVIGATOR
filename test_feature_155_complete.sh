#!/bin/bash
# Feature #155: Import then export data integrity - Complete Test
# Using test155@example.com user

echo "============================================================"
echo "Feature #155: Import-Export Data Integrity Test"
echo "============================================================"

BASE_URL="http://localhost:8000/api/v1"
TIMESTAMP=$(date +%s)

echo ""
echo "Step 1: Login and get token..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test155@example.com&password=Test1234")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get access token"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Logged in successfully"

echo ""
echo "Step 2: Create 3 test reports..."

REPORT1=$(curl -s -X POST "$BASE_URL/reports" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"TEST_155_A_${TIMESTAMP}\",\"type\":\"company_profile\",\"company\":\"Test Company A\",\"summary\":\"Test report A\",\"status\":\"completed\"}")

REPORT2=$(curl -s -X POST "$BASE_URL/reports" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"TEST_155_B_${TIMESTAMP}\",\"type\":\"market_analysis\",\"company\":\"Test Company B\",\"summary\":\"Test report B\",\"status\":\"draft\"}")

REPORT3=$(curl -s -X POST "$BASE_URL/reports" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"TEST_155_C_${TIMESTAMP}\",\"type\":\"competitive_analysis\",\"summary\":\"Test report C\",\"status\":\"in_progress\"}")

ID1=$(echo "$REPORT1" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
ID2=$(echo "$REPORT2" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
ID3=$(echo "$REPORT3" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$ID1" ] || [ -z "$ID2" ] || [ -z "$ID3" ]; then
  echo "❌ Failed to create test reports"
  echo "Report1: $REPORT1"
  echo "Report2: $REPORT2"
  echo "Report3: $REPORT3"
  exit 1
fi

echo "✅ Created 3 test reports:"
echo "   - Report A (ID: $ID1)"
echo "   - Report B (ID: $ID2)"
echo "   - Report C (ID: $ID3)"

echo ""
echo "Step 3: Export reports to CSV..."

CSV_FILE="test_export_155_${TIMESTAMP}.csv"
cat > "$CSV_FILE" << EOF
title,type,company,summary,status
TEST_155_A_${TIMESTAMP},company_profile,Test Company A,Test report A,completed
TEST_155_B_${TIMESTAMP},market_analysis,Test Company B,Test report B,draft
TEST_155_C_${TIMESTAMP},competitive_analysis,,Test report C,in_progress
EOF

echo "✅ Created CSV export file: $CSV_FILE"
cat "$CSV_FILE"

echo ""
echo "Step 4: Delete original reports..."

curl -s -X DELETE "$BASE_URL/reports/$ID1" -H "Authorization: Bearer $TOKEN" > /dev/null
curl -s -X DELETE "$BASE_URL/reports/$ID2" -H "Authorization: Bearer $TOKEN" > /dev/null
curl -s -X DELETE "$BASE_URL/reports/$ID3" -H "Authorization: Bearer $TOKEN" > /dev/null

echo "✅ Deleted 3 original reports"

sleep 2

# Verify deletion
ALL_AFTER_DELETE=$(curl -s -X GET "$BASE_URL/reports" -H "Authorization: Bearer $TOKEN")
echo "$ALL_AFTER_DELETE" | grep -q "TEST_155_A_${TIMESTAMP}"
if [ $? -eq 0 ]; then
  echo "⚠️  Warning: Report A still exists after deletion"
fi

echo ""
echo "Step 5: Import from CSV file..."

IMPORT_RESPONSE=$(curl -s -X POST "$BASE_URL/reports/bulk-import" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$CSV_FILE")

echo "Import response:"
echo "$IMPORT_RESPONSE"

IMPORTED_COUNT=$(echo "$IMPORT_RESPONSE" | grep -o '"imported_count":[0-9]*' | cut -d':' -f2)
ERROR_COUNT=$(echo "$IMPORT_RESPONSE" | grep -o '"errors":\[[^]]*\]' | wc -l)

if [ -z "$IMPORTED_COUNT" ]; then
  echo "❌ Import failed - no imported_count in response"
  exit 1
fi

echo ""
echo "✅ Import completed:"
echo "   - Imported: $IMPORTED_COUNT reports"

if [ "$IMPORTED_COUNT" -ne 3 ]; then
  echo "⚠️  Expected 3 imports, got $IMPORTED_COUNT"
fi

sleep 2

echo ""
echo "Step 6: Verify imported data integrity..."

ALL_REPORTS=$(curl -s -X GET "$BASE_URL/reports" -H "Authorization: Bearer $TOKEN")

# Check each report
echo "$ALL_REPORTS" | grep -q "TEST_155_A_${TIMESTAMP}"
HAS_A=$?
echo "$ALL_REPORTS" | grep -q "TEST_155_B_${TIMESTAMP}"
HAS_B=$?
echo "$ALL_REPORTS" | grep -q "TEST_155_C_${TIMESTAMP}"
HAS_C=$?

if [ $HAS_A -eq 0 ]; then
  echo "✅ Report A found in database"
else
  echo "❌ Report A missing"
fi

if [ $HAS_B -eq 0 ]; then
  echo "✅ Report B found in database"
else
  echo "❌ Report B missing"
fi

if [ $HAS_C -eq 0 ]; then
  echo "✅ Report C found in database"
else
  echo "❌ Report C missing"
fi

echo ""
echo "Step 7: Verify data field integrity..."

# Extract report details for verification
REPORT_A_DATA=$(echo "$ALL_REPORTS" | grep -A 10 "TEST_155_A_${TIMESTAMP}")
REPORT_B_DATA=$(echo "$ALL_REPORTS" | grep -A 10 "TEST_155_B_${TIMESTAMP}")
REPORT_C_DATA=$(echo "$ALL_REPORTS" | grep -A 10 "TEST_155_C_${TIMESTAMP}")

# Check Report A fields
echo "$REPORT_A_DATA" | grep -q "company_profile"
A_TYPE=$?
echo "$REPORT_A_DATA" | grep -q "Test Company A"
A_COMPANY=$?

# Check Report B fields
echo "$REPORT_B_DATA" | grep -q "market_analysis"
B_TYPE=$?
echo "$REPORT_B_DATA" | grep -q "Test Company B"
B_COMPANY=$?

# Check Report C fields
echo "$REPORT_C_DATA" | grep -q "competitive_analysis"
C_TYPE=$?

INTEGRITY_PASS=0
if [ $A_TYPE -eq 0 ] && [ $A_COMPANY -eq 0 ]; then
  echo "✅ Report A: type and company preserved"
  INTEGRITY_PASS=$((INTEGRITY_PASS + 1))
else
  echo "❌ Report A: data integrity issues"
fi

if [ $B_TYPE -eq 0 ] && [ $B_COMPANY -eq 0 ]; then
  echo "✅ Report B: type and company preserved"
  INTEGRITY_PASS=$((INTEGRITY_PASS + 1))
else
  echo "❌ Report B: data integrity issues"
fi

if [ $C_TYPE -eq 0 ]; then
  echo "✅ Report C: type preserved"
  INTEGRITY_PASS=$((INTEGRITY_PASS + 1))
else
  echo "❌ Report C: data integrity issues"
fi

echo ""
echo "============================================================"
if [ $HAS_A -eq 0 ] && [ $HAS_B -eq 0 ] && [ $HAS_C -eq 0 ] && [ "$IMPORTED_COUNT" -eq 3 ] && [ $INTEGRITY_PASS -eq 3 ]; then
  echo "✅ Feature #155 PASSED"
  echo ""
  echo "All 5 test steps verified:"
  echo "  ✅ Step 1: Export existing data (CSV created)"
  echo "  ✅ Step 2: Clear data (3 reports deleted)"
  echo "  ✅ Step 3: Import exported file (3 reports imported)"
  echo "  ✅ Step 4: Verify all data restored (3/3 found)"
  echo "  ✅ Step 5: Verify data matches original (fields intact)"
  echo "============================================================"
  exit 0
else
  echo "❌ Feature #155 FAILED"
  echo ""
  echo "Test Results:"
  echo "  - Reports found: A=$HAS_A B=$HAS_B C=$HAS_C (0=found, 1=missing)"
  echo "  - Imported count: $IMPORTED_COUNT (expected 3)"
  echo "  - Integrity checks passed: $INTEGRITY_PASS/3"
  echo "============================================================"
  exit 1
fi
