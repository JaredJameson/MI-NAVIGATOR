#!/usr/bin/env python3
"""
Agent Deployment Validation Script - Phase 3 Week 31 Day 2
============================================================

Validates that agent deployment endpoints are working correctly before
deploying to staging or production.

Usage:
    python scripts/validate_agent_deployment.py [--host localhost] [--port 8000]

Tests:
    1. Health check endpoints (/agents/health, /agents/health/{agent_name})
    2. Prometheus metrics endpoint (/agents/metrics)
    3. Market Search Agent endpoint (/agents/market-search)
    4. Response validation and error handling

Author: Claude Code SuperClaude
Created: 2026-02-01 (Phase 3 Week 31 Day 2)
"""

import argparse
import sys
import time
import requests
from typing import Dict, List, Tuple


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


class AgentDeploymentValidator:
    """Validates agent deployment endpoints."""

    def __init__(self, host: str = "localhost", port: int = 8000):
        self.base_url = f"http://{host}:{port}"
        self.api_prefix = "/api/v1"
        self.results: List[Tuple[str, bool, str]] = []

    def print_header(self, text: str):
        """Print formatted header."""
        print(f"\n{Colors.BLUE}{'=' * 80}{Colors.NC}")
        print(f"{Colors.BLUE}{text}{Colors.NC}")
        print(f"{Colors.BLUE}{'=' * 80}{Colors.NC}\n")

    def print_success(self, text: str):
        """Print success message."""
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {text}")

    def print_error(self, text: str):
        """Print error message."""
        print(f"{Colors.RED}[ERROR]{Colors.NC} {text}")

    def print_info(self, text: str):
        """Print info message."""
        print(f"{Colors.YELLOW}[INFO]{Colors.NC} {text}")

    def record_result(self, test_name: str, passed: bool, message: str):
        """Record test result."""
        self.results.append((test_name, passed, message))
        if passed:
            self.print_success(f"{test_name}: {message}")
        else:
            self.print_error(f"{test_name}: {message}")

    def test_server_health(self) -> bool:
        """Test if server is running."""
        try:
            url = f"{self.base_url}{self.api_prefix}/system/health"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                self.record_result("Server Health", True, "Server is running and healthy")
                return True
            else:
                # Try root endpoint as fallback
                response = requests.get(f"{self.base_url}/", timeout=5)
                if response.status_code in [200, 404]:  # 404 is ok, means server is running
                    self.record_result("Server Health", True, "Server is running")
                    return True

            self.record_result("Server Health", False, f"Unexpected status code: {response.status_code}")
            return False

        except requests.exceptions.ConnectionError:
            self.record_result("Server Health", False, "Cannot connect to server. Is it running?")
            return False
        except Exception as e:
            self.record_result("Server Health", False, f"Error: {str(e)}")
            return False

    def test_all_agents_health(self) -> bool:
        """Test /agents/health endpoint."""
        try:
            url = f"{self.base_url}{self.api_prefix}/agents/health"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Validate response structure
                required_fields = ['timestamp', 'overall_status', 'agents', 'total_requests_24h', 'average_quality_score']
                missing = [f for f in required_fields if f not in data]

                if missing:
                    self.record_result("All Agents Health", False, f"Missing fields: {missing}")
                    return False

                # Validate agents
                expected_agents = ['market_search', 'financial_analysis', 'competitor_mapping',
                                  'company_profile', 'digital_presence']
                agents_data = data.get('agents', {})

                found_agents = list(agents_data.keys())
                if set(found_agents) == set(expected_agents):
                    avg_quality = data['average_quality_score']
                    self.record_result("All Agents Health", True,
                                      f"All 5 agents reported, avg quality: {avg_quality:.1%}")
                    return True
                else:
                    missing_agents = set(expected_agents) - set(found_agents)
                    self.record_result("All Agents Health", False, f"Missing agents: {missing_agents}")
                    return False
            else:
                self.record_result("All Agents Health", False,
                                  f"HTTP {response.status_code}: {response.text[:100]}")
                return False

        except Exception as e:
            self.record_result("All Agents Health", False, f"Error: {str(e)}")
            return False

    def test_individual_agent_health(self, agent_name: str) -> bool:
        """Test /agents/health/{agent_name} endpoint."""
        try:
            url = f"{self.base_url}{self.api_prefix}/agents/health/{agent_name}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Validate response structure
                required_fields = ['agent_name', 'status', 'quality_score', 'llm_enhancement_enabled']
                missing = [f for f in required_fields if f not in data]

                if missing:
                    self.record_result(f"{agent_name} Health", False, f"Missing fields: {missing}")
                    return False

                quality = data['quality_score']
                status = data['status']
                llm_enabled = data['llm_enhancement_enabled']

                self.record_result(f"{agent_name} Health", True,
                                  f"Quality: {quality:.1%}, Status: {status}, LLM: {llm_enabled}")
                return True
            else:
                self.record_result(f"{agent_name} Health", False,
                                  f"HTTP {response.status_code}: {response.text[:100]}")
                return False

        except Exception as e:
            self.record_result(f"{agent_name} Health", False, f"Error: {str(e)}")
            return False

    def test_prometheus_metrics(self) -> bool:
        """Test /agents/metrics endpoint."""
        try:
            url = f"{self.base_url}{self.api_prefix}/agents/metrics"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                metrics_text = response.text

                # Validate Prometheus format and expected metrics
                expected_metrics = [
                    'mi_navigator_agent_requests_total',
                    'mi_navigator_agent_response_seconds',
                    'mi_navigator_agent_quality_score',
                    'mi_navigator_agent_llm_enhancement_enabled'
                ]

                found_metrics = [m for m in expected_metrics if m in metrics_text]

                if len(found_metrics) == len(expected_metrics):
                    lines = len(metrics_text.split('\n'))
                    self.record_result("Prometheus Metrics", True,
                                      f"All {len(expected_metrics)} metrics present ({lines} lines)")
                    return True
                else:
                    missing = set(expected_metrics) - set(found_metrics)
                    self.record_result("Prometheus Metrics", False, f"Missing metrics: {missing}")
                    return False
            else:
                self.record_result("Prometheus Metrics", False,
                                  f"HTTP {response.status_code}: {response.text[:100]}")
                return False

        except Exception as e:
            self.record_result("Prometheus Metrics", False, f"Error: {str(e)}")
            return False

    def test_market_search_endpoint(self) -> bool:
        """Test /agents/market-search endpoint."""
        try:
            url = f"{self.base_url}{self.api_prefix}/agents/market-search"

            # Test request payload
            payload = {
                "query": "software development companies in Warsaw",
                "max_results": 10,
                "include_advanced_features": True,
                "use_cache": False
            }

            self.print_info("Testing Market Search Agent endpoint (may take 10-30 seconds)...")
            response = requests.post(url, json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()

                # Validate response structure
                required_fields = ['success', 'query', 'total_results', 'companies', 'quality_score']
                missing = [f for f in required_fields if f not in data]

                if missing:
                    self.record_result("Market Search Endpoint", False, f"Missing fields: {missing}")
                    return False

                # Validate advanced features (Week 29)
                advanced_fields = ['market_sizing', 'trend_analysis', 'geographic_insights',
                                  'industry_characteristics', 'competitive_density']
                has_advanced = sum(1 for f in advanced_fields if data.get(f))

                success = data['success']
                total = data['total_results']
                quality = data['quality_score']
                exec_time = data.get('execution_time_ms', 0)

                if success:
                    self.record_result("Market Search Endpoint", True,
                                      f"{total} results, quality: {quality:.1%}, {has_advanced}/5 advanced features, {exec_time}ms")
                    return True
                else:
                    self.record_result("Market Search Endpoint", False, "Request returned success=false")
                    return False
            elif response.status_code == 401:
                self.record_result("Market Search Endpoint", False,
                                  "Authentication required (expected for production)")
                return False
            else:
                self.record_result("Market Search Endpoint", False,
                                  f"HTTP {response.status_code}: {response.text[:200]}")
                return False

        except requests.exceptions.Timeout:
            self.record_result("Market Search Endpoint", False, "Request timeout (>60s)")
            return False
        except Exception as e:
            self.record_result("Market Search Endpoint", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self) -> bool:
        """Run all validation tests."""
        self.print_header("Agent Deployment Validation - Phase 3 Week 31 Day 2")

        self.print_info(f"Testing against: {self.base_url}")
        self.print_info("Running comprehensive endpoint validation...\n")

        # Test 1: Server health
        self.print_header("Test 1: Server Health Check")
        if not self.test_server_health():
            self.print_error("\nServer is not running. Please start the backend server first.")
            self.print_info("Start command: uvicorn app.main:app --reload --port 8000")
            return False

        # Test 2: All agents health
        self.print_header("Test 2: All Agents Health Endpoint")
        self.test_all_agents_health()

        # Test 3: Individual agent health
        self.print_header("Test 3: Individual Agent Health Endpoints")
        agents = ['market_search', 'financial_analysis', 'competitor_mapping',
                 'company_profile', 'digital_presence']
        for agent in agents:
            self.test_individual_agent_health(agent)

        # Test 4: Prometheus metrics
        self.print_header("Test 4: Prometheus Metrics Endpoint")
        self.test_prometheus_metrics()

        # Test 5: Market Search endpoint
        self.print_header("Test 5: Market Search Agent Endpoint")
        self.test_market_search_endpoint()

        # Summary
        self.print_summary()

        # Return overall success
        passed = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)
        return passed == total

    def print_summary(self):
        """Print test results summary."""
        self.print_header("Test Results Summary")

        passed = sum(1 for _, success, _ in self.results if success)
        failed = len(self.results) - passed
        pass_rate = (passed / len(self.results) * 100) if self.results else 0

        print(f"\nTotal Tests: {len(self.results)}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.NC}")
        print(f"{Colors.RED}Failed: {failed}{Colors.NC}")
        print(f"Pass Rate: {pass_rate:.1f}%\n")

        if failed > 0:
            print(f"{Colors.YELLOW}Failed Tests:{Colors.NC}")
            for name, success, message in self.results:
                if not success:
                    print(f"  - {name}: {message}")
            print()

        if pass_rate == 100:
            self.print_success("🎉 All tests passed! Agent deployment is ready.")
        elif pass_rate >= 80:
            self.print_info("⚠️  Most tests passed, but some issues detected.")
        else:
            self.print_error("❌ Multiple test failures. Agent deployment needs fixes.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Validate agent deployment endpoints')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')

    args = parser.parse_args()

    validator = AgentDeploymentValidator(host=args.host, port=args.port)
    success = validator.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
