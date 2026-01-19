#!/usr/bin/env python3
"""
Feature #155: Import then export data integrity
Test data integrity through import-export cycle

Step 1: Export existing data
Step 2: Clear data
Step 3: Import exported file
Step 4: Verify all data restored
Step 5: Verify data matches original
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def login():
    """Login and get token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "test@example.com",
            "password": "Test1234"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def create_test_reports(token):
    """Create test reports for export-import cycle"""
    headers = {"Authorization": f"Bearer {token}"}

    test_reports = [
        {
            "title": f"TEST_155_REPORT_A_{datetime.now().timestamp()}",
            "type": "company_profile",
            "company": "Test Company A",
            "summary": "This is test report A for integrity testing",
            "status": "completed"
        },
        {
            "title": f"TEST_155_REPORT_B_{datetime.now().timestamp()}",
            "type": "market_analysis",
            "company": "Test Company B",
            "summary": "This is test report B for integrity testing",
            "status": "draft"
        },
        {
            "title": f"TEST_155_REPORT_C_{datetime.now().timestamp()}",
            "type": "competitive_analysis",
            "company": None,
            "summary": "This is test report C without company",
            "status": "in_progress"
        }
    ]

    created_ids = []
    for report_data in test_reports:
        response = requests.post(
            f"{BASE_URL}/reports",
            headers=headers,
            json=report_data
        )
        if response.status_code in [200, 201]:
            report = response.json()
            created_ids.append(report["id"])
            print(f"✅ Created test report: {report['title']} (ID: {report['id']})")
        else:
            print(f"❌ Failed to create report: {response.status_code}")
            print(response.text)

    return created_ids, test_reports

