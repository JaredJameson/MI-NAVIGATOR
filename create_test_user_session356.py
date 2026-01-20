#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

from app.core.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = SessionLocal()
try:
    # Check if user exists
    email = "test_session356@example.com"
    existing = db.query(User).filter(User.email == email).first()

    if existing:
        print(f"User already exists: {existing.email}")
        print(f"ID: {existing.id}")
        print(f"Role: {existing.role}")
        print(f"Password: TestPass123!")
    else:
        # Create new test user
        hashed = pwd_context.hash("TestPass123!")
        user = User(
            email=email,
            name="Session 356 Test User",
            password_hash=hashed,
            role="user",
            industry="manufacturing",
            job_role="analyst",
            language="pl",
            onboarding_completed=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"Created user: {user.email}")
        print(f"ID: {user.id}")
        print(f"Password: TestPass123!")
finally:
    db.close()
