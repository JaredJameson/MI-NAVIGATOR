#!/usr/bin/env python3
"""
Create test user for Feature #211 - Usage limit enforcement testing
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.db.session import async_session
from app.models.user import User, UserRole
from sqlalchemy import select
import uuid


async def create_test_user():
    """Create a test user for Feature #211"""
    async with async_session() as db:
        # Create unique test user
        user_id = str(uuid.uuid4())
        test_email = f"test211_session341_{user_id[:8]}@example.com"

        user = User(
            id=user_id,
            email=test_email,
            name="Test User Feature 211",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIxNzM6faW",  # password: "test123"
            role=UserRole.USER,  # NON-ADMIN = limit of 2
            is_active=True,
            email_verified=True,
            two_factor_enabled=False
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        print(f"✅ Test user created successfully!")
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Password: test123")
        print(f"Usage Limit: 2 (non-admin)")
        print(f"\n🔑 Login credentials:")
        print(f"   Email: {user.email}")
        print(f"   Password: test123")

        return user


if __name__ == "__main__":
    asyncio.run(create_test_user())
