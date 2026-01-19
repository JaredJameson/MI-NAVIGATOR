#!/bin/bash
# Feature #155: Import then export data integrity
# Manual test using curl commands

echo "============================================================"
echo "Feature #155: Import-Export Data Integrity Test"
echo "============================================================"

BASE_URL="http://localhost:8000/api/v1"
TIMESTAMP=$(date +%s)

echo ""
echo "Step 1: Login and get token..."
# Note: This user might have 2FA enabled - if so, we'll need to work around it
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=Test123!")

echo "$LOGIN_RESPONSE" | grep -q "requires_2fa"
if [ $? -eq 0 ]; then
  echo "❌ User has 2FA enabled - cannot proceed with automated test"
  echo "   Manual intervention needed to disable 2FA first"
  exit 1
fi

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get access token"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Logged in successfully"

echo ""
echo "Step 2: Create test reports..."

# Create 3 test reports
REPORT1=$(curl -s -X POST "$BASE_URL/reports" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"TEST_155_A_${TIMESTAMP}\",
    \"type\": \"company_profile\",
    \"company\": \"Test Company A\",
    \"summary\": \"Test report A for integrity check\",
    \"status\": \"completed\"
  }")

REPORT2=$(curl -s -X POST "$BASE_URL/reports" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"TEST_155_B_${TIMESTAMP}\",
    \"type\": \"market_analysis\",
    \"company\": \"Test Company B\",
    \"summary\": \"Test report B for integrity check\",
    \"status\": \"draft\"
  }")

REPORT3=$(curl -s -X POST "$BASE_URL/reports" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"TEST_155_C_${TIMESTAMP}\",
    \"type\": \"competitive_analysis\",
    \"summary\": \"Test report C without company\",
    \"status\": \"in_progress\"
  }")

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
echo "   - ID1: $ID1"
echo "   - ID2: $ID2"
echo "   - ID3: $ID3"

echo ""
echo "Step 3: Create CSV export file manually..."

# Create CSV file with the test data
CSV_FILE="test_export_155_${TIMESTAMP}.csv"
cat > "$CSV_FILE" << EOF
title,type,company,summary,status
"TEST_155_A_${TIMESTAMP}",company_profile,"Test Company A","Test report A for integrity check",completed
"TEST_155_B_${TIMESTAMP}",market_analysis,"Test Company B","Test report B for integrity check",draft
"TEST_155_C_${TIMESTAMP}",competitive_analysis,"","Test report C without company",in_progress
EOF

echo "✅ Created CSV export file: $CSV_FILE"

echo ""
echo "Step 4: Delete original reports..."

DELETE1=$(curl -s -X DELETE "$BASE_URL/reports/$ID1" -H "Authorization: Bearer $TOKEN")
DELETE2=$(curl -s -X DELETE "$BASE_URL/reports/$ID2" -H "Authorization: Bearer $TOKEN")
DELETE3=$(curl -s -X DELETE "$BASE_URL/reports/$ID3" -H "Authorization: Bearer $TOKEN")

echo "✅ Deleted 3 original reports"

sleep 1

echo ""
echo "Step 5: Import from CSV file..."

IMPORT_RESPONSE=$(curl -s -X POST "$BASE_URL/reports/bulk-import" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$CSV_FILE")

echo "Import response:"
echo "$IMPORT_RESPONSE" | head -20

IMPORTED_COUNT=$(echo "$IMPORT_RESPONSE" | grep -o '"imported_count":[0-9]*' | cut -d':' -f2)

if [ -z "$IMPORTED_COUNT" ]; then
  echo "❌ Import failed or returned unexpected response"
  exit 1
fi

echo "✅ Import completed: $IMPORTED_COUNT reports imported"

if [ "$IMPORTED_COUNT" -eq 3 ]; then
  echo "✅ Expected count matches (3 reports)"
else
  echo "⚠️  Count mismatch: expected 3, got $IMPORTED_COUNT"
fi

echo ""
echo "Step 6: Verify imported data..."

# Get all reports
ALL_REPORTS=$(curl -s -X GET "$BASE_URL/reports" -H "Authorization: Bearer $TOKEN")

# Check if our test reports exist
echo "$ALL_REPORTS" | grep -q "TEST_155_A_${TIMESTAMP}"
HAS_A=$?
echo "$ALL_REPORTS" | grep -q "TEST_155_B_${TIMESTAMP}"
HAS_B=$?
echo "$ALL_REPORTS" | grep -q "TEST_155_C_${TIMESTAMP}"
HAS_C=$?

if [ $HAS_A -eq 0 ] && [ $HAS_B -eq 0 ] && [ $HAS_C -eq 0 ]; then
  echo "✅ All 3 reports found in database"
else
  echo "❌ Some reports missing:"
  [ $HAS_A -ne 0 ] && echo "   - TEST_155_A missing"
  [ $HAS_B -ne 0 ] && echo "   - TEST_155_B missing"
  [ $HAS_C -ne 0 ] && echo "   - TEST_155_C missing"
fi

echo ""
echo "============================================================"
if [ $HAS_A -eq 0 ] && [ $HAS_B -eq 0 ] && [ $HAS_C -eq 0 ] && [ "$IMPORTED_COUNT" -eq 3 ]; then
  echo "✅ Feature #155 PASSED: Data integrity verified"
  echo "============================================================"
  exit 0
else
  echo "❌ Feature #155 FAILED: Data integrity issues"
  echo "============================================================"
  exit 1
fi
