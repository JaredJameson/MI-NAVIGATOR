#!/usr/bin/env python3
"""
Test Feature #159: Router classifies query correctly
Test router agent classifies queries accurately
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

def print_header(text):
    print("\n" + "=" * 50)
    print(text)
    print("=" * 50 + "\n")

def print_step(step_num, description):
    print(f"\nStep {step_num}: {description}")
    print("-" * 50)

def test_query(query, expected_route=None):
    """Test a single query classification"""
    print(f"Query: {query}")

    try:
        response = requests.post(
            f"{BASE_URL}/analysis/classify-query",
            json={"query": query},
            timeout=10
        )

        if response.status_code != 200:
            print(f"{RED}❌ FAIL{NC} - API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return None, None, False

        data = response.json()

        primary_route = data.get("primary_route")
        confidence = data.get("confidence")
        description = data.get("description")
        alternatives = data.get("alternative_routes", [])

        print(f"Primary Route: {primary_route}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Description: {description}")

        if alternatives:
            print(f"Alternative routes: {len(alternatives)}")
            for alt in alternatives[:2]:  # Show top 2
                print(f"  - {alt['route']} ({alt['confidence']:.2f})")

        # Verify expected route
        success = True
        if expected_route:
            if primary_route == expected_route:
                print(f"{GREEN}✅ PASS{NC} - Correctly routed to {expected_route}")
            else:
                print(f"{RED}❌ FAIL{NC} - Expected {expected_route}, got: {primary_route}")
                success = False

        # Check confidence
        if confidence and confidence > 0.7:
            print(f"{GREEN}✅ PASS{NC} - Confidence is high ({confidence:.2f})")
        elif confidence:
            print(f"{YELLOW}⚠️  WARN{NC} - Confidence is below 0.7 ({confidence:.2f})")

        return primary_route, confidence, success

    except Exception as e:
        print(f"{RED}❌ ERROR{NC} - {str(e)}")
        return None, None, False

def main():
    print_header("Feature #159: Router Query Classification")

    all_passed = True
    test_results = []

    # Test Step 1 & 2: Company profile query
    print_step(1, "Submit company profile query")
    route1, conf1, pass1 = test_query(
        "Podaj informacje o firmie ABC Sp. z o.o.",
        expected_route="company_profile"
    )
    test_results.append(("Company profile query", pass1))
    all_passed = all_passed and pass1

    # Test Step 3 & 4: Market analysis query
    print_step(2, "Submit market analysis query")
    route2, conf2, pass2 = test_query(
        "Ile jest wart rynek opakowań w Polsce?",
        expected_route="market_analysis"
    )
    test_results.append(("Market analysis query", pass2))
    all_passed = all_passed and pass2

    # Test Step 5: Additional queries
    print_step(3, "Submit financial analysis query")
    route3, conf3, pass3 = test_query(
        "Jaka jest rentowność firmy XYZ?",
        expected_route="financial_analysis"
    )
    test_results.append(("Financial analysis query", pass3))
    all_passed = all_passed and pass3

    print_step(4, "Submit competitive analysis query")
    route4, conf4, pass4 = test_query(
        "Kim są główni konkurenci firmy DEF?",
        expected_route="competitive_analysis"
    )
    test_results.append(("Competitive analysis query", pass4))
    all_passed = all_passed and pass4

    print_step(5, "Submit SWOT analysis query")
    route5, conf5, pass5 = test_query(
        "Zrób analizę SWOT dla firmy GHI",
        expected_route="swot_analysis"
    )
    test_results.append(("SWOT analysis query", pass5))
    all_passed = all_passed and pass5

    # Additional test: Porter query
    print_step(6, "Submit Porter analysis query")
    route6, conf6, pass6 = test_query(
        "Przeprowadź analizę 5 sił Portera dla branży automotive",
        expected_route="porter_analysis"
    )
    test_results.append(("Porter analysis query", pass6))
    all_passed = all_passed and pass6

    # Test Step 6: Verify all confidence scores are valid
    print_step(7, "Verify confidence scores are valid")
    confidences = [conf1, conf2, conf3, conf4, conf5, conf6]
    confidences = [c for c in confidences if c is not None]

    if confidences:
        all_valid = all(0 <= c <= 1 for c in confidences)
        avg_confidence = sum(confidences) / len(confidences)

        print(f"Average confidence: {avg_confidence:.2f}")
        print(f"Min confidence: {min(confidences):.2f}")
        print(f"Max confidence: {max(confidences):.2f}")

        if all_valid:
            print(f"{GREEN}✅ PASS{NC} - All confidence scores in valid range [0, 1]")
        else:
            print(f"{RED}❌ FAIL{NC} - Some confidence scores out of range")
            all_passed = False
    else:
        print(f"{RED}❌ FAIL{NC} - No valid confidence scores received")
        all_passed = False

    # Summary
    print_header("TEST SUMMARY")

    print("Test Results:")
    for test_name, passed in test_results:
        status = f"{GREEN}✅ PASS{NC}" if passed else f"{RED}❌ FAIL{NC}"
        print(f"  {test_name}: {status}")

    print(f"\nTotal: {sum(1 for _, p in test_results if p)}/{len(test_results)} tests passed")

    if all_passed:
        print(f"\n{GREEN}{'=' * 50}")
        print("✅ ALL TESTS PASSED - Feature #159 VERIFIED")
        print(f"{'=' * 50}{NC}")
        return 0
    else:
        print(f"\n{RED}{'=' * 50}")
        print("❌ SOME TESTS FAILED - Feature #159 NEEDS WORK")
        print(f"{'=' * 50}{NC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
