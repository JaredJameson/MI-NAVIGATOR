#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Use correct database path
DATABASE_URL = "sqlite:///./mi_navigator.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()
try:
    # Get all users
    results = db.execute(text("SELECT id, email, role FROM users LIMIT 10")).fetchall()
    print(f"Found {len(results)} users:")
    for row in results:
        print(f"  Email: {row[1]}, Role: {row[2]}")

    # Total count
    count = db.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
    print(f"\nTotal users in database: {count}")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
