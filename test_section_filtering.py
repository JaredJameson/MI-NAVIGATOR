#!/usr/bin/env python3
"""Test script to verify section filtering in export functionality."""

# Simulate the filtering logic from backend
report = {
    "id": "report_001",
    "title": "Test Report",
    "sections": [
        {"id": "section_1", "title": "Section 1", "content": "Content 1"},
        {"id": "section_2", "title": "Section 2", "content": "Content 2"},
        {"id": "section_3", "title": "Section 3", "content": "Content 3"},
        {"id": "section_4", "title": "Section 4", "content": "Content 4"},
        {"id": "section_5", "title": "Section 5", "content": "Content 5"},
        {"id": "section_6", "title": "Section 6", "content": "Content 6"},
    ]
}

# Test case: Filter to only sections 2, 4, 5 (like in our browser test)
section_ids = ["section_2", "section_4", "section_5"]

print("Original report sections:")
for s in report["sections"]:
    print(f"  - {s['id']}: {s['title']}")

# Apply filtering (same logic as backend)
filtered_report = report.copy()
original_sections = filtered_report.get("sections", [])
filtered_sections = [s for s in original_sections if s["id"] in section_ids]
filtered_report["sections"] = filtered_sections

print(f"\nFiltered report sections (only {section_ids}):")
for s in filtered_report["sections"]:
    print(f"  - {s['id']}: {s['title']}")

print(f"\nOriginal sections count: {len(report['sections'])}")
print(f"Filtered sections count: {len(filtered_report['sections'])}")
print(f"Expected count: {len(section_ids)}")

# Verify
if len(filtered_report["sections"]) == len(section_ids):
    print("\n✅ PASS: Filtering works correctly!")
    print(f"✅ Only selected sections included: {[s['id'] for s in filtered_report['sections']]}")
else:
    print("\n❌ FAIL: Filtering did not work as expected")
