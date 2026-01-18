#!/usr/bin/env python3
"""Unlock test2fa user account"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from app.models.user import User

DATABASE_URL = "sqlite:///./backend/mi_navigator.db"

def unlock_user():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Reset failed login attempts and unlock
        result = session.execute(
            update(User)
            .where(User.email == "test2fa@example.com")
            .values(failed_login_attempts=0, account_locked_until=None)
        )
        session.commit()

        print(f"✓ Unlocked test2fa@example.com (rows affected: {result.rowcount})")

    except Exception as e:
        print(f"✗ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    unlock_user()
