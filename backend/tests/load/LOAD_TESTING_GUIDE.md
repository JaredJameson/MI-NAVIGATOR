# MI-Navigator Load Testing Guide

**Version**: 1.0.0
**Framework**: Locust 2.0+
**Purpose**: Production readiness validation through comprehensive load testing

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Test Scenarios](#test-scenarios)
4. [Running Tests](#running-tests)
5. [Interpreting Results](#interpreting-results)
6. [Performance Targets](#performance-targets)
7. [Troubleshooting](#troubleshooting)

---

## 🔍 Overview

The MI-Navigator load testing suite uses Locust to simulate realistic user behavior and validate system performance under various load conditions.

### Test Coverage

- ✅ **Concurrent User Simulation**: 100, 500, 1000 users
- ✅ **API Endpoint Stress Testing**: All major endpoints
- ✅ **Agent Performance Testing**: All 6 agents
- ✅ **Cache Performance**: Cache hit rates and response times
- ✅ **Rate Limiting**: Validation of rate limit enforcement
- ✅ **Error Handling**: System behavior under stress

### User Classes

| Class | Purpose | Characteristics |
|-------|---------|-----------------|
| **AgentUser** | Test agent endpoints | Focused on 6 agent endpoints |
| **MixedWorkloadUser** | Realistic usage patterns | Mix of browsing, searching, analysis |
| **StressTestUser** | Aggressive stress testing | Minimal wait time, rapid requests |
| **CacheTestUser** | Cache performance | Repeated requests to same data |

---

## 📦 Installation

### 1. Install Locust

```bash
# Install Locust
pip install locust

# Or add to requirements.txt
echo "locust>=2.14.0" >> requirements.txt
pip install -r requirements.txt
```

### 2. Verify Installation

```bash
locust --version
# Expected: locust 2.14.0 (or higher)
```

---

## 🎯 Test Scenarios

### Scenario 1: Baseline Performance

**Purpose**: Establish baseline metrics under light load

**Configuration**:
```bash
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  -u 10 \
  -r 2 \
  --run-time 5m \
  --headless \
  --html reports/baseline_load.html
```

**Expected Results**:
- Mean response time: <200ms
- P95 response time: <400ms
- Error rate: 0%
- Throughput: >20 req/s

---

### Scenario 2: Moderate Load (Typical Usage)

**Purpose**: Simulate typical production workload

**Configuration**:
```bash
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  -u 100 \
  -r 10 \
  --run-time 10m \
  --headless \
  --html reports/moderate_load.html
```

**Expected Results**:
- Mean response time: <250ms
- P95 response time: <500ms
- Error rate: <1%
- Throughput: >40 req/s
- Cache hit rate: >80%

---

### Scenario 3: Heavy Load (Peak Hours)

**Purpose**: Validate performance during peak usage

**Configuration**:
```bash
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  -u 500 \
  -r 50 \
  --run-time 15m \
  --headless \
  --html reports/heavy_load.html
```

**Expected Results**:
- Mean response time: <500ms
- P95 response time: <1000ms
- Error rate: <5%
- Throughput: >30 req/s
- System remains stable

---

### Scenario 4: Stress Test (Breaking Point)

**Purpose**: Identify system breaking point and failure modes

**Configuration**:
```bash
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  -u 1000 \
  -r 100 \
  --run-time 20m \
  --headless \
  --html reports/stress_test.html
```

**Expected Behavior**:
- Rate limiting activates (429 errors)
- Response times increase but system remains responsive
- No crashes or data corruption
- Graceful degradation

---

### Scenario 5: Cache Performance Test

**Purpose**: Validate caching effectiveness

**Configuration**:
```bash
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  -u 50 \
  -r 10 \
  --run-time 5m \
  --headless \
  --html reports/cache_performance.html \
  --user-class CacheTestUser
```

**Expected Results**:
- Cached response time: <10ms
- Uncached response time: <250ms
- Cache hit rate: >90%
- Significant performance improvement with caching

---

### Scenario 6: Agent-Specific Load Test

**Purpose**: Test agent endpoint performance

**Configuration**:
```bash
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  -u 200 \
  -r 20 \
  --run-time 10m \
  --headless \
  --html reports/agent_load.html \
  --user-class AgentUser
```

**Expected Results**:
- Company Profile Agent: <200ms average
- Financial Analysis Agent: <250ms average
- Digital Presence Agent: <300ms average
- Competitor Mapping Agent: <280ms average
- Fact Checker Agent: <200ms average
- Insight Generator Agent: <240ms average

---

## 🚀 Running Tests

### Quick Start

```bash
# Change to project directory
cd /path/to/MI-NAVIGATOR/backend

# Run with Web UI (recommended for first run)
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Access Web UI at http://localhost:8089
```

### Headless Mode (Automated)

```bash
# Run complete test suite
bash tests/load/run_all_tests.sh

# Or run individual scenarios
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  -u 100 \
  -r 10 \
  --run-time 10m \
  --headless \
  --html reports/load_test_$(date +%Y%m%d_%H%M%S).html \
  --csv reports/load_test_$(date +%Y%m%d_%H%M%S)
```

### Parameters Explained

- `-f`: Locustfile path
- `--host`: Target server URL
- `-u`: Number of concurrent users to simulate
- `-r`: Spawn rate (users per second)
- `--run-time`: Test duration (e.g., 5m, 1h, 30s)
- `--headless`: Run without web UI
- `--html`: Generate HTML report
- `--csv`: Generate CSV reports (stats, failures, stats_history)
- `--user-class`: Specific user class to test

---

## 📊 Interpreting Results

### Web UI Metrics

When using the web UI (http://localhost:8089), monitor:

1. **Request Stats**:
   - Number of requests
   - Number of failures
   - Median response time
   - Average response time
   - Min/Max response time
   - Requests per second

2. **Failures**:
   - Error types and frequencies
   - Failed endpoints
   - Error messages

3. **Charts**:
   - Response time percentiles
   - Requests per second
   - Number of users

### HTML Report

Generated HTML reports include:

- **Request Statistics**: Comprehensive stats for each endpoint
- **Response Time Distribution**: Percentiles (50th, 66th, 75th, 80th, 90th, 95th, 98th, 99th, 100th)
- **Failures**: Detailed failure information
- **Exceptions**: Any exceptions encountered
- **Charts**: Visual representation of performance over time

### CSV Reports

Three CSV files are generated:

1. **`*_stats.csv`**: Request statistics
   - Type, Name, Request Count, Failure Count
   - Median, Average, Min, Max response times
   - Requests per second

2. **`*_failures.csv`**: Failure details
   - Endpoint, Error message, Occurrences

3. **`*_stats_history.csv`**: Time-series data
   - Timestamp, User count, Request stats over time

---

## 🎯 Performance Targets

### Response Times

| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| Mean (uncached) | <250ms | <500ms | >1000ms |
| Mean (cached) | <10ms | <50ms | >100ms |
| P95 (uncached) | <500ms | <1000ms | >2000ms |
| P95 (cached) | <20ms | <100ms | >200ms |
| P99 (uncached) | <1000ms | <2000ms | >5000ms |
| P99 (cached) | <50ms | <200ms | >500ms |

### Throughput

| Load Level | Target | Acceptable | Critical |
|------------|--------|------------|----------|
| Light (10 users) | >20 req/s | >10 req/s | <5 req/s |
| Moderate (100 users) | >40 req/s | >20 req/s | <10 req/s |
| Heavy (500 users) | >30 req/s | >15 req/s | <5 req/s |

### Error Rates

| Load Level | Target | Acceptable | Critical |
|------------|--------|------------|----------|
| Light | 0% | <0.5% | >1% |
| Moderate | <0.5% | <2% | >5% |
| Heavy | <2% | <5% | >10% |
| Stress | <10% | <20% | >50% |

### Cache Performance

| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| Cache Hit Rate | >90% | >80% | <70% |
| Cache Response Time | <10ms | <50ms | >100ms |
| Uncached Response Time | <250ms | <500ms | >1000ms |

---

## 🔧 Troubleshooting

### High Error Rates

**Symptoms**: >5% error rate under moderate load

**Possible Causes**:
- Rate limiting triggered
- Database connection pool exhausted
- Redis connection issues
- External API failures

**Solutions**:
```bash
# Check rate limiting configuration
grep RATE_LIMIT backend/.env

# Monitor database connections
docker-compose exec postgres psql -U postgres -c \
  "SELECT count(*) FROM pg_stat_activity;"

# Check Redis connectivity
docker-compose exec redis redis-cli ping

# Review application logs
docker-compose logs -f backend | grep ERROR
```

---

### Slow Response Times

**Symptoms**: Mean response time >1s

**Possible Causes**:
- Cache misses
- Database slow queries
- CPU/memory constraints
- Network latency

**Solutions**:
```bash
# Check cache hit rates
docker-compose exec redis redis-cli INFO stats

# Identify slow queries
docker-compose exec postgres psql -U postgres -d mi_navigator -c \
  "SELECT query, calls, total_time, mean_time
   FROM pg_stat_statements
   ORDER BY mean_time DESC
   LIMIT 10;"

# Monitor resource usage
docker stats

# Check network latency
ping -c 10 localhost
```

---

### Memory Leaks

**Symptoms**: Gradual performance degradation over time

**Possible Causes**:
- Unclosed database connections
- Cache overflow
- Memory leaks in application code

**Solutions**:
```bash
# Monitor memory usage over time
watch -n 5 'docker stats --no-stream backend'

# Check for connection leaks
docker-compose exec postgres psql -U postgres -c \
  "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"

# Review Redis memory
docker-compose exec redis redis-cli INFO memory

# Restart services if needed
docker-compose restart backend
```

---

### Rate Limiting Issues

**Symptoms**: Many 429 (Too Many Requests) errors

**Expected Behavior**: Rate limiting is working correctly

**Verify Configuration**:
```bash
# Check rate limit settings
grep RATE_LIMIT backend/.env

# Expected: 10 requests per minute per IP
```

**Note**: Rate limiting errors during stress tests are expected and indicate proper protection against abuse.

---

## 📝 Best Practices

1. **Baseline First**: Always establish baseline performance before load testing
2. **Gradual Ramp-up**: Use appropriate spawn rates to avoid overwhelming the system
3. **Monitor Resources**: Watch CPU, memory, and network during tests
4. **Realistic Data**: Use realistic test data and scenarios
5. **Multiple Runs**: Run tests multiple times for consistency
6. **Documentation**: Document test results and any issues encountered
7. **Production-like Environment**: Test in environment similar to production
8. **Regular Testing**: Schedule regular load tests (weekly/monthly)

---

## 🗓️ Test Schedule (Recommended)

- **Daily**: Smoke tests (10 users, 2 minutes)
- **Weekly**: Moderate load tests (100 users, 10 minutes)
- **Monthly**: Heavy load tests (500 users, 15 minutes)
- **Quarterly**: Stress tests (1000 users, 20 minutes)
- **Before Release**: Complete test suite with all scenarios

---

## 📈 Sample Test Run

```bash
# Complete load test suite
cd /path/to/MI-NAVIGATOR/backend

# 1. Baseline
echo "Running baseline test..."
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
  -u 10 -r 2 --run-time 5m --headless \
  --html reports/baseline_$(date +%Y%m%d_%H%M%S).html

# 2. Moderate load
echo "Running moderate load test..."
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
  -u 100 -r 10 --run-time 10m --headless \
  --html reports/moderate_$(date +%Y%m%d_%H%M%S).html

# 3. Heavy load
echo "Running heavy load test..."
locust -f tests/load/locustfile.py --host=http://localhost:8000 \
  -u 500 -r 50 --run-time 15m --headless \
  --html reports/heavy_$(date +%Y%m%d_%H%M%S).html

echo "Load tests complete! Check reports/ directory for results."
```

---

**Last Updated**: 2026-01-26
**Version**: 1.0.0
**Status**: Production Ready ✅
