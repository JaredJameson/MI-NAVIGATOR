#!/usr/bin/env python3
"""
Feature #150: Export data contains all created records
Simple test using Python requests
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Generate unique test data
timestamp = int(datetime.now().timestamp())
test_email = f"export_test_{timestamp}@test.com"
test_password = "TestPassword123"

print("=" * 50)
print("Feature #150: Export data contains all created records")
print("=" * 50)
print()

# Step 1: Register user
print("Step 1: Register test user...")
register_data = {
    "email": test_email,
    "password": test_password,
    "confirm_password": test_password,
    "name": "Export Test User"
}

response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print(f"✅ User registered: {test_email}")
print()

# Step 2: Login
print("Step 2: Login...")
login_data = {
    "username": test_email,
    "password": test_password
}

response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
tokens = response.json()
access_token = tokens["access_token"]
print(f"✅ Logged in, got access token")
print()

# Step 3: Get CSRF token (if needed)
print("Step 3: Get CSRF token...")
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/auth/csrf-token", headers=headers)
csrf_token = response.json()["csrf_token"]
print(f"✅ Got CSRF token")
print()

# Step 4: Create 5 reports
print("Step 4: Create 5 reports with unique names...")
headers = {
    "Authorization": f"Bearer {access_token}",
    "X-CSRF-Token": csrf_token
}

report_ids = []
for i in range(1, 6):
    report_data = {
        "title": f"Test Report #{i} - Created at {timestamp}",
        "type": "market_analysis",
        "company": f"Test Company {i}",
        "content": f"This is test report content for report number {i}. Created at {timestamp} for testing export functionality.",
        "summary": f"Test report {i} summary"
    }

    response = requests.post(f"{BASE_URL}/reports", json=report_data, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to create report #{i}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        exit(1)

    result = response.json()
    report_id = result["id"]
    report_ids.append(report_id)
    print(f"   ✅ Created report #{i}: {report_id}")

print()
print(f"✅ Created {len(report_ids)} reports total")
print()

# Step 5: Export all user data
print("Step 5: Export all user data...")
response = requests.post(f"{BASE_URL}/users/me/export-data", headers=headers)

if response.status_code != 200:
    print(f"❌ Export failed with status {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)

export_data = response.json()
print(f"✅ Export successful")
print()

# Step 6: Verify reports section exists
print("Step 6: Verify export structure...")
if "reports" not in export_data:
    print("❌ No 'reports' section in export data")
    print(f"   Available keys: {list(export_data.keys())}")
    exit(1)

print("✅ Found 'reports' section")
print()

# Step 7: Verify all 5 reports are present
print("Step 7: Verify all 5 reports present...")
exported_reports = export_data["reports"]
print(f"   Exported reports count: {len(exported_reports)}")

if len(exported_reports) != 5:
    print(f"❌ Expected 5 reports, found {len(exported_reports)}")
    exit(1)

print("✅ All 5 reports present in export")
print()

# Step 8: Verify data integrity
print("Step 8: Verify data integrity...")
for idx, report in enumerate(exported_reports, 1):
    print(f"   Report {idx}:")
    print(f"      ID: {report['id']}")
    print(f"      Title: {report['title']}")
    print(f"      Type: {report['type']}")
    print(f"      Company: {report.get('company', 'N/A')}")

    # Verify title contains timestamp
    if str(timestamp) not in report['title']:
        print(f"❌ Report {idx} title doesn't contain expected timestamp")
        exit(1)

print()
print("✅ All reports have correct data integrity")
print()

# Step 9: Verify export metadata
print("Step 9: Verify export metadata...")
metadata = export_data["export_metadata"]
total_reports = metadata.get("total_reports")

if total_reports != 5:
    print(f"❌ Metadata shows {total_reports} reports, expected 5")
    exit(1)

print(f"✅ Export metadata correct: total_reports = {total_reports}")
print()

# Step 10: Verify all required sections
print("Step 10: Verify all required sections...")
required_sections = ["user_profile", "preferences", "security", "reports", "activity_log", "export_metadata"]

for section in required_sections:
    if section not in export_data:
        print(f"❌ Missing section: {section}")
        exit(1)
    print(f"   ✅ Section present: {section}")

print()
print("=" * 50)
print("✅ ALL TESTS PASSED!")
print("Feature #150: Export data contains all created records - VERIFIED")
print("=" * 50)
print()
print("Summary:")
print(f"- Created 5 reports with unique names")
print(f"- Exported all user data")
print(f"- Verified all 5 reports present in export")
print(f"- Verified data integrity")
print(f"- Verified export metadata")
print(f"- Verified all required sections")
print()
print(f"Test user: {test_email}")
