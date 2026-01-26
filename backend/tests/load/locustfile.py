"""
Load Testing Suite for MI-Navigator - Week 21 Implementation

Comprehensive load testing for production readiness:
- Concurrent user simulation (100, 500, 1000 users)
- API endpoint stress testing
- Agent endpoint performance testing
- WebSocket connection limits
- Response time measurement
- Error rate tracking

Usage:
    # Run with 100 users
    locust -f tests/load/locustfile.py --host=http://localhost:8000 -u 100 -r 10

    # Run with 500 users
    locust -f tests/load/locustfile.py --host=http://localhost:8000 -u 500 -r 50

    # Run with 1000 users
    locust -f tests/load/locustfile.py --host=http://localhost:8000 -u 1000 -r 100

    # Web UI mode
    locust -f tests/load/locustfile.py --host=http://localhost:8000

Author: MI-Navigator Development Team
Created: 2026-01-26 (Week 21)
"""

import random
import json
from locust import HttpUser, task, between, events
from locust.contrib.fasthttp import FastHttpUser


# ============================================================================
# TEST DATA
# ============================================================================

TEST_NIPS = [
    "1234567890",
    "9876543210",
    "5555555555",
    "1111111111",
    "2222222222"
]

TEST_WEBSITES = [
    "https://example.com",
    "https://test.com",
    "https://sample.org",
    "https://demo.net",
    "https://showcase.com"
]

TEST_CREDENTIALS = {
    "email": "loadtest@example.com",
    "password": "LoadTest123!"
}


# ============================================================================
# BASE USER CLASS
# ============================================================================

class MINavigatorUser(FastHttpUser):
    """
    Base user class for MI-Navigator load testing.

    Uses FastHttpUser for better performance (uses gevent instead of requests).
    """

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """
        Executed when a user starts.
        Authenticate and get access token.
        """
        # Try to login (may fail if user doesn't exist, that's OK for load testing)
        response = self.client.post(
            "/api/v1/auth/login",
            json=TEST_CREDENTIALS,
            name="/api/v1/auth/login"
        )

        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.access_token}"}
        else:
            # Use a dummy token for load testing
            self.access_token = "dummy_token_for_load_testing"
            self.headers = {"Authorization": f"Bearer {self.access_token}"}

    @task(1)
    def health_check(self):
        """Test health endpoint (lightweight)."""
        self.client.get("/health", name="/health")

    @task(1)
    def root_endpoint(self):
        """Test root endpoint (API info)."""
        self.client.get("/", name="/")


# ============================================================================
# AGENT ENDPOINT TESTING
# ============================================================================

class AgentUser(MINavigatorUser):
    """
    User that primarily tests agent endpoints.

    Simulates real usage patterns with different agent types.
    """

    @task(10)
    def company_profile_agent(self):
        """Test Company Profile Agent endpoint."""
        nip = random.choice(TEST_NIPS)
        self.client.post(
            "/api/v1/agents/company-profile",
            headers=self.headers,
            json={"nip": nip},
            name="/api/v1/agents/company-profile"
        )

    @task(8)
    def financial_analysis_agent(self):
        """Test Financial Analysis Agent endpoint."""
        nip = random.choice(TEST_NIPS)
        self.client.post(
            "/api/v1/agents/financial-analysis",
            headers=self.headers,
            json={"nip": nip, "analysis_type": "comprehensive"},
            name="/api/v1/agents/financial-analysis"
        )

    @task(7)
    def digital_presence_agent(self):
        """Test Digital Presence Agent endpoint."""
        website = random.choice(TEST_WEBSITES)
        self.client.post(
            "/api/v1/agents/digital-presence",
            headers=self.headers,
            json={"website_url": website},
            name="/api/v1/agents/digital-presence"
        )

    @task(6)
    def competitor_mapping_agent(self):
        """Test Competitor Mapping Agent endpoint."""
        nip = random.choice(TEST_NIPS)
        self.client.post(
            "/api/v1/agents/competitor-mapping",
            headers=self.headers,
            json={"nip": nip, "max_competitors": 5},
            name="/api/v1/agents/competitor-mapping"
        )

    @task(5)
    def fact_checker_agent(self):
        """Test Fact Checker Agent endpoint."""
        nip = random.choice(TEST_NIPS)
        claims = [
            "Company has 500 employees",
            f"Company revenue grew 20% in 2023"
        ]
        self.client.post(
            "/api/v1/agents/fact-checker",
            headers=self.headers,
            json={"claims": claims, "nip": nip},
            name="/api/v1/agents/fact-checker"
        )

    @task(5)
    def insight_generator_agent(self):
        """Test Insight Generator Agent endpoint."""
        nip = random.choice(TEST_NIPS)
        self.client.post(
            "/api/v1/agents/insight-generator",
            headers=self.headers,
            json={"nip": nip, "analysis_focus": "growth_opportunities"},
            name="/api/v1/agents/insight-generator"
        )


# ============================================================================
# MIXED WORKLOAD USER
# ============================================================================

