#!/usr/bin/env python3
"""Create test user for Feature #211 - Version 2"""

import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.services.auth import AuthService
import uuid

db = SessionLocal()

email = "feature211_v2@example.com"
password = "test123"

# Check if user already exists
existing = db.query(User).filter(User.email == email).first()
if existing:
    print(f"{existing.id}")
    db.close()
    sys.exit(0)

# Create new user
user = User(
    id=uuid.uuid4(),
    email=email,
    password_hash=AuthService.hash_password(password),
    name="Feature 211 V2",
    role=UserRole.USER,
    is_active=True,
    email_verified=True,
    onboarding_completed=True
)

db.add(user)
db.commit()
db.refresh(user)

print(f"{user.id}")
db.close()
