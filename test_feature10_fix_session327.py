#!/usr/bin/env python3
"""
Test script for Feature #10 data isolation fix (Session 327)
Tests that per-user unique IDs prevent 403 errors when multiple users access reports
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def register_user(email, password, name):
    """Register a new user"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "confirm_password": password,
            "name": name
        }
    )
    if response.status_code in [200, 201]:
        user_data = response.json()
        print(f"✅ Registered {name} ({email})")
        print(f"   User ID: {user_data['id']}")
        return user_data
    elif "already exists" in response.text.lower() or "already registered" in response.text.lower():
        print(f"⚠️  User {name} already exists, will try to login")
        return {"email": email}  # Return minimal data to continue
    else:
        print(f"❌ Failed to register {name}: {response.text}")
        return None

def login_user(email, password):
    """Login and get access token"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    if response.status_code == 200:
        tokens = response.json()
        print(f"✅ Logged in as {email}")
        return tokens['access_token']
    else:
        print(f"❌ Failed to login {email}: {response.text}")
        return None

def get_reports(token, limit=3):
    """Get reports list"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/reports/?page=1&limit={limit}",
        headers=headers
    )
    if response.status_code == 200:
        data = response.json()
        total = data.get('total', 0)
        items = data.get('items', [])
        print(f"✅ Retrieved reports list: {total} total reports, showing {len(items)}")
        return items
    else:
        print(f"❌ Failed to get reports: {response.status_code} {response.text}")
        return None

def get_report_detail(token, report_id):
    """Get single report detail"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/reports/{report_id}",
        headers=headers
    )
    if response.status_code == 200:
        report = response.json()
        print(f"✅ Successfully accessed report {report_id}")
        return report
    elif response.status_code == 403:
        print(f"❌ 403 FORBIDDEN on report {report_id} - DATA ISOLATION BUG!")
        return None
    else:
        print(f"❌ Failed to get report {report_id}: {response.status_code} {response.text[:100]}")
        return None

def main():
    print("=" * 80)
    print("Feature #10 Data Isolation Test (Session 327 Fix Verification)")
    print("=" * 80)
    print()

    # Test with User A
    print("STEP 1: Testing User A")
    print("-" * 80)
    import time
    timestamp = int(time.time())
    user_a = register_user(f"userA_test327_{timestamp}@example.com", "TestPass123", "User A")
    if not user_a:
        print("❌ FAILED: Could not create User A")
        return False

    token_a = login_user(f"userA_test327_{timestamp}@example.com", "TestPass123")
    if not token_a:
        print("❌ FAILED: Could not login as User A")
        return False

    reports_a = get_reports(token_a, limit=3)
    if not reports_a or len(reports_a) == 0:
        print("❌ FAILED: User A has no reports")
        return False

    first_report_a = reports_a[0]
    report_id_a = first_report_a['id']
    print(f"   First report ID: {report_id_a}")

    detail_a = get_report_detail(token_a, report_id_a)
    if not detail_a:
        print("❌ FAILED: User A cannot access their own report!")
        return False

    print()

    # Test with User B
    print("STEP 2: Testing User B")
    print("-" * 80)
    user_b = register_user(f"userB_test327_{timestamp}@example.com", "TestPass123", "User B")
    if not user_b:
        print("❌ FAILED: Could not create User B")
        return False

    token_b = login_user(f"userB_test327_{timestamp}@example.com", "TestPass123")
    if not token_b:
        print("❌ FAILED: Could not login as User B")
        return False

    reports_b = get_reports(token_b, limit=3)
    if not reports_b or len(reports_b) == 0:
        print("❌ FAILED: User B has no reports")
        return False

    first_report_b = reports_b[0]
    report_id_b = first_report_b['id']
    print(f"   First report ID: {report_id_b}")

    detail_b = get_report_detail(token_b, report_id_b)
    if not detail_b:
        print("❌ FAILED: User B cannot access their own report!")
        return False

    print()

    # Verify IDs are different
    print("STEP 3: Verifying per-user unique IDs")
    print("-" * 80)
    if report_id_a == report_id_b:
        print(f"❌ FAILED: Report IDs are THE SAME!")
        print(f"   User A: {report_id_a}")
        print(f"   User B: {report_id_b}")
        print("   This means the fix DID NOT WORK - IDs should be unique per user")
        return False
    else:
        print(f"✅ SUCCESS: Report IDs are DIFFERENT")
        print(f"   User A: {report_id_a}")
        print(f"   User B: {report_id_b}")
        print("   Per-user unique IDs are working correctly!")

    print()

    # Cross-access test (User B should NOT access User A's report)
    print("STEP 4: Testing data isolation (User B accessing User A's report)")
    print("-" * 80)
    cross_access = get_report_detail(token_b, report_id_a)
    if cross_access:
        print(f"❌ FAILED: User B can access User A's report - DATA LEAK!")
        return False
    else:
        print(f"✅ SUCCESS: User B correctly denied access to User A's report")

    print()
    print("=" * 80)
    print("✅ ALL TESTS PASSED - Feature #10 is WORKING CORRECTLY")
    print("=" * 80)
    return True

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
