#!/usr/bin/env python3
"""Disable 2FA for test2fa user"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models.user import User

DATABASE_URL = "sqlite:///./backend/mi_navigator.db"

def disable_2fa():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Find user
        user = session.execute(
            select(User).where(User.email == "test2fa@example.com")
        ).scalar_one_or_none()

        if not user:
            print("✗ User test2fa@example.com not found")
            return

        # Disable 2FA
        user.two_factor_enabled = False
        user.totp_secret = None
        session.commit()

        print("✓ Successfully disabled 2FA for test2fa@example.com")
        print(f"  two_factor_enabled: {user.two_factor_enabled}")
        print(f"  totp_secret: {user.totp_secret}")

    except Exception as e:
        print(f"✗ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    disable_2fa()