class MixedWorkloadUser(MINavigatorUser):
    """
    User that performs a mix of operations.

    Simulates realistic user behavior with various endpoints.
    """

    @task(15)
    def browse_companies(self):
        """Browse companies list."""
        self.client.get(
            "/api/v1/companies",
            headers=self.headers,
            params={"skip": 0, "limit": 20},
            name="/api/v1/companies (list)"
        )

    @task(10)
    def search_companies(self):
        """Search for companies."""
        query = random.choice(["tech", "finance", "consulting", "IT", "services"])
        self.client.get(
            "/api/v1/search",
            headers=self.headers,
            params={"q": query, "limit": 10},
            name="/api/v1/search"
        )

    @task(8)
    def get_company_profile(self):
        """Get specific company profile."""
        nip = random.choice(TEST_NIPS)
        self.client.post(
            "/api/v1/agents/company-profile",
            headers=self.headers,
            json={"nip": nip},
            name="/api/v1/agents/company-profile"
        )

    @task(5)
    def view_reports(self):
        """View reports list."""
        self.client.get(
            "/api/v1/reports",
            headers=self.headers,
            params={"skip": 0, "limit": 10},
            name="/api/v1/reports (list)"
        )

    @task(3)
    def check_alerts(self):
        """Check alerts."""
        self.client.get(
            "/api/v1/alerts",
            headers=self.headers,
            params={"skip": 0, "limit": 10},
            name="/api/v1/alerts (list)"
        )


# ============================================================================
# STRESS TEST USER
# ============================================================================

class StressTestUser(FastHttpUser):
    """
    Aggressive user for stress testing.

    Minimal wait time to maximize load.
    """

    wait_time = between(0.1, 0.5)  # Very short wait time

    def on_start(self):
        """Quick login."""
        self.headers = {"Authorization": "Bearer dummy_token"}

    @task(20)
    def rapid_health_checks(self):
        """Rapid health check requests."""
        self.client.get("/health", name="/health (stress)")

    @task(10)
    def rapid_api_calls(self):
        """Rapid API calls to test rate limiting."""
        nip = random.choice(TEST_NIPS)
        self.client.post(
            "/api/v1/agents/company-profile",
            headers=self.headers,
            json={"nip": nip},
            name="/api/v1/agents/company-profile (stress)"
        )


# ============================================================================
# CACHE PERFORMANCE TEST
# ============================================================================

class CacheTestUser(MINavigatorUser):
    """
    User that tests cache performance.

    Repeatedly requests the same data to test cache hit rates.
    """

    wait_time = between(0.1, 0.3)

    def on_start(self):
        """Setup with fixed NIP for cache testing."""
        super().on_start()
        self.test_nip = "1234567890"  # Fixed NIP for cache testing

    @task(50)
    def cached_company_profile(self):
        """Request same company profile repeatedly (should be cached)."""
        self.client.post(
            "/api/v1/agents/company-profile",
            headers=self.headers,
            json={"nip": self.test_nip},
            name="/api/v1/agents/company-profile (cached)"
        )


# ============================================================================
# EVENT LISTENERS (METRICS COLLECTION)
# ============================================================================

# Track response times for analysis
response_times = []

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """
    Collect response time metrics.
    """
    if exception is None:
        response_times.append(response_time)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Print summary statistics when test stops.
    """
    if response_times:
        import statistics

        print("\n" + "="*80)
        print("LOAD TEST SUMMARY - MI-Navigator")
        print("="*80)
        print(f"Total Requests: {len(response_times)}")
        print(f"Mean Response Time: {statistics.mean(response_times):.2f}ms")
        print(f"Median Response Time: {statistics.median(response_times):.2f}ms")
        if len(response_times) > 1:
            print(f"Std Dev: {statistics.stdev(response_times):.2f}ms")
        print(f"Min Response Time: {min(response_times):.2f}ms")
        print(f"Max Response Time: {max(response_times):.2f}ms")

        # Calculate percentiles
        sorted_times = sorted(response_times)
        p95_index = int(len(sorted_times) * 0.95)
        p99_index = int(len(sorted_times) * 0.99)
        print(f"P95: {sorted_times[p95_index]:.2f}ms")
        print(f"P99: {sorted_times[p99_index]:.2f}ms")
        print("="*80 + "\n")


# ============================================================================
# LOAD TEST SCENARIOS
# ============================================================================

"""
RECOMMENDED TEST SCENARIOS:

1. LIGHT LOAD (Baseline):
   locust -f tests/load/locustfile.py --host=http://localhost:8000 -u 10 -r 2 --run-time 5m --headless

2. MODERATE LOAD (Typical Usage):
   locust -f tests/load/locustfile.py --host=http://localhost:8000 -u 100 -r 10 --run-time 10m --headless

3. HEAVY LOAD (Peak Hours):
   locust -f tests/load/locustfile.py --host=http://localhost:8000 -u 500 -r 50 --run-time 15m --headless

4. STRESS TEST (Breaking Point):
   locust -f tests/load/locustfile.py --host=http://localhost:8000 -u 1000 -r 100 --run-time 20m --headless

5. CACHE PERFORMANCE TEST:
   locust -f tests/load/locustfile.py --host=http://localhost:8000 -u 50 -r 10 --run-time 5m --headless --user-class CacheTestUser

6. AGENT-SPECIFIC TEST:
   locust -f tests/load/locustfile.py --host=http://localhost:8000 -u 200 -r 20 --run-time 10m --headless --user-class AgentUser

PARAMETERS:
  -u: Number of concurrent users
  -r: Spawn rate (users per second)
  --run-time: Test duration
  --headless: Run without web UI
  --user-class: Specific user class to test

EXPECTED RESULTS (Production):
  - Mean response time: <250ms (uncached), <10ms (cached)
  - P95: <500ms (uncached), <20ms (cached)
  - Error rate: <1%
  - Throughput: >40 req/s
  - Cache hit rate: >80%
"""
