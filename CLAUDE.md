# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MI-Navigator is an AI-powered Market Intelligence platform that automates business research using a hierarchical agent system. The platform aggregates data from Polish business registries (KRS, GUS, REGON), performs financial analysis, competitive intelligence, and generates comprehensive market research reports.

**Tech Stack:**
- Backend: FastAPI (Python 3.11+), PostgreSQL 15, Redis 7
- Frontend: Next.js 14 (App Router), React 18, TailwindCSS, shadcn/ui
- AI: Claude API (Anthropic)
- Real-time: WebSocket, Socket.io
- Monitoring: Prometheus, structlog
- Load Testing: Locust 2.14.0+

## Development Commands

### Backend (FastAPI)

```bash
# Setup and activate virtual environment
cd backend
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database migrations
alembic upgrade head                    # Apply all migrations
alembic revision --autogenerate -m "description"  # Create new migration
alembic downgrade -1                    # Rollback one migration

# Run tests
pytest                                  # Run all tests
pytest tests/unit                       # Unit tests only
pytest tests/integration                # Integration tests only
pytest -v --cov=app --cov-report=html   # With coverage report
pytest -m unit                          # Run by marker
pytest -m "not slow"                    # Exclude slow tests
pytest tests/unit/test_specific.py::test_function  # Single test

# Code quality
black app tests                         # Format code
isort app tests                         # Sort imports
flake8 app                             # Lint
mypy app                               # Type check
```

### Frontend (Next.js)

```bash
# Setup
cd frontend
npm install

# Development
npm run dev                             # Start dev server (http://localhost:3000)
npm run build                           # Production build
npm run start                           # Start production server
npm run lint                            # ESLint

# Testing
npm test                                # Run tests
npm run test:watch                      # Watch mode
```

### Docker Services

```bash
# Start all services (PostgreSQL, Redis, Qdrant)
docker-compose up -d

# Start specific services
docker-compose up -d postgres redis

# Stop services
docker-compose down

# View logs
docker-compose logs -f postgres
docker-compose logs -f redis

# Connect to PostgreSQL
docker exec -it mi-navigator-postgres psql -U minavigator -d minavigator

# Connect to Redis
docker exec -it mi-navigator-redis redis-cli
```

### Environment-Specific Deployment

**Staging Environment:**
```bash
# Backend
cd backend
docker-compose -f ../docker-compose.staging.yml up -d
# Use backend/.env.staging.template as reference

# Frontend
cd frontend
# Use frontend/.env.staging as reference
```

**Production Environment:**
```bash
docker-compose -f docker-compose.production.yml up -d
# Use backend/.env.production.template as reference
```

**Environment Files:**
- `backend/.env.staging.template` - Staging configuration template
- `backend/.env.production.template` - Production configuration template
- `frontend/.env.staging` - Frontend staging configuration

### Load Testing

**Framework:** Locust 2.14.0+ (implemented in Week 21)

```bash
# Run load tests
cd backend
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

Access Locust UI at http://localhost:8089

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check database connection
docker exec -it mi-navigator-postgres pg_isready -U minavigator

# Check Redis connection
docker exec -it mi-navigator-redis redis-cli ping

# Verify all Docker services are running
docker-compose ps
```

## Architecture

### AI Agent System (Hierarchical)

The platform uses a 4-layer agent hierarchy orchestrated by `app/services/orchestrator.py`:

**L1 - Core Orchestration:**
- `orchestrator.py` - Main coordinator, parallel/sequential execution, progress tracking
- `intent_parser.py` - Parse user queries and detect intent
- `query_router.py` - Route queries to appropriate agents
- `conversation_agent.py` - User interaction and query handling (20KB)

**L2 - Data Acquisition Agents:**
- `company_profile_agent.py` - KRS/GUS/REGON data aggregation (46KB)
- `market_search_agent.py` - Market research and data gathering (53KB)
- `digital_presence_agent.py` - Website crawling and online presence analysis (50KB)

**L3 - Analysis Agents:**
- `financial_analysis_agent.py` - Financial statement analysis, ratios, Z-score (81KB, most complex)
- `competitor_mapping_agent.py` - Competitive intelligence, Porter's Five Forces, SWOT (60KB)

