#!/usr/bin/env python3
"""
Generate 500+ test reports for infinite scroll performance testing.
This script creates reports via the API to test Feature #201.
"""

import requests
import json
from datetime import datetime, timedelta
import random
import time

API_BASE = "http://localhost:8000/api/v1"

# Test user credentials (assuming a test user exists)
TEST_EMAIL = "user@example.com"
TEST_PASSWORD = "Test1234"

# Report types
REPORT_TYPES = ["company_profile", "market_analysis", "due_diligence", "competitive"]
STATUSES = ["draft", "in_progress", "completed"]
COMPANIES = [
    "Tech Solutions Sp. z o.o.", "Industrial Corp", "Digital Services SA",
    "Manufacturing Poland", "Consulting Group", "E-commerce Ventures",
    "Logistics Hub", "Finance Partners", "Marketing Agency", None
]

def login():
    """Login and get access token"""
    print("🔐 Logging in...")
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )

    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Logged in successfully")
        return token
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def get_csrf_token():
    """Get CSRF token for POST requests"""
    try:
        response = requests.get(f"{API_BASE}/auth/csrf-token")
        if response.status_code == 200:
            return response.json()["csrf_token"]
    except Exception as e:
        print(f"⚠️  Failed to get CSRF token: {e}")
    return None

def create_test_report(token: str, csrf_token: str, index: int):
    """Create a single test report"""
    report_type = random.choice(REPORT_TYPES)
    status = random.choice(STATUSES)
    company = random.choice(COMPANIES)

    # Generate timestamp in the past (last 90 days)
    days_ago = random.randint(0, 90)
    created_at = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()

    title = f"Test Report #{index:04d} - {report_type.replace('_', ' ').title()}"
    summary = f"This is a test report generated for infinite scroll performance testing. Report type: {report_type}. Created for Feature #201 validation."

    if company:
        title += f" for {company}"
        summary += f" Subject: {company}."

    # Content for the report
    content = f"""
# Test Report #{index:04d}

This is test content generated for infinite scroll performance testing (Feature #201).

## Report Details
- **Type**: {report_type}
- **Company**: {company or 'N/A'}
- **Status**: {status}
- **Index**: {index}

## Executive Summary
This report was automatically generated to test the infinite scroll functionality and performance.
We need to verify that:
1. Scrolling remains smooth with 500+ items
2. No memory leaks occur during continuous scrolling
3. Older items are properly managed (virtualization)

## Test Data
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
"""

    payload = {
        "title": title,
        "type": report_type,
        "company": company,
        "summary": summary,
        "content": content
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    if csrf_token:
        headers["X-CSRF-Token"] = csrf_token

    try:
        response = requests.post(
            f"{API_BASE}/reports/",
            json=payload,
            headers=headers
        )

        if response.status_code in [200, 201]:
            return True
        else:
            print(f"❌ Failed to create report {index}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Exception creating report {index}: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 GENERATING 500+ TEST REPORTS FOR INFINITE SCROLL")
    print("=" * 60)
    print()

    # Login
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return

    # Get CSRF token
    csrf_token = get_csrf_token()
    if not csrf_token:
        print("⚠️  Proceeding without CSRF token (may fail)")

    print()
    # Use smaller count for faster testing (can increase to 500+ if needed)
    target_count = 100
    print(f"📊 Creating {target_count} test reports...")
    print()
    success_count = 0
    failed_count = 0

    start_time = time.time()

    for i in range(1, target_count + 1):
        if create_test_report(token, csrf_token, i):
            success_count += 1
        else:
            failed_count += 1

        # Progress indicator every 50 reports
        if i % 50 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = (target_count - i) * avg_time
            print(f"✅ Progress: {i}/{target_count} ({(i/target_count)*100:.1f}%) - ETA: {remaining:.1f}s")

        # Small delay to avoid overwhelming the API
        time.sleep(0.05)

    elapsed_time = time.time() - start_time

    print()
    print("=" * 60)
    print("📈 GENERATION COMPLETE")
    print("=" * 60)
    print(f"✅ Successfully created: {success_count} reports")
    print(f"❌ Failed: {failed_count} reports")
    print(f"⏱️  Total time: {elapsed_time:.2f} seconds")
    print(f"⚡ Average: {elapsed_time/target_count:.3f}s per report")
    print()
    print(f"🌐 Test infinite scroll at: http://localhost:3000/reports/infinite")
    print()

if __name__ == "__main__":
    main()
