# Integration Test Plan - Phase 3 Week 31

**Status**: 📋 **READY FOR EXECUTION**
**Version**: 1.0
**Date**: 2026-02-01
**Scope**: Integration testing for Phase 2 LLM-enhanced agents

---

## 🎯 Test Objectives

### Primary Goals

1. **Cross-Agent Data Flow**: Validate data consistency across agent workflows
2. **Performance Under Load**: Ensure system stability under realistic workloads
3. **LLM Enhancement Integration**: Verify AI enhancement works in multi-agent scenarios
4. **Error Recovery**: Test graceful degradation and error handling
5. **Monitoring Validation**: Confirm metrics accuracy and completeness

### Success Criteria

- ✅ All integration tests pass (100% success rate)
- ✅ p95 response time <5 seconds for multi-agent workflows
- ✅ Error rate <1% under normal load
- ✅ Graceful degradation when LLM service unavailable
- ✅ Prometheus metrics accurately reflect system behavior

---

## 🧪 Test Suites

### Suite 1: Cross-Agent Workflows

#### Test 1.1: Complete Company Analysis Workflow

**Description**: Multi-agent workflow for comprehensive company analysis

**Agents Involved**: All 5 Phase 2 agents

**Test Steps**:
```python
# 1. Start with Company Profile Agent
company_data = company_profile_agent.execute("Company XYZ")
assert company_data["confidence_score"] >= 0.85

# 2. Financial Analysis using company data
financial_data = financial_analysis_agent.execute(company_data["nip"])
assert financial_data["confidence_score"] >= 0.85

# 3. Digital Presence analysis
digital_data = digital_presence_agent.execute(company_data["website"])
assert digital_data["confidence_score"] >= 0.85

# 4. Competitor mapping
competitor_data = competitor_mapping_agent.execute(company_data["krs"])
assert len(competitor_data["competitors"]) > 0

# 5. Market search for similar companies
market_data = market_search_agent.search(
    f"{company_data['industry']} companies in {company_data['region']}"
)
assert market_data["total_results"] > 0
```

**Expected Results**:
- All agents return data successfully
- Confidence scores ≥85% for all agents
- Cross-references between agents are consistent
- Total execution time <30 seconds
- No data inconsistencies detected

**Metrics to Monitor**:
- `agent_requests_total` (all 5 agents called)
- `agent_response_time` (p95 <5s per agent)
- `agent_errors_total` (0 errors expected)
- `agent_llm_calls_total` (5 LLM calls if available)

---

#### Test 1.2: Market Research Workflow

**Description**: Market discovery and enrichment pipeline

**Agents Involved**: Market Search, Company Profile, Financial Analysis, Digital Presence

**Test Steps**:
```python
# 1. Discover companies
companies = market_search_agent.search(
    "fintech companies in Warsaw",
    max_results=10
)
assert companies["total_results"] >= 10

# 2. Enrich each company
for company in companies["companies"][:5]:  # Test first 5
    # Company profile
    profile = company_profile_agent.execute(company["nip"])
    assert profile["confidence_score"] >= 0.75

    # Financial analysis (if data available)
    if company.get("has_financial_data"):
        financial = financial_analysis_agent.execute(company["nip"])
        assert financial["confidence_score"] >= 0.75

    # Digital presence
    if company.get("website"):
        digital = digital_presence_agent.execute(company["website"])
        assert digital["confidence_score"] >= 0.75
```

**Expected Results**:
- Market search discovers ≥10 companies
- Profile enrichment succeeds for all companies
- Financial/digital data available for ≥50% of companies
- Average enrichment time <5s per company
- Total workflow time <60 seconds

**Performance Targets**:
- Market search: <15s
- Profile enrichment (per company): <2s
- Financial analysis (per company): <3s
- Digital presence (per company): <3s

---

#### Test 1.3: Competitor Analysis Chain

**Description**: Deep competitor analysis using multiple agents

**Agents Involved**: Company Profile, Competitor Mapping, Market Search, Financial Analysis