**L4 - Synthesis Agents:**
- `fact_checker_agent.py` - Verify data accuracy and sources (35KB)
- `insight_generator_agent.py` - Generate insights and recommendations (65KB)
- `report_generator.py` - Compose final reports

**Key Service Integration:**
- `claude_service.py` - Claude API integration with streaming support
- `websocket_manager.py` - Real-time progress updates to frontend
- `report_composer.py` - Report assembly and formatting

### Data Source Integrations (`app/integrations/`)

- `krs_client.py` - Polish National Court Register (29KB, comprehensive)
- `gus_client.py` - Central Statistical Office integration (13KB)
- `regon_client.py` - REGON business registry (13KB)
- `website_crawler.py` - Playwright-based web scraping (40KB)

### Backend Structure

```
backend/app/
├── agents/           # AI agents (8 specialized agents)
├── api/v1/
│   ├── endpoints/    # 25+ REST endpoints (auth, reports, chat, analytics, etc.)
│   └── router.py     # API aggregation
├── core/
│   ├── config.py     # Settings and environment
│   ├── csrf.py       # CSRF protection
│   ├── rate_limit.py # Rate limiting middleware
│   ├── cache.py      # Redis caching
│   └── maintenance.py # Maintenance mode
├── db/
│   ├── base.py       # SQLAlchemy base with naming conventions
│   └── session.py    # Database session management
├── integrations/     # External data sources
├── models/           # SQLAlchemy ORM models (15+ models)
│   ├── user.py       # User with 2FA, account lockout
│   ├── alert.py      # Monitoring alerts
│   ├── audit_log.py  # Audit trail
│   ├── webhook.py    # Webhook integrations
│   └── workspace.py  # Multi-tenant workspaces
├── services/         # Business logic layer
│   ├── orchestrator.py      # Agent orchestration
│   ├── claude_service.py    # Claude API integration
│   ├── websocket_manager.py # Real-time updates
│   ├── auth.py              # Authentication/JWT
│   ├── two_factor.py        # 2FA with TOTP
│   └── audit_service.py     # Audit logging
├── schemas/          # Pydantic models for validation
└── utils/            # Helper utilities
```

### Frontend Structure

```
frontend/src/
├── app/              # Next.js 14 App Router (42 routes)
│   ├── auth/         # Login, register, 2FA, password reset
│   ├── dashboard/    # Main dashboard
│   ├── chat/         # AI chat interface
│   ├── reports/      # Report management and templates
│   ├── companies/    # Company profiles and schedules
│   ├── analysis/     # Analysis tools (SWOT, Porter, PESTLE)
│   ├── alerts/       # Monitoring alerts CRUD
│   ├── admin/        # Admin panel
│   ├── settings/     # User/workspace settings, billing, webhooks
│   └── api/          # API route handlers
├── components/
│   ├── auth/         # AuthGuard, login forms
│   ├── chat/         # Chat UI, message components, specialized displays
│   │                 # (CompanyCard, FinancialStatements, SwotAnalysis, etc.)
│   ├── ui/           # shadcn/ui components (button, card, input, etc.)
│   └── charts/       # Recharts visualizations
├── hooks/            # Custom React hooks
│   └── useLocale.ts  # i18n support
├── services/
│   ├── api.ts        # Axios client with auth interceptors
│   ├── syncQueue.ts  # Offline sync
│   └── errorTracking.ts # Error monitoring
├── stores/           # Zustand state management (empty - using React Query)
└── lib/
    └── utils.ts      # Utility functions (cn, date formatting)
```

### Database Schema

All models inherit from SQLAlchemy `Base` with naming conventions for constraints.

**Core Tables:**
- `users` - Authentication, 2FA, timezone, preferences, usage limits
- `sessions` - JWT session management
- `workspaces` - Multi-tenant support
- `audit_logs` - Complete audit trail with IP tracking
- `analytics_events` - User analytics and feature usage

**Business Tables:**
- `alerts` - Monitoring alerts with schedules
- `report_templates` - Customizable report templates
- `webhooks` - External integrations
- `api_keys` - API key management
- `feature_flags` - Feature toggles
- `custom_fields` - Dynamic field definitions
- `uploaded_files` - File management with virus scanning
- `error_logs` - Application error tracking

**Migrations:** Alembic in `backend/alembic/versions/`

### API Endpoints (25+ endpoints in `app/api/v1/endpoints/`)

