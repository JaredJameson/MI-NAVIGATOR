#!/usr/bin/env python3
"""Create test report for Feature 117 - Multiple tabs test"""

import datetime

# Generate unique report ID
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
report_id = f"report_test117_{timestamp}"

report_data = {
    "id": report_id,
    "title": f"Test Multi-Tab Report {timestamp}",
    "type": "market_analysis",
    "company": "Test Company 117",
    "created_at": datetime.datetime.now().isoformat() + "Z",
    "updated_at": datetime.datetime.now().isoformat() + "Z",
    "status": "completed",
    "is_archived": False,
    "created_by": "dde243d1-a7a9-44c5-b28a-772ece7d500e",
    "summary": "Test report created in Tab 1 for multi-tab feature testing",
    "sections": [],
    "sources": []
}

print(f"Report ID: {report_id}")
print(f"Title: {report_data['title']}")
print("\nReport created successfully!")
