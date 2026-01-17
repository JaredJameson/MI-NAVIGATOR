"""
MI-Navigator - Main FastAPI Application
Market Intelligence Platform
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime
from pathlib import Path

from app.core.config import settings
from app.core.rate_limit import RateLimitMiddleware
from app.core.csrf import CSRFMiddleware
from app.core.maintenance import MaintenanceMiddleware
from app.api.v1.router import api_router

async def run_scheduler():
    """Background task to check and run scheduled data updates"""
    from app.api.v1.endpoints.companies import (
        COMPANY_UPDATE_SCHEDULES,
        COMPANY_LAST_UPDATED,
        MOCK_COMPANIES,
        SCHEDULE_NOTIFICATIONS,
        calculate_next_run
    )

    while True:
        await asyncio.sleep(10)  # Check every 10 seconds (for fast testing)

        now = datetime.now()
        print(f"[Scheduler] Checking schedules... ({len(COMPANY_UPDATE_SCHEDULES)} configured)")
        for company_id, schedule in list(COMPANY_UPDATE_SCHEDULES.items()):
            if not schedule.enabled:
                continue

            if not schedule.next_run:
                continue

            next_run_dt = datetime.fromisoformat(schedule.next_run)

            # Check if it's time to run (within 15 seconds window for testing)
            if now >= next_run_dt:
                print(f"[Scheduler] Running scheduled update for company {company_id}")

                # Update last_run timestamp
                schedule.last_run = now.isoformat()

                # Simulate data refresh
                COMPANY_LAST_UPDATED[company_id] = now.isoformat()

                # Calculate next run
                schedule.next_run = calculate_next_run(schedule.frequency, schedule.time)

                # Find company name
                company = next((c for c in MOCK_COMPANIES if c["id"] == company_id), None)
                company_name = company["name"] if company else company_id

                # Create notification
                notification = {
                    "id": f"sched_{company_id}_{now.timestamp()}",
                    "type": "scheduled_update",
                    "company_id": company_id,
                    "company_name": company_name,
                    "message": f"Automatyczna aktualizacja danych dla {company_name} została zakończona",
                    "timestamp": now.isoformat(),
                    "read": False
                }
                SCHEDULE_NOTIFICATIONS.append(notification)

                print(f"[Scheduler] Update completed for {company_name}. Next run: {schedule.next_run}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    print(f"Starting {settings.APP_NAME}...")

    # Start background scheduler
    scheduler_task = asyncio.create_task(run_scheduler())
    print("[Scheduler] Background scheduler started")

    yield

    # Shutdown
    print(f"Shutting down {settings.APP_NAME}...")
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        print("[Scheduler] Background scheduler stopped")

app = FastAPI(
    title=settings.APP_NAME,
    description="Market Intelligence Navigator - AI-powered business research platform",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
    # redirect_slashes defaults to True
)

# Maintenance mode middleware (check first, before other middleware)
app.add_middleware(MaintenanceMiddleware)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware, limit=10000, window_seconds=2592000)

# CSRF protection middleware
# Error logging endpoint is exempt to allow errors during login/before auth
app.add_middleware(
    CSRFMiddleware,
    exempt_paths=[
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
        "/api/v1/csrf-token",
        "/api/v1/errors/log",  # Allow error logging without CSRF token
        "/api/v1/reports",  # Allow report operations without CSRF token (auth handled at endpoint level)
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # Allow browser to access all response headers
    max_age=600  # Cache preflight requests for 10 minutes
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Mount static files directory
STATIC_DIR = Path(__file__).parent.parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "uploads").mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