**Test Steps**:
```python
# 1. Get target company
target = company_profile_agent.execute("Target Company KRS")
assert target["confidence_score"] >= 0.85

# 2. Map competitors
competitors = competitor_mapping_agent.execute(target["krs"])
assert len(competitors["competitors"]) >= 3

# 3. Search for additional competitors
additional = market_search_agent.search(
    f"{target['industry']} companies",
    max_results=20
)

# 4. Financial comparison
for competitor in competitors["competitors"][:3]:
    financial = financial_analysis_agent.execute(competitor["nip"])
    assert financial["confidence_score"] >= 0.70

    # Compare with target
    assert "ratios" in financial
    # Store for comparison matrix
```

**Expected Results**:
- Competitor mapping identifies ≥3 competitors
- Market search finds ≥20 similar companies
- Financial comparison succeeds for all competitors
- Competitive insights include SWOT and Porter's Five Forces
- Total execution time <45 seconds

---

### Suite 2: Performance & Load Testing

#### Test 2.1: Concurrent User Simulation

**Description**: Simulate 50 concurrent users making requests

**Load Profile**:
```yaml
users: 50
duration: 5 minutes
ramp_up: 30 seconds

request_distribution:
  market_search: 40%      # Most common use case
  company_profile: 25%
  financial_analysis: 15%
  digital_presence: 10%
  competitor_mapping: 10%
```

**Test Execution**:
```python
# Using Locust load testing framework
from locust import HttpUser, task, between

class MINavigatorUser(HttpUser):
    wait_time = between(1, 3)

    @task(4)  # 40% weight
    def market_search(self):
        self.client.post("/api/v1/agents/market-search", json={
            "query": "software companies in Poland",
            "max_results": 50
        })

    @task(2)  # 25% weight
    def company_profile(self):
        self.client.post("/api/v1/agents/company-profile", json={
            "target": "0000123456"  # KRS number
        })

    @task(2)  # 15% weight
    def financial_analysis(self):
        self.client.post("/api/v1/agents/financial-analysis", json={
            "target": "1234567890"  # NIP number
        })
```

**Success Criteria**:
- All requests complete successfully (error rate <1%)
- p50 response time <3 seconds
- p95 response time <5 seconds
- p99 response time <10 seconds
- No memory leaks detected
- CPU usage <80% average
- Database connection pool healthy

**Metrics to Monitor**:
- Request throughput (requests/second)
- Response time distribution (p50, p95, p99)
- Error rates by agent
- Active requests gauge (peak and average)
- Database query performance
- Cache hit rates

---

#### Test 2.2: Sustained Load Test

**Description**: 10 requests/second for 10 minutes

**Load Profile**:
```yaml
rate: 10 req/s
duration: 10 minutes
target_agent: market_search  # Focus on highest quality agent
```

**Test Configuration**:
```python
# Constant load for 10 minutes
total_requests = 10 * 60 * 10  # 6000 requests
queries = [
    "tech companies in Warsaw",
    "manufacturing in Mazowieckie",
    "retail companies in Krakow",
    "healthcare in Wroclaw",
    "fintech startups"
]

for i in range(total_requests):
    query = queries[i % len(queries)]
    response = market_search_agent.search(query)

    # Validate response
    assert response["success"] == True
    assert response["quality_score"] >= 0.90

    # Check for degradation
    if i % 100 == 0:
        assert response_time < baseline_response_time * 1.5
```

**Success Criteria**:
- Response times remain stable (no degradation)
- No memory leaks (memory usage stable)
- Error rate <0.5%
- LLM enhancement success rate >95%
- Cache hit rate >30% (after warm-up)
- Database connection pool stable

---

#### Test 2.3: Spike Test

**Description**: Sudden burst of 100 concurrent requests

**Load Profile**:
```yaml
normal_load: 5 req/s
spike_load: 100 concurrent requests
spike_duration: 30 seconds
recovery_time: 60 seconds
```

