#!/usr/bin/env python3
"""
Create an admin user for testing Feature #209 (Role-based menu visibility)
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserRole
from app.core.security import get_password_hash
import uuid

# Database URL
DATABASE_URL = "sqlite:///./mi_navigator.db"

# Create engine and session
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def create_admin_user():
    """Create admin user for testing"""
    db = SessionLocal()

    try:
        # Check if admin user already exists
        admin_email = "admin@test.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()

        if existing_admin:
            print(f"✅ Admin user already exists: {admin_email}")
            print(f"   ID: {existing_admin.id}")
            print(f"   Role: {existing_admin.role}")
            return existing_admin.id, admin_email

        # Create new admin user
        admin_user = User(
            id=uuid.uuid4(),
            email=admin_email,
            password_hash=get_password_hash("admin123"),
            name="Admin Test User",
            role=UserRole.ADMIN,
            is_active=True,
            email_verified=True,
            onboarding_completed=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print(f"✅ Created admin user:")
        print(f"   Email: {admin_email}")
        print(f"   Password: admin123")
        print(f"   ID: {admin_user.id}")
        print(f"   Role: {admin_user.role}")

        return admin_user.id, admin_email

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    admin_id, admin_email = create_admin_user()
    print(f"\n🔐 Login credentials:")
    print(f"   Email: {admin_email}")
    print(f"   Password: admin123")
