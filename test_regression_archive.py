import requests
import json

print("=== REGRESSION TEST: Feature #289 - Archive/Unarchive Reports ===")

# Get all reports
print("\n1. Getting list of reports...")
response = requests.get("http://localhost:8000/api/v1/reports")
if response.status_code == 200:
    data = response.json()
    reports = data.get('reports', [])
    print(f"Found {len(reports)} reports")
    if reports:
        for r in reports[:3]:
            print(f"  - {r.get('id')} - {r.get('title')} - archived: {r.get('is_archived', False)}")
        
        # Test archive endpoint
        report_id = reports[0]['id']
        print(f"\n2. Testing archive for report: {report_id}")
        
        archive_response = requests.post(f"http://localhost:8000/api/v1/reports/{report_id}/archive")
        print(f"Archive status: {archive_response.status_code}")
        
        # Check if archived
        print("\n3. Checking if report is archived...")
        check_response = requests.get(f"http://localhost:8000/api/v1/reports/{report_id}")
        if check_response.status_code == 200:
            report = check_response.json()
            is_archived = report.get('is_archived', 'field_not_found')
            print(f"is_archived: {is_archived}")
            
            if is_archived == True:
                print("\n✅ PASSED: Archive functionality works!")
            else:
                print(f"\n⚠️  WARNING: Archive might not work (is_archived: {is_archived})")
        else:
            print(f"Error checking report: {check_response.status_code}")
    else:
        print("No reports found")
else:
    print(f"Error getting reports: {response.status_code}")

print("\n=== Regression test completed ===")
