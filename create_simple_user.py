#!/usr/bin/env python3
"""Create simple test user without 2FA"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from passlib.context import CryptContext

DATABASE_URL = "sqlite:///./mi_navigator.db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if user exists
        existing = session.execute(
            select(User).where(User.email == "simple@test.com")
        ).scalar_one_or_none()

        if existing:
            print("✓ User already exists: simple@test.com")
            print(f"  Password: SimpleTest123!")
            print(f"  2FA: {existing.two_factor_enabled}")
            return

        # Create new user
        user = User(
            email="simple@test.com",
            hashed_password=pwd_context.hash("SimpleTest123!"),
            name="Simple User",
            role="user",
            two_factor_enabled=False,
            totp_secret=None
        )
        session.add(user)
        session.commit()

        print("✓ Created user: simple@test.com")
        print(f"  Password: SimpleTest123!")
        print(f"  2FA: Disabled")

    except Exception as e:
        print(f"✗ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_user()