- **Authentication:** Login, register, 2FA, password reset, refresh tokens
- **Users:** Profile, preferences, timezone, usage limits
- **Chat:** WebSocket streaming, conversation history
- **Reports:** CRUD, templates, export (PDF/DOCX/XLSX/PPTX)
- **Research:** Trigger analysis, progress tracking
- **Companies:** Profile data, schedules, KRS/REGON integration
- **Analysis:** SWOT, Porter, PESTLE, market sizing
- **Alerts:** CRUD, scheduling, notifications
- **Search:** Semantic search, filters
- **Workspaces:** Multi-tenant management
- **Analytics:** Usage metrics, events tracking
- **Webhooks:** CRUD, secret management, payload delivery
- **Admin:** User management, system monitoring, feature flags

### Authentication & Security

**Stack:**
- JWT tokens (access + refresh)
- 2FA with TOTP (QR code generation)
- Account lockout after failed attempts
- CSRF protection middleware
- Rate limiting per endpoint
- Audit logging for all actions
- Password hashing with bcrypt

**Implementation:**
- `app/services/auth.py` - JWT handling
- `app/services/two_factor.py` - TOTP implementation
- `app/core/csrf.py` - CSRF middleware
- `app/core/rate_limit.py` - Rate limiting
- `frontend/src/components/auth/AuthGuard.tsx` - Route protection

### Real-time Features

**WebSocket Architecture:**
- Backend: `app/services/websocket_manager.py` - Connection management, progress updates
- Frontend: Socket.io client for streaming responses
- Use cases: Chat streaming, agent progress, report generation status

**Progress Tracking:**
```python
# Backend broadcasts progress
await progress_manager.update_progress(task_id, {
    "agent": "company_profile",
    "status": "in_progress",
    "progress": 0.5
})

# Frontend receives via WebSocket
socket.on('progress_update', (data) => {...})
```

### Monitoring & Observability

**Stack (Phase 3 - Week 31):**
- Prometheus for metrics collection (`prometheus-client==0.19.0`)
- Monitoring configuration in `backend/monitoring/`
- Nginx configuration in `backend/nginx/`
- Application logging via structlog

**Metrics Endpoints:**
- Backend metrics: `/metrics` (Prometheus format)
- Structured logging with request tracing

### Configuration

**Backend Environment (backend/.env):**
```
ANTHROPIC_API_KEY=         # Claude API key (required)
DATABASE_URL=              # PostgreSQL connection
REDIS_URL=                 # Redis connection
SECRET_KEY=                # JWT signing key
JWT_SECRET_KEY=            # Alternative JWT key
CORS_ORIGINS=              # Allowed origins (JSON array)
```

**Frontend Environment (frontend/.env.local):**
```
NEXT_PUBLIC_API_URL=       # Backend API URL
NEXT_PUBLIC_WS_URL=        # WebSocket URL
```

**Docker Ports:**
- PostgreSQL: 5439 (external) → 5432 (internal)
- Redis: 6385 (external) → 6379 (internal)
- Qdrant: 6333, 6334

## Testing Strategy

**Backend Testing Structure:**
```
backend/tests/
├── conftest.py           # Pytest fixtures, test database setup
├── unit/                 # Fast, isolated tests
│   ├── test_users_endpoints.py
│   └── test_financial_analysis_agent.py
├── integration/          # Tests with external resources
├── agents/               # Agent-specific tests
├── services/             # Service layer tests
├── performance/          # Performance benchmarks
│   └── test_benchmarks.py
└── load/                 # Load testing with Locust
```

**Test Markers:**
- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.regression` - Regression tests

**Coverage:** Configured for 80%+ coverage target with HTML and XML reports.

## Key Patterns

### Agent Execution Pattern

```python
# In orchestrator.py
results = await asyncio.gather(
    agent1.execute(query),
    agent2.execute(query),
    return_exceptions=True  # Graceful degradation
)
```

All agents follow:
1. Input validation
2. Data acquisition (parallel where possible)
3. Processing/analysis
4. Result formatting
5. Error handling with fallbacks

### API Response Pattern

```python
# Success
return {"status": "success", "data": {...}}

