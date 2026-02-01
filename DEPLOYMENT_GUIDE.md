# MI-Navigator Deployment Guide

**Phase 3 Week 31** - Production Deployment Documentation

---

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Staging Deployment](#staging-deployment)
- [Production Deployment](#production-deployment)
- [Database Migrations](#database-migrations)
- [Monitoring & Logging](#monitoring--logging)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Backup & Recovery](#backup--recovery)
- [Troubleshooting](#troubleshooting)
- [Rollback Procedures](#rollback-procedures)

---

## Overview

MI-Navigator deployment uses Docker containers orchestrated by Docker Compose (or Kubernetes for large-scale deployments). The platform consists of:

- **Backend API** (FastAPI + Python 3.11)
- **Frontend** (Next.js + React)
- **PostgreSQL Database** (managed service recommended)
- **Redis Cache** (managed service recommended)
- **Nginx Reverse Proxy** (SSL termination + load balancing)
- **Monitoring Stack** (Prometheus + Grafana)

**Deployment Environments**:
1. **Development** - Local development (existing)
2. **Staging** - Pre-production testing
3. **Production** - Live environment

---

## Prerequisites

### Required Software
- Docker Engine 24.0+ with Docker Compose v2
- Git 2.30+
- OpenSSL (for SSL certificate generation)
- AWS CLI / Azure CLI / GCloud SDK (if using cloud providers)

### Required Accounts & Services
- Domain name (e.g., `mi-navigator.com`)
- SSL certificate (Let's Encrypt or commercial)
- Email service (SendGrid, AWS SES, Mailgun)
- LLM API keys (OpenAI, Anthropic, Gemini)
- Sentry account (error tracking)
- Cloud provider account (AWS/Azure/GCP)

### Recommended Managed Services
**Production**:
- **Database**: AWS RDS PostgreSQL, Azure Database, Google Cloud SQL
- **Cache**: AWS ElastiCache, Azure Cache for Redis, Google Memorystore
- **File Storage**: AWS S3, Azure Blob Storage, Google Cloud Storage
- **Monitoring**: Sentry, Datadog, New Relic

---

## Environment Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/MI-NAVIGATOR.git
cd MI-NAVIGATOR
```

### Step 2: Environment Configuration

#### Production Environment Variables
```bash
# Copy template
cp backend/.env.production.template backend/.env.production

# Generate secure secrets
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"

# Edit .env.production with your values
nano backend/.env.production
```

**Critical Variables to Configure**:
- `SECRET_KEY` - Application secret (64 characters)
- `JWT_SECRET_KEY` - JWT signing secret (64 characters)
- `DATABASE_URL` - Managed PostgreSQL connection string
- `REDIS_URL` - Managed Redis connection string
- `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` - LLM provider keys
- `SENTRY_DSN` - Error tracking DSN
- `SMTP_*` - Email service credentials
- `CORS_ORIGINS` - Production domain URLs

#### Staging Environment Variables
```bash
cp backend/.env.staging.template backend/.env.staging
# Configure with staging-specific values
nano backend/.env.staging
```

### Step 3: SSL Certificate Setup

#### Option A: Let's Encrypt (Recommended for Production)
```bash
# Install Certbot
sudo apt-get install certbot

# Obtain certificate
sudo certbot certonly --standalone -d app.mi-navigator.com -d www.mi-navigator.com

# Copy certificates
sudo cp /etc/letsencrypt/live/app.mi-navigator.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/app.mi-navigator.com/privkey.pem nginx/ssl/
```

#### Option B: Self-Signed Certificate (Staging Only)
```bash
# Generate self-signed certificate (staging)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/staging/staging.key \
  -out nginx/ssl/staging/staging.crt \
  -subj "/C=PL/ST=Mazowieckie/L=Warsaw/O=MI-Navigator/CN=staging.mi-navigator.com"
```

---

## Staging Deployment

Staging environment for testing before production release.

### Step 1: Build Images
```bash
# Build staging images
docker-compose -f docker-compose.staging.yml build
```

### Step 2: Database Initialization
```bash
# Start database and Redis only
docker-compose -f docker-compose.staging.yml up -d postgres redis

# Wait for database to be ready
docker-compose -f docker-compose.staging.yml exec postgres pg_isready -U minavigator_staging

# Run migrations
docker-compose -f docker-compose.staging.yml run --rm backend alembic upgrade head
```

### Step 3: Start All Services
```bash
# Start all staging services
docker-compose -f docker-compose.staging.yml up -d

# Check service health
docker-compose -f docker-compose.staging.yml ps

# View logs
docker-compose -f docker-compose.staging.yml logs -f backend
```

### Step 4: Verify Deployment
```bash
# Check backend health
curl http://localhost:8080/health

# Check frontend
curl http://localhost:8080/

# Check API
curl http://localhost:8080/api/v1/health
```

**Staging Access**:
- Frontend: `http://staging.mi-navigator.com:8080`
- API: `http://staging.mi-navigator.com:8080/api/v1`
- Grafana: `http://staging.mi-navigator.com:3100`

---

## Production Deployment

### Step 1: Pre-Deployment Checklist
- [ ] All tests passing (194+ unit tests, integration tests)
- [ ] Environment variables configured and verified
- [ ] SSL certificates installed and valid
- [ ] Managed database configured (AWS RDS, Azure Database, etc.)
- [ ] Managed Redis configured (ElastiCache, Azure Cache, etc.)
- [ ] DNS records configured (A/CNAME records)
- [ ] Email service configured and tested
- [ ] Backup strategy implemented
- [ ] Monitoring dashboards configured
- [ ] Runbook and rollback procedures documented

### Step 2: Database Setup (Managed Service)
```bash
# Example: AWS RDS PostgreSQL
# 1. Create RDS instance via AWS Console/CLI
# 2. Configure security groups (allow backend IP/VPC)
# 3. Update DATABASE_URL in .env.production

# Run migrations against production database
export DATABASE_URL="postgresql://username:password@your-rds-endpoint:5432/minavigator"
alembic upgrade head
```

### Step 3: Build Production Images
```bash
# Build production images
docker-compose -f docker-compose.production.yml build

# Tag images for registry (optional)
docker tag mi-navigator-backend:production your-registry/mi-navigator-backend:v1.0.0
docker tag mi-navigator-frontend:production your-registry/mi-navigator-frontend:v1.0.0

# Push to registry
docker push your-registry/mi-navigator-backend:v1.0.0
docker push your-registry/mi-navigator-frontend:v1.0.0
```

### Step 4: Deploy to Production
```bash
# Deploy all services
docker-compose -f docker-compose.production.yml up -d

# Check service status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### Step 5: Post-Deployment Verification
```bash
# Health checks
curl https://app.mi-navigator.com/health
curl https://app.mi-navigator.com/api/v1/health

# Test critical endpoints
curl -X POST https://app.mi-navigator.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword"}'

# Monitor logs for errors
docker-compose -f docker-compose.production.yml logs backend --tail=100 -f
```

**Production Access**:
- Frontend: `https://app.mi-navigator.com`
- API: `https://app.mi-navigator.com/api/v1`
- Grafana: Internal only (via VPN/bastion)
- Prometheus: Internal only

---

## Database Migrations

MI-Navigator uses Alembic for database schema management.

### Creating New Migrations
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new table or column"

# Review generated migration file
cat alembic/versions/<revision>_add_new_table.py

# Apply migration
alembic upgrade head
```

### Migration Best Practices
- Always review auto-generated migrations before applying
- Test migrations on staging before production
- Backup database before running migrations
- Use transaction wrapping for data migrations
- Document breaking changes in migration message

### Rollback Migration
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# View migration history
alembic history
```

---

## Monitoring & Logging

### Prometheus Setup
Prometheus collects metrics from:
- Backend API (`/metrics` endpoint)
- PostgreSQL (postgres-exporter)
- Redis (redis-exporter)
- Nginx (nginx-exporter)
- System metrics (node-exporter)

**Access**: `http://internal-prometheus:9090`

### Grafana Dashboards
Pre-configured dashboards:
- **MI-Navigator Overview** - Request rate, response time, error rate
- **Database Performance** - Connections, query performance, cache hit rate
- **Infrastructure** - CPU, memory, disk, network

**Access**: `http://internal-grafana:3100`
**Default Credentials**: `admin` / `CHANGE_ME_SECURE_PASSWORD` (configure in `.env.production`)

### Sentry Error Tracking
Configure Sentry DSN in `.env.production`:
```bash
SENTRY_DSN=https://your_sentry_dsn@sentry.io/project_id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

**Features**:
- Real-time error alerts
- Stack traces with source code
- Performance monitoring
- User feedback integration

### Application Logs
```bash
# View backend logs
docker-compose -f docker-compose.production.yml logs backend -f

# View frontend logs
docker-compose -f docker-compose.production.yml logs frontend -f

# View nginx logs
docker-compose -f docker-compose.production.yml logs nginx -f

# Search logs for errors
docker-compose -f docker-compose.production.yml logs backend | grep ERROR

# Export logs to file
docker-compose -f docker-compose.production.yml logs --no-color > deployment-$(date +%Y%m%d).log
```

---

## SSL/TLS Configuration

### Let's Encrypt Auto-Renewal
```bash
# Setup auto-renewal cron job
sudo crontab -e

# Add line (runs daily at 2 AM):
0 2 * * * certbot renew --post-hook "docker-compose -f /path/to/docker-compose.production.yml restart nginx"
```

### SSL Best Practices
- Use TLS 1.2 and TLS 1.3 only (disable TLS 1.0/1.1)
- Implement HSTS header with preload
- Use strong cipher suites (configured in nginx.production.conf)
- Monitor certificate expiration (set alerts for 30 days before expiry)
- Test SSL configuration: https://www.ssllabs.com/ssltest/

---

## Backup & Recovery

### Database Backup (Automated)
```bash
# Automated backup script (run via cron)
#!/bin/bash
BACKUP_DIR=/backups/postgres
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/minavigator_$TIMESTAMP.sql.gz"

# Backup database
pg_dump -h $DB_HOST -U $DB_USER -d minavigator | gzip > $BACKUP_FILE

# Upload to S3
aws s3 cp $BACKUP_FILE s3://mi-navigator-backups-production/

# Delete local backup after upload
rm $BACKUP_FILE

# Retain backups for 30 days
aws s3 ls s3://mi-navigator-backups-production/ | \
  while read -r line; do
    createDate=$(echo $line | awk '{print $1" "$2}')
    createDate=$(date -d"$createDate" +%s)
    olderThan=$(date -d"30 days ago" +%s)
    if [[ $createDate -lt $olderThan ]]; then
      fileName=$(echo $line | awk '{print $4}')
      aws s3 rm s3://mi-navigator-backups-production/$fileName
    fi
  done
```

### Manual Backup
```bash
# Backup database
docker-compose -f docker-compose.production.yml exec postgres \
  pg_dump -U minavigator minavigator | gzip > backup-$(date +%Y%m%d).sql.gz

# Backup uploaded files
tar -czf uploads-$(date +%Y%m%d).tar.gz backend/uploads/
```

### Restore from Backup
```bash
# Restore database
gunzip < backup-20260131.sql.gz | \
  docker-compose -f docker-compose.production.yml exec -T postgres \
  psql -U minavigator -d minavigator

# Verify restore
docker-compose -f docker-compose.production.yml exec postgres \
  psql -U minavigator -d minavigator -c "SELECT COUNT(*) FROM users;"
```

---

## Troubleshooting

### Common Issues

#### Issue: Backend container fails to start
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs backend

# Common causes:
# 1. Database connection failed
# 2. Missing environment variables
# 3. Secret key validation failed
# 4. Migration failed

# Verify environment variables
docker-compose -f docker-compose.production.yml exec backend env | grep DATABASE_URL

# Test database connection
docker-compose -f docker-compose.production.yml exec backend \
  python -c "from app.db.session import engine; engine.connect()"
```

#### Issue: High memory usage
```bash
# Check resource usage
docker stats

# Adjust resource limits in docker-compose.production.yml
# deploy:
#   resources:
#     limits:
#       memory: 4G

# Restart services with new limits
docker-compose -f docker-compose.production.yml up -d --force-recreate
```

#### Issue: Slow API responses
```bash
# Check database query performance
docker-compose -f docker-compose.production.yml exec postgres \
  psql -U minavigator -d minavigator -c "
    SELECT query, mean_exec_time, calls
    FROM pg_stat_statements
    ORDER BY mean_exec_time DESC
    LIMIT 10;"

# Check Redis cache hit rate
docker-compose -f docker-compose.production.yml exec redis redis-cli INFO stats | grep keyspace

# Enable query logging temporarily
# In .env.production: LOG_LEVEL=DEBUG
```

#### Issue: SSL certificate expired
```bash
# Check certificate expiration
openssl x509 -in nginx/ssl/fullchain.pem -noout -dates

# Renew Let's Encrypt certificate
sudo certbot renew

# Reload nginx
docker-compose -f docker-compose.production.yml restart nginx
```

---

## Rollback Procedures

### Rollback Application Code
```bash
# Stop current deployment
docker-compose -f docker-compose.production.yml down

# Checkout previous version
git checkout <previous-version-tag>

# Rebuild and deploy
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

### Rollback Database Migration
```bash
# Check current migration
alembic current

# View migration history
alembic history

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Verify rollback
alembic current
```

### Emergency Maintenance Mode
```bash
# Enable maintenance mode
docker-compose -f docker-compose.production.yml exec backend \
  python -c "
from app.core.config import settings
settings.MAINTENANCE_MODE = True
"

# Or update .env.production
# MAINTENANCE_MODE=true

# Restart backend
docker-compose -f docker-compose.production.yml restart backend
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Code reviewed and approved
- [ ] All tests passing (unit, integration, E2E)
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Database migration tested on staging
- [ ] Environment variables verified
- [ ] SSL certificates valid
- [ ] Backup completed

### Deployment
- [ ] Deploy to staging first
- [ ] Smoke tests passed on staging
- [ ] Deploy to production
- [ ] Run database migrations
- [ ] Verify health checks
- [ ] Monitor error rates
- [ ] Test critical user flows

### Post-Deployment
- [ ] Monitor logs for errors (30 minutes)
- [ ] Check Sentry for exceptions
- [ ] Verify Grafana metrics
- [ ] Test API endpoints
- [ ] Notify team of successful deployment
- [ ] Update deployment log
- [ ] Tag release in Git

---

## Support & Resources

**Documentation**:
- [Master Roadmap](/MASTER_ROADMAP.md)
- [Phase 2 Completion Report](/backend/PHASE_2_COMPLETION_REPORT.md)
- [API Documentation](/docs/api/)

**Monitoring**:
- Sentry: https://sentry.io/your-project
- Grafana: Internal access only
- AWS CloudWatch: https://console.aws.amazon.com/cloudwatch

**Emergency Contacts**:
- DevOps Team: devops@mi-navigator.com
- On-Call Engineer: +48 XXX XXX XXX

---

**Document Version**: 1.0
**Last Updated**: 2026-02-01
**Phase**: Phase 3 Week 31 Day 1
**Status**: Production Ready ✅
