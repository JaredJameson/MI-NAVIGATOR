#!/usr/bin/env python3
"""
Test Fact Checker Agent - Feature #156
Tests fact checking functionality with multiple sources, confidence scores, and conflict detection.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def login():
    """Login and get auth token."""
    # Try test user
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "testuser@example.com",
            "password": "Test123!"
        }
    )

    if response.status_code != 200:
        # Try admin user
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": "admin@example.com",
                "password": "Admin123!"
            }
        )

    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_fact_checker_basic(token):
    """Test basic fact checking with single source (should be LOW confidence)."""
    print("\n" + "="*80)
    print("TEST 1: Basic Fact Checking - Single Source")
    print("="*80)

    payload = {
        "company_name": "Test Company A",
        "facts": {
            "employee_count": {
                "sources": [
                    {
                        "name": "Company Website",
                        "type": "company_website",
                        "value": "100",
                        "date": "2024-01-15"
                    }
                ]
            }
        }
    }

    response = requests.post(
        f"{BASE_URL}/analysis/fact-check",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )

    if response.status_code == 200:
        result = response.json()
        report = result["fact_check_report"]

        print(f"✅ Fact check completed")
        print(f"Company: {report['subject']}")
        print(f"Total facts: {report['total_facts_checked']}")
        print(f"Quality score: {report['data_quality_score']}/100")
        print(f"\nConfidence summary:")
        for level, count in report['confidence_summary'].items():
            print(f"  {level.upper()}: {count}")

        # Verify single source = LOW confidence
        fact = report['verified_facts'][0]
        print(f"\nFact: {fact['fact']}")
        print(f"Confidence: {fact['confidence']}")
        print(f"Flags: {fact['flags']}")

        if fact['confidence'] == 'low' and 'single_source' in fact['flags']:
            print("✅ PASS: Single source correctly flagged as LOW confidence")
            return True
        else:
            print("❌ FAIL: Expected LOW confidence with single_source flag")
            return False
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return False

def test_fact_checker_official_source(token):
    """Test fact checking with official source (should be HIGH confidence)."""
    print("\n" + "="*80)
    print("TEST 2: Official Source - HIGH Confidence")
    print("="*80)

    payload = {
        "company_name": "Test Company B",
        "facts": {
            "revenue_2023": {
                "sources": [
                    {
                        "name": "KRS Financial Report",
                        "type": "official_registry",
                        "value": "50.2M PLN",
                        "date": "2024-03-15"
                    }
                ]
            }
        }
    }

    response = requests.post(
        f"{BASE_URL}/analysis/fact-check",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )

    if response.status_code == 200:
        result = response.json()
        report = result["fact_check_report"]
        fact = report['verified_facts'][0]

        print(f"✅ Fact check completed")
        print(f"Fact: {fact['fact']}")
        print(f"Verified value: {fact['verified_value']}")
        print(f"Confidence: {fact['confidence']}")
        print(f"Source: {fact['sources']}")

        if fact['confidence'] == 'high':
            print("✅ PASS: Official registry source correctly assigned HIGH confidence")
            return True
        else:
            print(f"❌ FAIL: Expected HIGH confidence, got {fact['confidence']}")
            return False
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return False

def test_fact_checker_multiple_sources(token):
    """Test cross-referencing with multiple sources."""
    print("\n" + "="*80)
    print("TEST 3: Multiple Sources Cross-Reference")
    print("="*80)

    payload = {
        "company_name": "FADO Sp. z o.o.",
        "facts": {
            "employee_count": {
                "sources": [
                    {
                        "name": "LinkedIn",
                        "type": "social_media",
                        "value": "245",
                        "date": "2024-01-15"
                    },
                    {
                        "name": "Company Website",
                        "type": "company_website",
                        "value": "250+",
                        "date": "2024-01-10"
                    },
                    {
                        "name": "GUS Database",
                        "type": "official_registry",
                        "value": "250",
                        "date": "2023-12-01"
                    }
                ]
            }
        }
    }

    response = requests.post(
        f"{BASE_URL}/analysis/fact-check",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )

    if response.status_code == 200:
        result = response.json()
        report = result["fact_check_report"]
        fact = report['verified_facts'][0]

        print(f"✅ Fact check completed")
        print(f"Fact: {fact['fact']}")
        print(f"Verified value: {fact['verified_value']}")
        print(f"Confidence: {fact['confidence']}")
        print(f"Sources ({fact['source_count']}): {', '.join(fact['sources'])}")
        print(f"Flags: {fact['flags']}")

        if fact['confidence'] == 'high' and fact['source_count'] == 3:
            print("✅ PASS: Multiple sources correctly assigned HIGH confidence")
            return True
        else:
            print(f"❌ FAIL: Expected HIGH confidence with 3 sources")
            return False
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return False

def test_conflict_detection(token):
    """Test detection of conflicting data between sources."""
    print("\n" + "="*80)
    print("TEST 4: Conflict Detection")
    print("="*80)

    payload = {
        "company_name": "Test Company C",
        "facts": {
            "founding_year": {
                "sources": [
                    {
                        "name": "Company Website",
                        "type": "company_website",
                        "value": "1995",
                        "date": "2024-01-15"
                    },
                    {
                        "name": "KRS Registry",
                        "type": "official_registry",
                        "value": "1998",
                        "date": "2024-01-20"
                    }
                ]
            }
        }
    }

    response = requests.post(
        f"{BASE_URL}/analysis/fact-check",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )

    if response.status_code == 200:
        result = response.json()
        report = result["fact_check_report"]
        fact = report['verified_facts'][0]

        print(f"✅ Fact check completed")
        print(f"Fact: {fact['fact']}")
        print(f"Verified value (from most reliable): {fact['verified_value']}")
        print(f"Confidence: {fact['confidence']}")
        print(f"Flags: {fact['flags']}")

        if fact.get('conflict'):
            conflict = fact['conflict']
            print(f"\n⚠️  CONFLICT DETECTED:")
            print(f"  Conflicting values: {len(conflict['conflicting_values'])}")
            for cv in conflict['conflicting_values']:
                print(f"    - {cv['value']} from {', '.join(cv['sources'])}")
            print(f"  Recommended value: {conflict['recommended_value']}")
            print(f"  Resolution: {conflict['resolution_note']}")

            if 'conflict' in fact['flags'] and conflict['recommended_value'] == '1998':
                print("✅ PASS: Conflict detected and resolved using most reliable source")
                return True
            else:
                print("❌ FAIL: Conflict not properly handled")
                return False
        else:
            print("❌ FAIL: Expected conflict to be detected")
            return False
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return False

def test_comprehensive_analysis(token):
    """Test comprehensive company analysis with multiple facts."""
    print("\n" + "="*80)
    print("TEST 5: Comprehensive Company Analysis")
    print("="*80)

    payload = {
        "company_name": "FADO Sp. z o.o.",
        "facts": {
            "employee_count": {
                "sources": [
                    {"name": "LinkedIn", "type": "social_media", "value": "245", "date": "2024-01-15"},
                    {"name": "Website", "type": "company_website", "value": "250+", "date": "2024-01-10"},
                    {"name": "GUS", "type": "official_registry", "value": "250", "date": "2023-12-01"}
                ]
            },
            "revenue_2023": {
                "sources": [
                    {"name": "KRS Financial Report", "type": "official_registry", "value": "50.2M PLN", "date": "2024-03-15"}
                ]
            },
            "founded": {
                "sources": [
                    {"name": "Website", "type": "company_website", "value": "1995", "date": "2024-01-15"},
                    {"name": "KRS", "type": "official_registry", "value": "1998", "date": "2024-01-20"}
                ]
            },
            "industry": {
                "sources": [
                    {"name": "KRS", "type": "official_registry", "value": "Manufacturing - Plastics", "date": "2024-01-20"},
                    {"name": "Website", "type": "company_website", "value": "Plastics Processing", "date": "2024-01-15"},
                    {"name": "LinkedIn", "type": "social_media", "value": "Manufacturing", "date": "2024-01-10"}
                ]
            },
            "market_leader": {
                "sources": [
                    {"name": "Website", "type": "company_website", "value": "Market leader in Poland", "date": "2024-01-15"}
                ]
            }
        }
    }

    response = requests.post(
        f"{BASE_URL}/analysis/fact-check",
        headers={"Authorization": f"Bearer {token}"},
        json=payload
    )

    if response.status_code == 200:
        result = response.json()
        report = result["fact_check_report"]

        print(f"✅ Fact check completed")
        print(f"\nCompany: {report['subject']}")
        print(f"Total facts checked: {report['total_facts_checked']}")
        print(f"Data quality score: {report['data_quality_score']}/100")

        print(f"\nConfidence Summary:")
        summary = report['confidence_summary']
        for level in ['high', 'medium', 'low', 'unverified']:
            count = summary[level]
            print(f"  {level.upper()}: {count}")

        print(f"\nConflicts detected: {len(report['conflicts_detected'])}")
        if report['conflicts_detected']:
            for conflict in report['conflicts_detected']:
                print(f"  - {conflict['fact']}: {len(conflict['conflicting_values'])} different values")

        print(f"\nRecommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")

        print(f"\nDetailed Facts:")
        for fact in report['verified_facts']:
            print(f"\n  • {fact['fact']}")
            print(f"    Value: {fact['verified_value']}")
            print(f"    Confidence: {fact['confidence'].upper()}")
            print(f"    Sources: {fact['source_count']} ({', '.join(fact['sources'])})")
            if fact['flags']:
                print(f"    Flags: {', '.join(fact['flags'])}")

        # Verify comprehensive results
        checks_passed = 0
        total_checks = 5

        # Check 1: Should have 5 facts
        if report['total_facts_checked'] == 5:
            print(f"\n✅ Check 1/5: Correct number of facts checked")
            checks_passed += 1
        else:
            print(f"\n❌ Check 1/5: Expected 5 facts, got {report['total_facts_checked']}")

        # Check 2: Should have at least one HIGH confidence
        if summary['high'] >= 1:
            print(f"✅ Check 2/5: Has HIGH confidence facts")
            checks_passed += 1
        else:
            print(f"❌ Check 2/5: Expected at least 1 HIGH confidence fact")

        # Check 3: Should have at least one LOW confidence (market_leader)
        if summary['low'] >= 1:
            print(f"✅ Check 3/5: Has LOW confidence facts (single source)")
            checks_passed += 1
        else:
            print(f"❌ Check 3/5: Expected at least 1 LOW confidence fact")

        # Check 4: Should detect conflicts (founded year)
        if len(report['conflicts_detected']) >= 1:
            print(f"✅ Check 4/5: Conflicts detected")
            checks_passed += 1
        else:
            print(f"❌ Check 4/5: Expected conflict detection")

        # Check 5: Quality score should be reasonable (60-90)
        if 60 <= report['data_quality_score'] <= 90:
            print(f"✅ Check 5/5: Quality score in expected range")
            checks_passed += 1
        else:
            print(f"❌ Check 5/5: Quality score {report['data_quality_score']} outside expected range")

        print(f"\n{'='*80}")
        print(f"Comprehensive test result: {checks_passed}/{total_checks} checks passed")
        return checks_passed == total_checks
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return False

def main():
    """Run all fact checker tests."""
    print("="*80)
    print("FACT CHECKER AGENT TEST SUITE - Feature #156")
    print("="*80)

    # Login
    print("\n🔑 Logging in...")
    token = login()
    if not token:
        print("❌ Cannot proceed without authentication")
        sys.exit(1)
    print(f"✅ Login successful")

    # Run tests
    results = []

    results.append(("Basic fact checking (single source)", test_fact_checker_basic(token)))
    results.append(("Official source (HIGH confidence)", test_fact_checker_official_source(token)))
    results.append(("Multiple sources cross-reference", test_fact_checker_multiple_sources(token)))
    results.append(("Conflict detection", test_conflict_detection(token)))
    results.append(("Comprehensive analysis", test_comprehensive_analysis(token)))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Feature #156 verification complete!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