**Test Execution**:
```python
# Phase 1: Normal load (baseline)
for i in range(150):  # 30 seconds @ 5 req/s
    make_request()
    time.sleep(0.2)

# Phase 2: Spike
threads = []
for i in range(100):
    t = threading.Thread(target=make_request)
    threads.append(t)
    t.start()

for t in threads:
    t.join()

# Phase 3: Recovery
for i in range(300):  # 60 seconds @ 5 req/s
    make_request()
    time.sleep(0.2)
```

**Success Criteria**:
- System handles spike without crashes
- Error rate during spike <5%
- System recovers to baseline performance within 60s
- No requests timeout (all complete within 60s)
- Graceful degradation visible in metrics
- No permanent performance degradation

---

### Suite 3: LLM Enhancement Integration

#### Test 3.1: LLM Service Availability

**Description**: Test behavior with and without LLM service

**Test Cases**:

**Case 3.1.1: LLM Service Available**
```python
# All agents with LLM enhancement
for agent_name, agent in all_agents.items():
    result = agent.execute(test_data)

    # Verify LLM enhancement
    assert result.get("llm_insights") is not None
    assert result.get("llm_quality_score") >= 0.7

    # Verify 70/30 formula
    base_confidence = result.get("base_confidence")
    llm_quality = result.get("llm_quality_score")
    expected_confidence = base_confidence * 0.7 + llm_quality * 0.3
    assert abs(result["confidence_score"] - expected_confidence) < 0.01
```

**Case 3.1.2: LLM Service Unavailable**
```python
# Disable ClaudeService
with mock.patch('app.services.claude_service.ClaudeService') as mock_service:
    mock_service.return_value = None

    for agent_name, agent in all_agents.items():
        result = agent.execute(test_data)

        # Verify graceful degradation
        assert result["success"] == True
        assert result.get("llm_insights") is None

        # Confidence should be base only
        assert result["confidence_score"] == result["base_confidence"]

        # Quality still acceptable (70-80% range)
        assert 0.70 <= result["confidence_score"] <= 0.85
```

**Expected Results**:
- With LLM: All agents return enhanced insights
- Without LLM: All agents return base data successfully
- Confidence scores reflect LLM availability
- No errors or exceptions thrown
- Metrics accurately track LLM usage

---

#### Test 3.2: LLM Quality Variations

**Description**: Test confidence calculation with varying LLM quality

**Test Cases**:

**High Quality LLM (>0.8)**:
```python
# Mock high quality LLM response
llm_response = {
    "insights": {...},
    "quality_score": 0.9
}

result = agent.execute(test_data, llm_insights=llm_response)

# Expect confidence boost
base = result["base_confidence"]  # e.g., 0.75
expected = base * 0.7 + 0.9 * 0.3  # 0.75*0.7 + 0.9*0.3 = 0.525 + 0.27 = 0.795
assert abs(result["confidence_score"] - expected) < 0.01
```

**Low Quality LLM (<0.4)**:
```python
# Mock low quality LLM response
llm_response = {
    "insights": {...},
    "quality_score": 0.3
}

result = agent.execute(test_data, llm_insights=llm_response)

# Expect confidence penalty
base = result["base_confidence"]  # e.g., 0.75
expected = base * 0.7 + 0.3 * 0.3  # 0.75*0.7 + 0.3*0.3 = 0.525 + 0.09 = 0.615
assert abs(result["confidence_score"] - expected) < 0.01
```

**Expected Results**:
- High LLM quality boosts confidence
- Low LLM quality applies penalty
- Formula consistently applied
- Confidence scores remain in 0-1 range

---

#### Test 3.3: LLM Error Handling

**Description**: Test error recovery for various LLM failure modes

**Test Cases**:

**Case 3.3.1: Invalid JSON Response**
```python
# Mock invalid JSON from LLM
with mock.patch('claude_service.enhance') as mock_enhance:
    mock_enhance.return_value = "Invalid JSON {not valid}"

    result = agent.execute(test_data)

    assert result["success"] == True
    assert result.get("llm_insights") is None
    assert result["confidence_score"] == result["base_confidence"]
```

