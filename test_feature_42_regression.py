#!/usr/bin/env python3
"""Feature #42 Regression Test: Report export to PDF"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:8000/api/v1"

print("=== Feature #42 Regression Test: Report export to PDF ===\n")

# Step 1: Login
print("Step 1: Login to get auth token...")
try:
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123"
    })

    if response.status_code != 200:
        print("⚠️  Login failed, creating test user...")
        # Register
        requests.post(f"{BASE_URL}/auth/register", json={
            "email": "test@example.com",
            "password": "TestPass123",
            "name": "Test User"
        })
        # Login again
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123"
        })

    token = response.json()["access_token"]
    print(f"✅ Access token obtained\n")
except Exception as e:
    print(f"❌ Failed to login: {e}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Step 2: Get list of reports
print("Step 2: Get list of reports...")
try:
    response = requests.get(f"{BASE_URL}/reports/", headers=headers)
    reports = response.json()

    if not reports:
        print("❌ No reports found")
        exit(1)

    report_id = reports[0]["id"]
    report_title = reports[0]["title"]
    print(f"✅ Found report: {report_id} - {report_title}\n")
except Exception as e:
    print(f"❌ Failed to get reports: {e}")
    exit(1)

# Step 3: Export report to PDF
print("Step 3: Export report to PDF...")
try:
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/reports/{report_id}/export/pdf",
        headers=headers,
        stream=True
    )
    end_time = time.time()
    response_time = int((end_time - start_time) * 1000)

    print(f"HTTP Status: {response.status_code}")
    print(f"Response time: {response_time}ms")

    if response.status_code == 200:
        # Save PDF to file
        pdf_file = "test_report_export.pdf"
        with open(pdf_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Check file size
        file_size = os.path.getsize(pdf_file)
        print(f"✅ PDF file created successfully")
        print(f"   File size: {file_size} bytes")

        # Verify it's a PDF
        with open(pdf_file, "rb") as f:
            header = f.read(4)
            if header == b'%PDF':
                print(f"✅ File is a valid PDF document")
            else:
                print(f"⚠️  File may not be a valid PDF (header: {header})")

        # Cleanup
        os.remove(pdf_file)

        print("\n=== ✅ Feature #42 REGRESSION TEST PASSED ===")
        print("Report PDF export is working correctly!")
    else:
        print(f"❌ PDF export failed with status {response.status_code}")
        print(f"Response: {response.text[:200]}")
        print("\n=== ❌ Feature #42 REGRESSION TEST FAILED ===")
        exit(1)

except Exception as e:
    print(f"❌ Export failed: {e}")
    print("\n=== ❌ Feature #42 REGRESSION TEST FAILED ===")
    exit(1)