# Error
return {"status": "error", "message": "...", "code": "ERROR_CODE"}
```

### Frontend Data Fetching

Uses React Query (`@tanstack/react-query`) for server state:
- Automatic caching and refetching
- Optimistic updates
- Error and loading states
- No Zustand stores currently used (React Query sufficient)

### Internationalization

**Implementation:**
- Next-intl for i18n support
- Messages in `frontend/messages/` (multiple locales)
- `useLocale` hook for language detection
- `middleware.ts` for locale routing
- User timezone and language preferences stored in database
- Polish (pl_PL) is the primary locale for user-facing content

**Supported Languages:**
- Polish (pl_PL) - Primary
- English (en) - Secondary

## Common Development Tasks

### Adding a New API Endpoint

1. Create endpoint in `backend/app/api/v1/endpoints/new_feature.py`
2. Add router to `backend/app/api/v1/router.py`
3. Create/update Pydantic schemas in `backend/app/schemas/`
4. Add business logic to `backend/app/services/`
5. Update frontend API client in `frontend/src/services/api.ts`
6. Add tests in `backend/tests/`

### Adding a New AI Agent

1. Create agent in `backend/app/agents/new_agent.py`
2. Implement `execute()` method with error handling
3. Register in `orchestrator.py` imports
4. Add to intent parser patterns in `intent_parser.py`
5. Update query router in `query_router.py`
6. Add specialized UI components in `frontend/src/components/chat/`

### Database Schema Changes

```bash
# 1. Modify models in backend/app/models/
# 2. Generate migration
cd backend
alembic revision --autogenerate -m "Add new_field to users"
# 3. Review and edit migration in alembic/versions/
# 4. Apply migration
alembic upgrade head
# 5. Update Pydantic schemas if needed
```

### Adding Frontend Route

1. Create page in `frontend/src/app/new-route/page.tsx`
2. Add to sidebar navigation in `frontend/src/components/Sidebar.tsx`
3. Protect with AuthGuard if needed
4. Add i18n messages if using translations

## Development Notes

- **Agent System:** All agents are real implementations (not mocks). The system uses actual KRS/REGON API integrations.
- **Scheduler:** Background scheduler exists but is disabled (see `main.py:25-41`). Scheduled updates should use Celery or similar with database persistence.
- **Testing:** Project has 380+ regression test reports documenting feature implementations and bug fixes.
- **Progress:** Week 31 completed - Production deployment infrastructure with monitoring (Phase 3)
- **Polish Language:** Many user-facing strings and documentation are in Polish (pl_PL locale).
- **PWA Support:** Service worker implementation in `frontend/public/sw.js`
- **Documentation:** Extensive session summaries and weekly implementation reports in root directory
- **Load Testing:** Locust framework integrated for performance testing (Week 21)

## Important Architecture Decisions

1. **Async-First:** FastAPI with asyncio throughout for concurrent agent execution
2. **Streaming:** Claude API responses streamed via WebSocket for better UX
3. **Graceful Degradation:** Agent failures don't cascade - partial results returned
4. **Audit Everything:** All user actions logged to audit_logs table
5. **Multi-tenant Ready:** Workspace model supports multiple organizations
6. **Type Safety:** Pydantic for backend validation, TypeScript for frontend
7. **Security Focused:** 2FA, rate limiting, CSRF, account lockout all implemented
8. **Real-time Updates:** WebSocket progress tracking during long-running operations

## Access Points

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs (Swagger)
- **Alternative Docs:** http://localhost:8000/redoc
- **PostgreSQL:** localhost:5439 (user: minavigator, db: minavigator)
- **Redis:** localhost:6385
- **Locust UI:** http://localhost:8089 (when running load tests)

## Troubleshooting

**Backend won't start:**
- Check `ANTHROPIC_API_KEY` in `.env`
- Verify PostgreSQL is running: `docker-compose ps`
- Check logs: `docker-compose logs postgres`
- Run migrations: `alembic upgrade head`

**Frontend build fails:**
- Clear `.next` folder: `rm -rf frontend/.next`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npm run lint`

**Database connection errors:**
- Verify docker ports: PostgreSQL on 5439, not 5432
- Check DATABASE_URL matches docker-compose configuration
- Ensure postgres container is healthy: `docker-compose ps`

**Tests failing:**
- Run single test for debugging: `pytest path/to/test.py::test_name -v`
- Check test database is clean: Drop and recreate test DB
- Review conftest.py for fixture setup