**Case 3.3.2: LLM Timeout**
```python
# Mock LLM timeout
with mock.patch('claude_service.enhance') as mock_enhance:
    mock_enhance.side_effect = TimeoutError("LLM request timeout")

    result = agent.execute(test_data)

    assert result["success"] == True
    assert "timeout" in result.get("warnings", [])
```

**Case 3.3.3: Rate Limit Exceeded**
```python
# Mock rate limit error
with mock.patch('claude_service.enhance') as mock_enhance:
    mock_enhance.side_effect = RateLimitError("Too many requests")

    result = agent.execute(test_data)

    assert result["success"] == True
    assert result.get("llm_insights") is None
```

---

### Suite 4: Monitoring & Metrics Validation

#### Test 4.1: Prometheus Metrics Accuracy

**Description**: Verify Prometheus metrics match actual system behavior

**Test Steps**:
```python
# 1. Reset metrics (restart or use test environment)
reset_prometheus_metrics()

# 2. Execute known number of requests
for i in range(100):
    agent_requests = {
        "market_search": 40,
        "financial_analysis": 25,
        "company_profile": 20,
        "digital_presence": 10,
        "competitor_mapping": 5
    }

# 3. Query Prometheus metrics
metrics = get_prometheus_metrics()

# 4. Validate counters
assert metrics["agent_requests_total{agent_name='market_search'}"] == 40
assert metrics["agent_requests_total{agent_name='financial_analysis'}"] == 25
# ... etc

# 5. Validate response time histograms
market_search_p95 = metrics["agent_response_time{agent_name='market_search', quantile='0.95'}"]
assert market_search_p95 < 5.0  # p95 <5 seconds
```

**Metrics to Validate**:
- `agent_requests_total` (counters accurate)
- `agent_response_time` (histograms correct)
- `agent_active_requests` (gauge reflects reality)
- `agent_quality_score` (Phase 2 baselines maintained)
- `agent_errors_total` (error tracking accurate)
- `agent_llm_calls_total` (LLM usage tracked)

---

#### Test 4.2: Health Check Endpoints

**Description**: Validate health check accuracy

**Test Steps**:
```python
# 1. All agents healthy
health = requests.get("/api/v1/agents/health").json()
assert health["overall_status"] == "healthy"
assert len(health["agents"]) == 5
for agent_name, agent_health in health["agents"].items():
    assert agent_health["status"] == "healthy"
    assert agent_health["quality_score"] >= 0.85

# 2. Simulate agent degradation (high error rate)
simulate_errors("market_search", error_rate=0.15)
time.sleep(5)

health = requests.get("/api/v1/agents/health").json()
assert health["overall_status"] == "degraded"
assert health["agents"]["market_search"]["status"] == "degraded"

# 3. Individual agent health
market_health = requests.get("/api/v1/agents/health/market_search").json()
assert market_health["agent_name"] == "market_search"
assert market_health["error_rate_24h"] > 0.10
```

**Expected Results**:
- Health status accurately reflects agent state
- Overall status aggregates correctly
- Individual agent metrics accurate
- Quality scores from Phase 2 maintained

---

### Suite 5: Error Recovery & Resilience

#### Test 5.1: Database Connection Failures

**Description**: Test agent behavior when database unavailable

**Test Steps**:
```python
# 1. Simulate database failure
with mock.patch('database.get_connection') as mock_db:
    mock_db.side_effect = DatabaseConnectionError("Connection failed")

    # 2. Execute agents
    for agent in all_agents.values():
        result = agent.execute(test_data)

        # 3. Verify graceful degradation
        if agent.requires_database:
            assert result["success"] == False
            assert "database" in result["error"].lower()
        else:
            assert result["success"] == True  # Some agents may not need DB
```

