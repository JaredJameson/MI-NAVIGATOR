#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from app.db.session import SessionLocal
from app.models.user import User

db = SessionLocal()
try:
    user = db.query(User).filter(User.email == 'regression_test_335@example.com').first()
    if user:
        print(f'Email: {user.email}')
        print(f'Password Hash: {user.hashed_password}')
        print(f'Hash Length: {len(user.hashed_password)}')
        print(f'Is Plaintext: {user.hashed_password == "TestPass123!"}')
        print(f'Starts with bcrypt: {user.hashed_password.startswith("$2b$")}')
    else:
        print('User not found')
finally:
    db.close()
