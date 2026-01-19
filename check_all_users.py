#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./backend/mi_navigator.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()
try:
    # Check for any admin or test210 users
    results = db.execute(text("SELECT id, email, role FROM users WHERE email LIKE '%210%' OR email LIKE '%admin%'")).fetchall()
    print(f"Found {len(results)} users matching '210' or 'admin':")
    for row in results:
        print(f"  ID: {row[0]}, Email: {row[1]}, Role: {row[2]}")
        
    # Also check total count
    count = db.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
    print(f"\nTotal users in database: {count}")
finally:
    db.close()
