#!/usr/bin/env python3
"""
Feature #160 Timing Test
Verify that parallel execution is faster than sequential execution
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"

def register_and_login():
    """Register test user and get token"""
    timestamp = int(time.time())
    email = f"test_timing_{timestamp}@example.com"
    password = "TestPass123!"

    # Register
    register_response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "confirm_password": password,
        "name": "Test Timing User"
    })

    # Login
    login_response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": email,
        "password": password
    })

    token = login_response.json()["access_token"]
    return token

def test_comprehensive_analysis(token, analysis_type="comprehensive"):
    """Run comprehensive analysis and measure time"""
    headers = {"Authorization": f"Bearer {token}"}

    start_time = time.time()

    response = requests.post(f"{BASE_URL}/analysis/comprehensive",
        headers=headers,
        json={
            "target": "Test Company",
            "analysis_type": analysis_type
        }
    )

    end_time = time.time()
    elapsed_ms = int((end_time - start_time) * 1000)

    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return None

    data = response.json()
    return {
        "elapsed_ms": elapsed_ms,
        "job_id": data.get("job_id"),
        "status": data.get("status"),
        "results": data.get("results", {}),
        "execution_plan": data.get("execution_plan", [])
    }

def analyze_timing(result):
    """Analyze timing from execution plan"""
    if not result or not result.get("execution_plan"):
        return None

    total_agent_time = 0
    phase_times = []

    for phase in result["execution_plan"]:
        phase_start = phase.get("started_at")
        phase_end = phase.get("completed_at")

        if phase_start and phase_end:
            # Calculate phase duration (rough estimate from timestamps)
            print(f"  Phase {phase['phase_id']} ({phase['name']}): {phase['execution_mode']}")
            print(f"    - Agents: {len(phase['agents'])}")
            print(f"    - Status: {phase['status']}")

        # Sum agent execution times from results
        for agent_name, agent_result in phase.get("results", {}).items():
            if isinstance(agent_result, dict) and "execution_time_ms" in agent_result:
                agent_time = agent_result["execution_time_ms"]
                total_agent_time += agent_time
                print(f"    - {agent_name}: {agent_time}ms")

    return total_agent_time

def main():
    print("=" * 60)
    print("Feature #160: Parallel vs Sequential Timing Test")
    print("=" * 60)
    print()

    # Login
    print("Step 1: Logging in...")
    token = register_and_login()
    print("✅ Logged in")
    print()

    # Test comprehensive analysis (with parallel execution)
    print("Step 2: Running comprehensive analysis (parallel + sequential)...")
    result = test_comprehensive_analysis(token, "comprehensive")

    if not result:
        print("❌ Test failed")
        return

    print(f"✅ Analysis completed in {result['elapsed_ms']}ms")
    print()

    print("Step 3: Analyzing execution details...")
    print()
    total_agent_time = analyze_timing(result)

    print()
    print("=" * 60)
    print("TIMING ANALYSIS")
    print("=" * 60)
    print()
    print(f"Total wall clock time: {result['elapsed_ms']}ms")
    print(f"Sum of all agent times: {total_agent_time}ms")
    print()

    # Calculate speedup
    if total_agent_time > 0:
        speedup = total_agent_time / result['elapsed_ms']
        print(f"Speedup factor: {speedup:.2f}x")
        print()

        if speedup > 1.5:
            print("✅ PARALLEL EXECUTION CONFIRMED!")
            print(f"   Wall clock time ({result['elapsed_ms']}ms) is significantly less than")
            print(f"   sum of agent times ({total_agent_time}ms)")
            print(f"   This proves agents ran in parallel (speedup: {speedup:.2f}x)")
        else:
            print("⚠️  WARNING: Speedup factor is low")
            print("   This might indicate sequential execution or overhead")

    print()
    print("Step 4: Verifying result aggregation...")
    agent_results = result.get("results", {})
    agent_count = len([k for k, v in agent_results.items() if isinstance(v, dict) and v.get("status") != "error"])

    print(f"  - Total agents executed: {agent_count}")
    print(f"  - Agents with results:")

    for agent_name in agent_results.keys():
        status = "✅" if isinstance(agent_results[agent_name], dict) else "❌"
        print(f"    {status} {agent_name}")

    print()

    if agent_count >= 7:
        print("✅ All agent results aggregated correctly")
    else:
        print(f"⚠️  WARNING: Expected 7 agents, got {agent_count}")

    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print()

    # Final verdict
    success_checks = []

    # Check 1: Request completed
    success_checks.append(result['status'] == 'completed')

    # Check 2: Reasonable execution time
    success_checks.append(result['elapsed_ms'] < 10000)  # Less than 10 seconds

    # Check 3: Speedup indicates parallelism
    if total_agent_time > 0:
        speedup = total_agent_time / result['elapsed_ms']
        success_checks.append(speedup > 1.3)

    # Check 4: All agents executed
    success_checks.append(agent_count >= 7)

    passed = sum(success_checks)
    total = len(success_checks)

    print(f"Passed: {passed}/{total} checks")
    print()

    if passed == total:
        print("✅ ALL TIMING TESTS PASSED!")
        print()
        print("Key findings:")
        print(f"  - Parallel execution speedup: {speedup:.2f}x")
        print(f"  - Wall clock time: {result['elapsed_ms']}ms")
        print(f"  - Sequential would take: ~{total_agent_time}ms")
        print(f"  - Time saved: ~{total_agent_time - result['elapsed_ms']}ms")
        print()
        print("Feature #160: Orchestrator executes agents in parallel - VERIFIED ✅")
    else:
        print("⚠️  SOME TIMING CHECKS FAILED")
        print("Review the output above for details")

if __name__ == "__main__":
    main()