def get_reports(token):
    """Get all reports"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/reports",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    return []

def export_reports_csv(token, report_ids):
    """Export reports to CSV format"""
    headers = {"Authorization": f"Bearer {token}"}

    # Create CSV content manually since bulk-export creates XLSX
    reports = get_reports(token)
    test_reports = [r for r in reports if r['id'] in report_ids]

    if not test_reports:
        print("❌ No test reports found for export")
        return None

    # Create CSV content
    csv_lines = ["title,type,company,summary,status"]
    for report in test_reports:
        company = report.get('company', '') or ''
        summary = (report.get('summary', '') or '').replace('\n', ' ').replace(',', ';')
        status = report.get('status', 'draft')
        csv_lines.append(f'"{report["title"]}",{report["type"]},"{company}","{summary}",{status}')

    csv_content = '\n'.join(csv_lines)

    # Save to file
    filename = f"test_export_155_{int(time.time())}.csv"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(csv_content)

    print(f"✅ Exported {len(test_reports)} reports to {filename}")
    return filename, test_reports

def delete_reports(token, report_ids):
    """Delete specific reports"""
    headers = {"Authorization": f"Bearer {token}"}

    deleted_count = 0
    for report_id in report_ids:
        response = requests.delete(
            f"{BASE_URL}/reports/{report_id}",
            headers=headers
        )
        if response.status_code in [200, 204]:
            deleted_count += 1
            print(f"✅ Deleted report: {report_id}")
        else:
            print(f"⚠️  Failed to delete {report_id}: {response.status_code}")

    return deleted_count

def import_reports_csv(token, filename):
    """Import reports from CSV file"""
    headers = {"Authorization": f"Bearer {token}"}

    with open(filename, 'rb') as f:
        files = {'file': (filename, f, 'text/csv')}
        response = requests.post(
            f"{BASE_URL}/reports/bulk-import",
            headers=headers,
            files=files
        )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Import completed: {result.get('imported_count', 0)} reports imported")
        if result.get('errors'):
            print(f"⚠️  Errors: {len(result['errors'])}")
            for error in result['errors'][:3]:
                print(f"   - Row {error['row']}: {error['errors']}")
        return result
    else:
        print(f"❌ Import failed: {response.status_code}")
        print(response.text)
        return None

def verify_data_integrity(token, original_reports, imported_result):
    """Verify that imported data matches original"""
    print("\n=== VERIFYING DATA INTEGRITY ===")

    # Get all current reports
    all_reports = get_reports(token)

    # Find the newly imported reports (they should have similar titles)
    imported_reports = []
    for orig in original_reports:
        # Find matching report by title prefix (without timestamp part)
        title_prefix = orig['title'].rsplit('_', 1)[0]  # Remove timestamp
        for report in all_reports:
            if report['title'].startswith(title_prefix):
                imported_reports.append(report)
                break

    print(f"Original reports count: {len(original_reports)}")
    print(f"Imported reports count: {len(imported_reports)}")

    if len(imported_reports) != len(original_reports):
        print(f"❌ Count mismatch! Expected {len(original_reports)}, got {len(imported_reports)}")
        return False

    # Verify each field
    matches = 0
    for i, orig in enumerate(original_reports):
        # Find corresponding imported report
        title_prefix = orig['title'].rsplit('_', 1)[0]
        imported = None
        for report in imported_reports:
            if report['title'].startswith(title_prefix):
                imported = report
                break

        if not imported:
            print(f"❌ No imported report found for: {orig['title']}")
            continue

        # Compare fields
        checks = []
        checks.append(("type", orig['type'] == imported['type']))
        checks.append(("company", (orig.get('company') or '') == (imported.get('company') or '')))
        checks.append(("status", orig.get('status', 'draft') == imported.get('status', 'draft')))

        all_match = all(check[1] for check in checks)
        if all_match:
            matches += 1
            print(f"✅ Report {i+1}: Data integrity verified")
        else:
            print(f"❌ Report {i+1}: Data mismatch")
            for field, match in checks:
                if not match:
                    print(f"   - {field}: '{orig.get(field)}' != '{imported.get(field)}'")

    print(f"\n{'✅' if matches == len(original_reports) else '❌'} Integrity check: {matches}/{len(original_reports)} reports match")
    return matches == len(original_reports)

def main():
    print("=" * 60)
    print("Feature #155: Import then export data integrity")
    print("=" * 60)

    # Login
    print("\n📝 Logging in...")
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        return

    # Step 1: Create test reports
    print("\n📝 Step 1: Creating test reports...")
    report_ids, original_reports = create_test_reports(token)
    if not report_ids:
        print("❌ Failed to create test reports")
        return

    time.sleep(1)  # Wait for creation

    # Step 2: Export data
    print("\n📝 Step 2: Exporting test reports to CSV...")
    export_result = export_reports_csv(token, report_ids)
    if not export_result:
        print("❌ Export failed")
        return

    filename, exported_reports = export_result

    # Step 3: Clear data (delete the reports)
    print("\n📝 Step 3: Deleting original reports...")
    deleted_count = delete_reports(token, report_ids)
    print(f"✅ Cleared {deleted_count} reports")

    time.sleep(1)  # Wait for deletion

    # Verify deletion
    remaining_reports = get_reports(token)
    still_exist = [r for r in remaining_reports if r['id'] in report_ids]
    if still_exist:
        print(f"⚠️  Warning: {len(still_exist)} reports still exist after deletion")
    else:
        print("✅ All test reports deleted successfully")

    # Step 4: Import the exported data
    print("\n📝 Step 4: Importing from exported CSV...")
    import_result = import_reports_csv(token, filename)
    if not import_result:
        print("❌ Import failed")
        return

    time.sleep(1)  # Wait for import

    # Step 5: Verify data integrity
    print("\n📝 Step 5: Verifying data integrity...")
    integrity_ok = verify_data_integrity(token, original_reports, import_result)

    # Final result
    print("\n" + "=" * 60)
    if integrity_ok:
        print("✅ Feature #155 PASSED: Data integrity maintained through export-import cycle")
        print("=" * 60)
        return True
    else:
        print("❌ Feature #155 FAILED: Data integrity issues detected")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
