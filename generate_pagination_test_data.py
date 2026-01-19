#!/usr/bin/env python3
"""
Generate 1000 mock reports for pagination performance testing (Feature #200)
"""

# Generate Python code to add to MOCK_REPORTS
reports = []

for i in range(1, 1001):
    report = {
        "id": f"pagination_test_{i:04d}",
        "title": f"Pagination Test Report #{i}",
        "type": "market_analysis" if i % 2 == 0 else "company_profile",
        "company": f"Test Company {i}" if i % 3 == 0 else None,
        "created_at": f"2026-01-{min(19, 1 + i % 28):02d}T{i % 24:02d}:{i % 60:02d}:00Z",
        "updated_at": f"2026-01-{min(19, 1 + i % 28):02d}T{i % 24:02d}:{i % 60:02d}:00Z",
        "status": "completed",
        "is_archived": False,
        "created_by": "f6e9a62efb704808882be5711d0a5411",  # user@example.com
        "summary": f"Test report {i} for pagination performance testing",
        "sections": [],
        "sources": []
    }
    reports.append(report)

# Generate Python code
print("# PAGINATION TEST DATA - Feature #200")
print("# Generated 1000 test reports")
print("PAGINATION_TEST_REPORTS = [")
for report in reports:
    print(f"    {{")
    for key, value in report.items():
        if isinstance(value, str):
            print(f"        \"{key}\": \"{value}\",")
        elif isinstance(value, bool):
            print(f"        \"{key}\": {value},")
        elif isinstance(value, list):
            print(f"        \"{key}\": [],")
        else:
            print(f"        \"{key}\": {value},")
    print(f"    }},")
print("]")
print()
print("# Add to MOCK_REPORTS:")
print("# MOCK_REPORTS.extend(PAGINATION_TEST_REPORTS)")