**Expected Results**:
- Agents gracefully handle database failures
- Error messages are clear and actionable
- No unhandled exceptions
- Metrics track database errors

---

#### Test 5.2: Network Timeout Scenarios

**Description**: Test behavior with slow/unreachable external services

**Test Cases**:

**Case 5.2.1: Slow External API**
```python
# Mock slow external service
with mock.patch('httpx.AsyncClient.get') as mock_get:
    mock_get.side_effect = asyncio.TimeoutError()

    result = digital_presence_agent.execute("https://example.com")

    assert result["success"] == True  # Partial success
    assert "timeout" in result.get("warnings", [])
    assert result["confidence_score"] < 0.85  # Reduced confidence
```

**Case 5.2.2: Unreachable KRS/GUS Services**
```python
# Mock KRS service down
with mock.patch('krs_client.search') as mock_krs:
    mock_krs.side_effect = ConnectionError("Service unavailable")

    result = company_profile_agent.execute("Company XYZ")

    # Should fallback to alternative data sources
    assert result["success"] == True
    assert result.get("data_sources") == ["cache", "fallback"]
```

---

## 📊 Test Execution Plan

### Phase 1: Smoke Tests (30 minutes)

1. **Basic Connectivity** (5 min)
   - Health check endpoints
   - Metrics endpoint
   - Agent endpoint availability

2. **Single Agent Tests** (25 min)
   - Execute each agent once
   - Verify response structure
   - Check confidence scores

### Phase 2: Integration Tests (2 hours)

1. **Cross-Agent Workflows** (1 hour)
   - Test 1.1: Complete Company Analysis
   - Test 1.2: Market Research Workflow
   - Test 1.3: Competitor Analysis Chain

2. **LLM Integration** (1 hour)
   - Test 3.1: LLM Service Availability
   - Test 3.2: LLM Quality Variations
   - Test 3.3: LLM Error Handling

### Phase 3: Performance Tests (3 hours)

1. **Load Tests** (2 hours)
   - Test 2.1: Concurrent Users (50 users)
   - Test 2.2: Sustained Load (10 min)
   - Test 2.3: Spike Test

2. **Monitoring Validation** (1 hour)
   - Test 4.1: Prometheus Metrics
   - Test 4.2: Health Checks

### Phase 4: Resilience Tests (1 hour)

1. **Error Recovery** (1 hour)
   - Test 5.1: Database Failures
   - Test 5.2: Network Timeouts

### Total Estimated Time: 6.5 hours

---

## 📋 Test Environment Requirements

### Infrastructure

```yaml
staging_environment:
  backend:
    instances: 2
    cpu: 2 cores
    memory: 4GB

  database:
    type: PostgreSQL 15
    size: 20GB
    connections: 50

  cache:
    type: Redis 7
    memory: 2GB

  monitoring:
    prometheus: enabled
    grafana: enabled

  load_balancer:
    type: Nginx
    rate_limit: 1000 req/min
```

### Test Data

- 100 test companies (varying quality)
- 20 test queries (market search)
- 50 financial statements (different periods)
- 30 websites (for digital presence)
- 10 competitor sets

### External Dependencies

- ClaudeService (or mock)
- KRS/GUS APIs (or mock)
- External website access (or cached responses)

---

## ✅ Success Metrics

### Performance Targets

| Metric | Target | Critical |
|--------|--------|----------|
| Error Rate | <1% | <5% |
| p50 Response Time | <3s | <5s |
| p95 Response Time | <5s | <10s |
| p99 Response Time | <10s | <30s |
| Throughput | >10 req/s | >5 req/s |
| Availability | >99% | >95% |

### Quality Targets

| Metric | Target |
|--------|--------|
| Confidence Score (avg) | ≥85% |
| LLM Enhancement Rate | ≥95% |
| Data Consistency | 100% |
| Cache Hit Rate | ≥30% |

---

**Document Version**: 1.0
**Last Updated**: 2026-02-01
**Status**: Ready for Execution
**Owner**: MI-Navigator DevOps Team
