#!/usr/bin/env python3
import requests
import json
import time

API_BASE = "http://localhost:8000/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlMmJiYzNmNC1jMDgwLTRjOWEtODExYi1mYmY0MWE3MmYyZjciLCJleHAiOjE3Njg4NTEwNzYsInR5cGUiOiJhY2Nlc3MiLCJqdGkiOiI5OTQ5OTYyNi05MjI1LTQ5ZDktYjY1NS00NGMwZjczNGU3NDgifQ.B00dj8MZYhAiCjlFGuUYWbZCxbJ6BubCKgR7RguSx2c"

REPORT_TYPES = ["company_profile", "market_analysis", "due_diligence", "competitive"]
COMPANIES = [
    "Tech Solutions Sp. z o.o.", "Industrial Corp", "Digital Services SA",
    "Manufacturing Poland", "Consulting Group", "E-commerce Ventures",
    "Logistics Hub", "Finance Partners", "Marketing Agency"
]

print("Generating 100 test reports...")
success_count = 0
start_time = time.time()

for i in range(2, 102):
    report_type = REPORT_TYPES[i % len(REPORT_TYPES)]
    company = COMPANIES[i % len(COMPANIES)]

    payload = {
        "title": f"Test Report {i:03d} - {report_type.replace('_', ' ').title()}",
        "type": report_type,
        "company": company,
        "summary": f"Test summary for report {i} - infinite scroll testing",
        "content": f"Test content for report {i}. This is generated for Feature #201 infinite scroll performance testing."
    }

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{API_BASE}/reports/",
            json=payload,
            headers=headers
        )

        if response.status_code in [200, 201]:
            success_count += 1
            if i % 20 == 0:
                elapsed = time.time() - start_time
                print(f"Created {i} reports in {elapsed:.1f}s")
        else:
            print(f"Failed to create report {i}: {response.status_code}")
    except Exception as e:
        print(f"Exception creating report {i}: {e}")

    time.sleep(0.05)

elapsed_time = time.time() - start_time
print(f"\n✅ Successfully created {success_count} reports in {elapsed_time:.2f}s")
print(f"Test at: http://localhost:3000/reports/infinite")
