#!/bin/bash
cd /home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend
./venv/bin/python << 'EOF'
import sys
import os
sys.path.insert(0, '.')

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.security import get_password_hash
import uuid

DATABASE_URL = "sqlite:///./mi_navigator.db"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Check if user exists
    existing = session.execute(
        select(User).where(User.email == "testuser@example.com")
    ).scalar_one_or_none()

    if existing:
        # Reset lockout
        existing.failed_login_attempts = 0
        existing.locked_until = None
        session.commit()
        print("✓ Unlocked existing user: testuser@example.com")
    else:
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email="testuser@example.com",
            password_hash=get_password_hash("Test123!"),
            name="Test User 2",
            role="USER",
            is_active=True,
            email_verified=True,
            onboarding_completed=True,
            preferred_language="pl",
            preferred_depth="standard",
            preferred_format="pdf",
            failed_login_attempts=0,
            locked_until=None
        )
        session.add(user)
        session.commit()
        print("✓ Created new user: testuser@example.com / Test123!")

except Exception as e:
    print(f"✗ Error: {e}")
    session.rollback()
finally:
    session.close()
EOF
