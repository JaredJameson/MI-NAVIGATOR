#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password

db = SessionLocal()

# Check user@example.com
user = db.query(User).filter(User.email == 'user@example.com').first()

if user:
    print(f"✅ User found: {user.email}")
    print(f"   ID: {user.id}")
    print(f"   Role: {user.role}")
    print(f"   Password hash exists: {bool(user.password_hash)}")
    print(f"   Hash starts with: {user.password_hash[:30]}..." if user.password_hash else "   Hash: NULL")

    # Test password verification
    test_passwords = ['Test123!', 'test123', 'Test1234!', 'password']
    print("\n🔐 Testing passwords:")
    for pwd in test_passwords:
        result = verify_password(pwd, user.password_hash)
        status = "✅ MATCH" if result else "❌ NO MATCH"
        print(f"   {pwd}: {status}")
else:
    print("❌ User not found: user@example.com")

db.close()
