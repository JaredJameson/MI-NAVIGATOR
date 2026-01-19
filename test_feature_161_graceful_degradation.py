#!/usr/bin/env python3
"""
Feature #161: Agent failure graceful degradation
Test that system continues when single agent fails
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"
EMAIL = "test161@example.com"
PASSWORD = "Test123!"

def print_section(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50 + "\n")

def login_or_register():
    """Login or register user"""
    print("Step 1: Logging in...")

    # Try login
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": EMAIL, "password": PASSWORD}
    )

    if response.status_code == 200:
        token = response.json().get("access_token")
        if token:
            print("✅ Authenticated successfully\n")
            return token

    # Try register
    print("Login failed. Trying to register...")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={"email": EMAIL, "password": PASSWORD, "name": "Test User 161"}
    )

    if response.status_code not in [200, 201]:
        print(f"❌ Registration failed: {response.text}")
        sys.exit(1)

    # Try login again
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": EMAIL, "password": PASSWORD}
    )

    if response.status_code != 200:
        print("❌ Failed to get auth token")
        sys.exit(1)

    token = response.json().get("access_token")
    print("✅ Authenticated successfully\n")
    return token

def run_analysis(token, target, simulate_failures=None):
    """Run comprehensive analysis"""
    payload = {
        "target": target,
        "analysis_type": "comprehensive"
    }

    if simulate_failures:
        payload["simulate_failures"] = simulate_failures

    response = requests.post(
        f"{BASE_URL}/analysis/comprehensive",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )

    if response.status_code != 200:
        print(f"❌ Analysis request failed: {response.status_code}")
        print(response.text)
        sys.exit(1)

    return response.json()

def test_normal_execution(token):
    """Test 1: Normal execution (no failures)"""
    print_section("Test 1: Normal Execution (No Failures)")

    result = run_analysis(token, "TestCompany Normal")

    print("Response:")
    print(json.dumps(result, indent=2))
    print()

    summary = result.get("summary", {})
    failed = summary.get("failed_agents", 0)
    success = summary.get("successful_agents", 0)
    total = summary.get("total_agents", 0)

    print(f"Summary:")
    print(f"  Total agents: {total}")
    print(f"  Successful: {success}")
    print(f"  Failed: {failed}\n")

    if failed == 0:
        print("✅ Test 1 PASSED: All agents completed successfully\n")
        return True
    else:
        print(f"❌ Test 1 FAILED: Expected 0 failures, got {failed}\n")
        return False

def test_single_failure(token):
    """Test 2: Single agent failure"""
    print_section("Test 2: Single Agent Failure (financial_analysis)")

    result = run_analysis(
        token,
        "TestCompany Failure",
        simulate_failures=["financial_analysis"]
    )

    print("Response:")
    print(json.dumps(result, indent=2))
    print()

    summary = result.get("summary", {})
    failed = summary.get("failed_agents", 0)
    success = summary.get("successful_agents", 0)
    total = summary.get("total_agents", 0)
    failed_list = summary.get("failed_agent_list", [])
    success_rate = summary.get("success_rate", 0)
    status = result.get("status", "")
    errors = summary.get("errors", [])

    print(f"Summary:")
    print(f"  Total agents: {total}")
    print(f"  Successful: {success}")
    print(f"  Failed: {failed}")
    print(f"  Failed agents: {', '.join(failed_list)}")
    print(f"  Success rate: {success_rate:.1f}%")
    print(f"  Status: {status}\n")

    all_passed = True

    # Step 2: Verify one agent failed
    if failed == 1:
        print("✅ Step 2 PASSED: One agent failed as expected")
    else:
        print(f"❌ Step 2 FAILED: Expected 1 failure, got {failed}")
        all_passed = False

    # Step 3: Verify other agents continued
    if success >= 6:
        print(f"✅ Step 3 PASSED: Other agents continued ({success} successful)")
    else:
        print(f"❌ Step 3 FAILED: Expected at least 6 successful agents, got {success}")
        all_passed = False

    # Step 4: Verify partial results returned
    results_count = len(result.get("results", {}))
    if results_count >= 6:
        print(f"✅ Step 4 PASSED: Partial results returned ({results_count} results)")
    else:
        print(f"❌ Step 4 FAILED: Expected at least 6 results, got {results_count}")
        all_passed = False

    # Step 5: Verify failure is reported
    financial_error = any("financial_analysis" in str(err).lower() for err in errors)
    if financial_error or "financial_analysis" in failed_list:
        print("✅ Step 5 PASSED: Failure reported in output")
        if errors:
            print(f"  Errors: {errors}")
    else:
        print("❌ Step 5 FAILED: Failure not reported in output")
        all_passed = False

    # Verify status is "completed"
    if status == "completed":
        print("✅ Job status is 'completed' despite agent failure")
    else:
        print(f"❌ Job status should be 'completed', got: {status}")
        all_passed = False

    print()
    return all_passed

def test_multiple_failures(token):
    """Test 3: Multiple agent failures"""
    print_section("Test 3: Multiple Agent Failures")

    result = run_analysis(
        token,
        "TestCompany Multi Failure",
        simulate_failures=["financial_analysis", "digital_presence", "competitor_mapping"]
    )

    print("Response:")
    print(json.dumps(result, indent=2))
    print()

    summary = result.get("summary", {})
    failed = summary.get("failed_agents", 0)
    success = summary.get("successful_agents", 0)
    total = summary.get("total_agents", 0)
    success_rate = summary.get("success_rate", 0)

    print(f"Summary:")
    print(f"  Total agents: {total}")
    print(f"  Successful: {success}")
    print(f"  Failed: {failed}")
    print(f"  Success rate: {success_rate:.1f}%\n")

    if failed == 3 and success >= 4:
        print("✅ Test 3 PASSED: Multiple failures handled gracefully\n")
        return True
    else:
        print(f"❌ Test 3 FAILED: Expected 3 failures and ≥4 successes, got {failed} failures and {success} successes\n")
        return False

def main():
    print_section("Feature #161: Agent Failure Graceful Degradation")

    try:
        # Login
        token = login_or_register()

        # Run tests
        test1_passed = test_normal_execution(token)
        test2_passed = test_single_failure(token)
        test3_passed = test_multiple_failures(token)

        # Final summary
        print_section("FINAL VERIFICATION")

        if test1_passed and test2_passed and test3_passed:
            print("✅ Feature #161: Agent failure graceful degradation - VERIFIED\n")
            print("Key findings:")
            print("  - System continues when single agent fails")
            print("  - Other agents execute successfully in parallel")
            print("  - Partial results are returned")
            print("  - Failures are properly reported")
            print("  - Job completes with 'completed' status\n")
            return 0
        else:
            print("❌ Some tests failed\n")
            return 1

    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
