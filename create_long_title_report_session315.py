#!/usr/bin/env python3
"""Create a report with very long title for Feature #142 testing"""

import requests
import json

# Login to get token
login_response = requests.post(
    "http://localhost:8004/api/v1/auth/login",
    json={
        "email": "session315_test@test.com",
        "password": "TestPass123"
    }
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token_data = login_response.json()
access_token = token_data["access_token"]

print(f"✅ Logged in successfully")

# Create report with very long title
very_long_title = "This Is An Extremely Long Report Title That Should Be Truncated With Ellipsis Because It Contains Way Too Many Characters And Should Not Display In Full Length On The UI Cards Or List Views According To Feature 142 Testing Requirements For Text Truncation Functionality"

report_data = {
    "title": very_long_title,
    "type": "company_profile",
    "status": "completed",
    "content": {
        "summary": "Test report for Feature #142 - Long text truncation with ellipsis",
        "sections": []
    },
    "metadata": {
        "test_feature": 142,
        "test_session": 315
    }
}

create_response = requests.post(
    "http://localhost:8004/api/v1/reports",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    },
    json=report_data
)

if create_response.status_code == 201:
    report = create_response.json()
    print(f"✅ Report created successfully!")
    print(f"   Report ID: {report.get('id')}")
    print(f"   Title (full): {report.get('title')}")
    print(f"   Title length: {len(report.get('title', ''))} characters")
else:
    print(f"❌ Failed to create report: {create_response.status_code}")
    print(create_response.text)
