#!/usr/bin/env python3
"""Create test user for MI-Navigator"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.security import get_password_hash
import uuid

DATABASE_URL = "sqlite:///./backend/mi_navigator.db"

def create_test_user():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if user exists
        existing = session.execute(
            select(User).where(User.email == "test@example.com")
        ).scalar_one_or_none()

        if existing:
            print("✓ Test user already exists: test@example.com")
            return

        # Create test user
        user = User(
            id=str(uuid.uuid4()),
            email="test@example.com",
            password_hash=get_password_hash("Test123!"),
            name="Test User",
            role="USER",
            is_active=True,
            email_verified=True,
            onboarding_completed=True,
            preferred_language="pl",
            preferred_depth="standard",
            preferred_format="pdf"
        )

        session.add(user)
        session.commit()

        print("✓ Created test user:")
        print(f"  Email: test@example.com")
        print(f"  Password: Test123!")
        print(f"  Role: USER")

    except Exception as e:
        print(f"✗ Error creating user: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_test_user()
