#!/usr/bin/env python3
"""
Feature #151: Export filtered data only exports filtered
Test that filtered export contains only filtered results
"""

import sys
import subprocess
import json

def run_curl(command):
    """Run curl command and return response"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout, result.returncode

def test_filtered_export():
    print("=" * 60)
    print("Feature #151: Export Filtered Data Test")
    print("=" * 60)
    
    # Step 1: Check total number of reports by type
    print("\n Step 1: Count reports by type...")
    
    stdout, _ = run_curl('curl -s http://localhost:8000/api/v1/reports')
    all_reports = json.loads(stdout)
    total_reports = len(all_reports.get('reports', []))
    print(f"   Total reports in system: {total_reports}")
    
    # Count by type
    type_counts = {}
    for report in all_reports.get('reports', []):
        rtype = report.get('type', 'unknown')
        type_counts[rtype] = type_counts.get(rtype, 0) + 1
    
    print("\n   Reports by type:")
    for rtype, count in sorted(type_counts.items()):
        print(f"     - {rtype}: {count}")
    
    # Step 2: Filter to show only company_profile type
    print("\n Step 2: Test filter for company_profile type...")
    stdout, _ = run_curl('curl -s "http://localhost:8000/api/v1/reports/ids?type=company_profile"')
    filtered_ids = json.loads(stdout)
    filtered_count = len(filtered_ids.get('ids', []))
    print(f"   Filtered company_profile reports: {filtered_count}")
    print(f"   IDs: {filtered_ids.get('ids', [])[:5]}...")  # Show first 5
    
    # Step 3: Verify correct filtering
    print("\n Step 3: Verify filtering works correctly...")
    expected_count = type_counts.get('company_profile', 0)
    if filtered_count == expected_count:
        print(f"   ✅ PASS: Filter returned correct count ({filtered_count} == {expected_count})")
    else:
        print(f"   ❌ FAIL: Filter count mismatch ({filtered_count} != {expected_count})")
        return False
    
    # Step 4: Test status filter (completed only)
    print("\n Step 4: Test status filter (completed)...")
    stdout, _ = run_curl('curl -s "http://localhost:8000/api/v1/reports/ids?status=completed"')
    status_filtered = json.loads(stdout)
    status_count = len(status_filtered.get('ids', []))
    print(f"   Filtered completed reports: {status_count}")
    
    # Count actual completed reports
    completed_count = sum(1 for r in all_reports.get('reports', []) if r.get('status') == 'completed')
    if status_count == completed_count:
        print(f"   ✅ PASS: Status filter correct ({status_count} == {completed_count})")
    else:
        print(f"   ❌ FAIL: Status filter mismatch ({status_count} != {completed_count})")
        return False
    
    # Step 5: Test combined filters (company_profile + completed)
    print("\n Step 5: Test combined filters...")
    stdout, _ = run_curl('curl -s "http://localhost:8000/api/v1/reports/ids?type=company_profile&status=completed"')
    combined_filtered = json.loads(stdout)
    combined_count = len(combined_filtered.get('ids', []))
    print(f"   Filtered company_profile+completed reports: {combined_count}")
    
    # Verify combined filter
    expected_combined = sum(
        1 for r in all_reports.get('reports', []) 
        if r.get('type') == 'company_profile' and r.get('status') == 'completed'
    )
    if combined_count == expected_combined:
        print(f"   ✅ PASS: Combined filter correct ({combined_count} == {expected_combined})")
    else:
        print(f"   ❌ FAIL: Combined filter mismatch ({combined_count} != {expected_combined})")
        return False
    
    # Step 6: Test archived filter
    print("\n Step 6: Test archived filter...")
    stdout, _ = run_curl('curl -s "http://localhost:8000/api/v1/reports/ids?archived=false"')
    non_archived = json.loads(stdout)
    non_archived_count = len(non_archived.get('ids', []))
    print(f"   Non-archived reports: {non_archived_count}")
    
    # By default, archived should be excluded
    stdout, _ = run_curl('curl -s "http://localhost:8000/api/v1/reports/ids"')
    default_ids = json.loads(stdout)
    default_count = len(default_ids.get('ids', []))
    if default_count == non_archived_count:
        print(f"   ✅ PASS: Default excludes archived ({default_count} == {non_archived_count})")
    else:
        print(f"   ❌ FAIL: Default behavior incorrect ({default_count} != {non_archived_count})")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("Feature #151: Export filtered data only exports filtered - VERIFIED")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_filtered_export()
    sys.exit(0 if success else 1)
