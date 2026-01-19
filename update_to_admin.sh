#!/bin/bash
# Update user role to admin for Feature #209 testing

cd /home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR

# Use Python to update the database
/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend/venv/bin/python3 << 'PYEOF'
import sys
import os
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:////home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()
try:
    # Update user role
    result = db.execute(
        text("UPDATE users SET role = 'admin' WHERE email = 'admin@test.com'")
    )
    db.commit()

    # Verify
    user = db.execute(
        text("SELECT id, email, name, role, is_active FROM users WHERE email = 'admin@test.com'")
    ).fetchone()

    if user:
        print(f"✅ User updated successfully:")
        print(f"   Email: {user[1]}")
        print(f"   Name: {user[2]}")
        print(f"   Role: {user[3]}")
        print(f"   Active: {user[4]}")
    else:
        print("❌ User not found")
finally:
    db.close()
PYEOF
