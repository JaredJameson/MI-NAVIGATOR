#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./mi_navigator.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()
try:
    # Update role to admin
    db.execute(text("UPDATE users SET role = 'admin' WHERE email = 'admin210@test.com'"))
    db.commit()
    
    # Verify
    result = db.execute(text("SELECT id, email, role, name FROM users WHERE email = 'admin210@test.com'")).fetchone()
    if result:
        print(f"✅ User updated successfully:")
        print(f"   ID: {result[0]}")
        print(f"   Email: {result[1]}")
        print(f"   Role: {result[2]}")
        print(f"   Name: {result[3]}")
    else:
        print("❌ User not found")
finally:
    db.close()
