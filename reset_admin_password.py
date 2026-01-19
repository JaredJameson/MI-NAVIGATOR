#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.security import get_password_hash

DATABASE_URL = "sqlite:///./backend/mi_navigator.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()
try:
    # Set new password
    new_password = "Admin123456"
    password_hash = get_password_hash(new_password)
    
    db.execute(text("UPDATE users SET password_hash = :hash WHERE email = 'test@example.com'"), {"hash": password_hash})
    db.commit()
    
    print(f"✅ Password updated for test@example.com")
    print(f"🔑 New credentials:")
    print(f"   Email: test@example.com")
    print(f"   Password: {new_password}")
finally:
    db.close()
