# MI-Navigator Deployment Guide

**Version**: 1.0.0
**Last Updated**: 2026-01-26
**Status**: Production Ready

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Docker Deployment](#docker-deployment)
4. [Database Setup](#database-setup)
5. [Redis Configuration](#redis-configuration)
6. [Security Hardening](#security-hardening)
7. [Monitoring & Logging](#monitoring--logging)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Health Checks](#health-checks)
10. [Backup & Recovery](#backup--recovery)
11. [Scaling Strategy](#scaling-strategy)
12. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 4GB
- Storage: 20GB SSD
- OS: Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)

**Recommended (Production)**:
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 50GB+ SSD
- OS: Ubuntu 22.04 LTS

### Software Requirements

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.11+ (if running without Docker)
- **PostgreSQL**: 14+ (managed service recommended)
- **Redis**: 7.0+ (managed service recommended)
- **Nginx**: 1.20+ (reverse proxy)

### Required Services

- PostgreSQL database
- Redis cache
- SMTP server (for email notifications)
- SSL certificate (Let's Encrypt recommended)

---

## 🔐 Environment Configuration

### 1. Create Environment File

Create `.env` in the backend directory:

```bash
cd backend
cp .env.example .env
```

### 2. Configure Environment Variables

**Required Variables**:

```env
# Application
APP_NAME="MI-Navigator"
ENVIRONMENT="production"  # development | staging | production
DEBUG=false
LOG_LEVEL="INFO"  # DEBUG | INFO | WARNING | ERROR | CRITICAL

# Server
HOST="0.0.0.0"
PORT=8000
WORKERS=4  # Number of uvicorn workers (2 * CPU cores + 1)

# Database
DATABASE_URL="postgresql://user:password@postgres:5432/mi_navigator"
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis
REDIS_URL="redis://redis:6379/0"
REDIS_MAX_CONNECTIONS=50
CACHE_TTL=3600  # seconds

# Security
SECRET_KEY="your-super-secret-key-change-this-in-production"  # Generate with: openssl rand -hex 32
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"

# External APIs (Optional but recommended)
KRS_API_KEY=""  # If using external KRS API
CEIDG_API_KEY=""  # If using external CEIDG API
GUS_API_KEY=""  # If using external GUS API
CLAUDE_API_KEY=""  # Required for AI-powered insights

# Email (SMTP)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-app-specific-password"
SMTP_FROM="noreply@yourdomain.com"

# Monitoring
SENTRY_DSN=""  # Optional: Sentry error tracking
```

**Optional Variables**:

```env
# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=60  # seconds

# File Uploads
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
UPLOAD_DIR="/app/static/uploads"

# Logging
LOG_FILE="/var/log/mi-navigator/app.log"
LOG_ROTATION="1 day"
LOG_RETENTION=30  # days
```

### 3. Generate Secret Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate CSRF secret
openssl rand -hex 32
```

### 4. Environment-Specific Configurations

**Development**:
```env
ENVIRONMENT="development"
DEBUG=true
LOG_LEVEL="DEBUG"
WORKERS=1
```

**Staging**:
```env
ENVIRONMENT="staging"
DEBUG=false
LOG_LEVEL="INFO"
WORKERS=2
```

**Production**:
```env
ENVIRONMENT="production"
DEBUG=false
LOG_LEVEL="WARNING"
WORKERS=4
```

---

## 🐳 Docker Deployment

### 1. Review Docker Configuration

**docker-compose.yml** (Production):

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: production
    container_name: mi-navigator-backend
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/mi_navigator
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend/static:/app/static
      - ./backend/logs:/var/log/mi-navigator
    networks:
      - mi-navigator-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:14-alpine
    container_name: mi-navigator-postgres
    restart: always
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=mi_navigator
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/migrations:/docker-entrypoint-initdb.d
    networks:
      - mi-navigator-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: mi-navigator-redis
    restart: always
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - mi-navigator-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    container_name: mi-navigator-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend/build:/usr/share/nginx/html:ro
    depends_on:
      - backend
    networks:
      - mi-navigator-network

volumes:
  postgres_data:
  redis_data:

networks:
  mi-navigator-network:
    driver: bridge
```

### 2. Optimize Dockerfile

**Backend Dockerfile** (Multi-stage):

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/static/uploads /var/log/mi-navigator

# Add non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /var/log/mi-navigator

USER appuser

# Make PATH include user packages
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 3. Build and Deploy

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Verify health
curl http://localhost:8000/health
```

---

## 💾 Database Setup

### 1. Initialize Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d mi_navigator

# Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  # For full-text search

# Verify
\dx
```

### 2. Run Migrations

```bash
# Apply migrations
docker-compose exec backend alembic upgrade head

# Verify
docker-compose exec backend alembic current
```

### 3. Create Admin User

```bash
# Create admin user via Python script
docker-compose exec backend python scripts/create_admin.py \
  --email admin@yourdomain.com \
  --password SecureAdminPassword123!
```

### 4. Database Backup Script

Create `scripts/backup_database.sh`:

```bash
#!/bin/bash
set -e

BACKUP_DIR="/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="mi_navigator_${TIMESTAMP}.sql"

mkdir -p $BACKUP_DIR

docker-compose exec -T postgres pg_dump -U postgres mi_navigator > "$BACKUP_DIR/$BACKUP_FILE"

# Compress
gzip "$BACKUP_DIR/$BACKUP_FILE"

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

---

## 🔴 Redis Configuration

### 1. Redis Optimization

**redis.conf** (custom configuration):

```conf
# Memory
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence
appendonly yes
appendfsync everysec

# Performance
tcp-backlog 511
timeout 300
tcp-keepalive 300

# Logging
loglevel notice
logfile "/var/log/redis/redis.log"
```

### 2. Redis Monitoring

```bash
# Check Redis stats
docker-compose exec redis redis-cli INFO stats

# Monitor commands
docker-compose exec redis redis-cli MONITOR

# Check memory usage
docker-compose exec redis redis-cli INFO memory
```

---

## 🔒 Security Hardening

### 1. Security Checklist

- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Configure firewall (UFW/iptables)
- [ ] Enable CSRF protection
- [ ] Configure rate limiting
- [ ] Set up fail2ban
- [ ] Regular security updates
- [ ] Enable audit logging
- [ ] Restrict database access
- [ ] Use environment variables (never commit secrets)

### 2. SSL/TLS Configuration

**Nginx SSL Configuration**:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 3. Firewall Configuration

```bash
# UFW setup
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

---

## 📊 Monitoring & Logging

### 1. Application Logging

**Configure structured logging**:

```python
# app/core/logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)
```

### 2. Health Check Monitoring

**scripts/health_monitor.sh**:

```bash
#!/bin/bash

HEALTH_URL="http://localhost:8000/health"
ALERT_EMAIL="admin@yourdomain.com"

response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $response -ne 200 ]; then
    echo "Health check failed with status $response" | \
        mail -s "MI-Navigator Health Check Alert" $ALERT_EMAIL
    exit 1
fi

echo "Health check passed"
exit 0
```

### 3. Metrics Collection

Recommended tools:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Sentry**: Error tracking
- **ELK Stack**: Log aggregation

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

**.github/workflows/deploy.yml**:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to production
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
          SERVER_HOST: ${{ secrets.SERVER_HOST }}
        run: |
          echo "$SSH_PRIVATE_KEY" > key.pem
          chmod 600 key.pem
          ssh -i key.pem user@$SERVER_HOST '
            cd /opt/mi-navigator &&
            git pull origin main &&
            docker-compose build &&
            docker-compose up -d &&
            docker-compose exec backend alembic upgrade head
          '
```

---

## ✅ Health Checks

### 1. Application Health

```http
GET /health
```

**Expected Response (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-26T10:00:00Z",
  "version": "1.0.0",
  "services": {
    "api": "operational",
    "cache": "operational",
    "database": "operational"
  },
  "agents": {
    "status": "all_operational",
    "count": 6
  }
}
```

### 2. Readiness Probe

Kubernetes readiness probe configuration:

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 5
  successThreshold: 1
  failureThreshold: 3
```

### 3. Liveness Probe

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 30
  timeoutSeconds: 10
  failureThreshold: 3
```

---

## 💾 Backup & Recovery

### 1. Automated Backup Schedule

**cron job** (`crontab -e`):

```cron
# Daily database backup at 2 AM
0 2 * * * /opt/mi-navigator/scripts/backup_database.sh

# Weekly Redis backup at 3 AM Sunday
0 3 * * 0 /opt/mi-navigator/scripts/backup_redis.sh
```

### 2. Recovery Procedure

```bash
# Stop application
docker-compose down

# Restore database
gunzip -c /backups/postgres/mi_navigator_20260126_020000.sql.gz | \
  docker-compose exec -T postgres psql -U postgres -d mi_navigator

# Restore Redis (if applicable)
docker-compose exec redis redis-cli --rdb /data/dump.rdb

# Start application
docker-compose up -d

# Verify
curl http://localhost:8000/health
```

---

## 📈 Scaling Strategy

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  nginx:
    # Load balancer configuration
    volumes:
      - ./nginx/load-balancer.conf:/etc/nginx/nginx.conf:ro
```

### Load Balancer Configuration

```nginx
upstream backend_servers {
    least_conn;
    server backend1:8000 max_fails=3 fail_timeout=30s;
    server backend2:8000 max_fails=3 fail_timeout=30s;
    server backend3:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;

    location / {
        proxy_pass http://backend_servers;
        proxy_next_upstream error timeout http_502 http_503 http_504;
    }
}
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Database Connection Failed**
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready -U postgres

# Verify connection string
docker-compose exec backend printenv DATABASE_URL

# Check network
docker network inspect mi-navigator-network
```

**2. Redis Connection Failed**
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Verify connectivity
docker-compose exec backend python -c "import redis; r=redis.from_url('redis://redis:6379/0'); print(r.ping())"
```

**3. Agent Failures**
```bash
# Check agent logs
docker-compose logs -f backend | grep "agent"

# Test specific agent
curl -X POST http://localhost:8000/api/v1/agents/company-profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nip": "1234567890"}'
```

**4. Performance Issues**
```bash
# Check resource usage
docker stats

# Check slow queries (PostgreSQL)
docker-compose exec postgres psql -U postgres -d mi_navigator -c \
  "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Check Redis memory
docker-compose exec redis redis-cli INFO memory
```

---

## 📝 Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Backup scripts tested
- [ ] Health checks operational
- [ ] Monitoring configured
- [ ] All 236 tests passing
- [ ] Performance benchmarks met
- [ ] Security audit completed
- [ ] Documentation updated
- [ ] Team trained on deployment procedure

---

**Deployment Status**: Ready for Production ✅
**Last Verified**: 2026-01-26
**Next Review**: 2026-02-26
