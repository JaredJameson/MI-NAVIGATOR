#!/usr/bin/env python3
"""Enable 2FA for test2fa@example.com user"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from datetime import datetime

DATABASE_URL = "sqlite:///./backend/mi_navigator.db"

def enable_2fa():
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

        # Enable 2FA with TOTP secret
        user.two_factor_enabled = True
        user.totp_secret = 'RWLS2I4IEEDKXZ4T3HWZLZ5ZV5ALACK2'  # Test TOTP secret
        user.updated_at = datetime.utcnow()
        session.commit()

        print("✓ Successfully enabled 2FA for test2fa@example.com")
        print(f"  two_factor_enabled: {user.two_factor_enabled}")
        print(f"  totp_secret: {'SET' if user.totp_secret else 'NULL'}")
        print(f"\n  TOTP Secret: {user.totp_secret}")
        print(f"\n  Use this QR code URL in your authenticator app:")
        print(f"  otpauth://totp/MI-Navigator:test2fa@example.com?secret={user.totp_secret}&issuer=MI-Navigator")

    except Exception as e:
        print(f"✗ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    enable_2fa()
