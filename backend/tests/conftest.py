"""
Pytest configuration and shared fixtures for MI-Navigator backend tests.
"""

import os
import sys
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from pathlib import Path
from httpx import AsyncClient, ASGITransport

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.config import settings
from app.db.session import get_db
from app.db.base import Base

# Import all models so they're registered with Base.metadata
# We need to import the actual model classes, not just the modules
from app.models import (
    User,
    Session,
    APIKey,
    CustomFieldDefinition,
    CustomFieldValue,
    FieldType,
    Workspace,
    WorkspaceMember,
    WorkspaceMemberRole,
    ReportTemplate,
    AuditLog,
    AnalyticsEvent,
    EventType,
    ErrorLog,
    UploadedFile,
    Webhook,
    WebhookEvent,
    WebhookStatus,
)
# Import PasswordResetToken which is in user.py but not exported in __init__.py
from app.models.user import PasswordResetToken


# ============================================================================
# TEST DATABASE FIXTURES
# ============================================================================

# Use PostgreSQL for tests (same as production, avoids SQLite compatibility issues)
TEST_DATABASE_URL = "postgresql+asyncpg://minavigator:minavigator@localhost:5439/minavigator_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    # Use NullPool for tests - connections are closed after each use
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=True,  # Enable SQL logging to see what's happening
    )

    # Debug: Check how many tables are registered
    print(f"\n[DEBUG] Number of tables in Base.metadata: {len(Base.metadata.tables)}")
    print(f"[DEBUG] Tables: {list(Base.metadata.tables.keys())}")

    # Create all tables - use a transaction and explicitly commit
    async with engine.begin() as conn:
        def create_tables(sync_conn):
            print(f"[DEBUG] Creating tables...")
            try:
                Base.metadata.create_all(sync_conn)
                print(f"[DEBUG] Tables created successfully")
            except Exception as e:
                print(f"[DEBUG] Error creating tables: {e}")
                raise

        await conn.run_sync(create_tables)
    # Transaction commits automatically when exiting the context manager
    print(f"[DEBUG] Transaction committed, checking if tables exist...")

    # Verify tables were created
    async with engine.connect() as conn:
        def check_tables(sync_conn):
            from sqlalchemy import text
            result = sync_conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            count = result.scalar()
            print(f"[DEBUG] Number of tables in public schema: {count}")

        await conn.run_sync(check_tables)

    yield engine

    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        # Clean up after each test
        await session.rollback()
        # Delete all test data from users table
        try:
            from app.models.user import User
            await session.execute(User.__table__.delete())
            await session.commit()
        except Exception:
            pass  # Table might not exist yet


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database dependency override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ============================================================================
# USER FIXTURES
# ============================================================================

@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user in the database."""
    import uuid
    from datetime import datetime
    from app.models.user import User, UserRole

    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash="$2b$12$TGPvezBHJCsLvN9sf1vS.O8WGNh8njCxq/VBS5KM7jPKqpmueEXSe",  # "password123" (valid bcrypt hash)
        name="Test User",
        role=UserRole.USER,
        preferred_language="pl",
        preferred_depth="standard",
        preferred_currency="PLN",
        timezone="Europe/Warsaw",
        onboarding_completed=True,
        is_active=True,
        email_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def test_admin(db_session: AsyncSession):
    """Create a test admin user in the database."""
    import uuid
    from datetime import datetime
    from app.models.user import User, UserRole

    admin = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        password_hash="$2b$12$nE5Lil1wEvGeGuq/iJ3wN..TwFkb1uv67HZ/pngXf6n.vGHmIwEkK",  # "admin123" (valid bcrypt hash)
        name="Admin User",
        role=UserRole.ADMIN,
        preferred_language="pl",
        preferred_depth="standard",
        preferred_currency="PLN",
        timezone="Europe/Warsaw",
        onboarding_completed=True,
        is_active=True,
        email_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    return admin


# Type aliases for fixtures
UserType = object  # Will be resolved at runtime
AdminType = object


@pytest.fixture
def test_password() -> str:
    """Test password (plaintext, matches the hash in test fixtures)."""
    return "password123"


@pytest.fixture
def admin_password() -> str:
    """Admin password (plaintext, matches the hash in test fixtures)."""
    return "admin123"


# ============================================================================
# AUTH TOKEN FIXTURES
# ============================================================================

@pytest.fixture
async def auth_headers(client: AsyncClient, test_user: "UserType", test_password: str) -> dict:
    """Get authentication headers for a test user (including CSRF token)."""
    # First get CSRF token
    csrf_response = await client.get("/api/v1/auth/csrf-token")
    assert csrf_response.status_code == 200
    csrf_data = csrf_response.json()
    csrf_token = csrf_data["csrf_token"]

    # Then login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": test_password
        },
        headers={"X-CSRF-Token": csrf_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

    return {
        "Authorization": f"Bearer {data['access_token']}",
        "Content-Type": "application/json",
        "X-CSRF-Token": csrf_token
    }


@pytest.fixture
async def auth_headers_no_csrf(client: AsyncClient, test_user: "UserType", test_password: str) -> dict:
    """Get authentication headers WITHOUT CSRF token (for exempt endpoints)."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": test_password
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

    return {
        "Authorization": f"Bearer {data['access_token']}",
        "Content-Type": "application/json"
    }


@pytest.fixture
async def admin_auth_headers(client: AsyncClient, test_admin: "AdminType", admin_password: str) -> dict:
    """Get authentication headers for an admin user (including CSRF token)."""
    # First get CSRF token
    csrf_response = await client.get("/api/v1/auth/csrf-token")
    assert csrf_response.status_code == 200
    csrf_data = csrf_response.json()
    csrf_token = csrf_data["csrf_token"]

    # Then login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_admin.email,
            "password": admin_password
        },
        headers={"X-CSRF-Token": csrf_token}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

    return {
        "Authorization": f"Bearer {data['access_token']}",
        "Content-Type": "application/json",
        "X-CSRF-Token": csrf_token
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def assert_valid_response(response, expected_status: int = 200):
    """Assert response is valid and has expected status."""
    assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}: {response.text}"


def assert_error_response(response, expected_status: int, expected_detail: str = None):
    """Assert response is an error with expected status and detail."""
    assert response.status_code == expected_status
    data = response.json()
    assert "detail" in data
    if expected_detail:
        assert expected_detail in data["detail"]


async def login_user(client: AsyncClient, email: str, password: str) -> dict:
    """Helper to login a user and return tokens."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password}
    )

    assert response.status_code == 200
    return response.json()


# ============================================================================
# CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "auth: mark test as authentication test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
