#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')
os.chdir('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

from app.db.database import get_db
from app.models.user import User
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

db = next(get_db())

# Check if test user exists
test_user = db.query(User).filter(User.email == "test@regression.com").first()

if test_user:
    print(f"✅ Test user exists: {test_user.email}")
    print(f"   ID: {test_user.id}")
    print(f"   Name: {test_user.name}")
else:
    # Create test user
    test_user = User(
        id=str(uuid.uuid4()),
        email="test@regression.com",
        password_hash=pwd_context.hash("Test123!"),
        name="Test Regression User",
        role="user",
        onboarding_completed=True,
        is_active=True
    )
    db.add(test_user)
    db.commit()
    print(f"✅ Created test user: {test_user.email}")
    print(f"   Password: Test123!")
    print(f"   ID: {test_user.id}")

db.close()
