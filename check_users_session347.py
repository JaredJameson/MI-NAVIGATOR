#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Use correct database path in backend directory
DATABASE_URL = "sqlite:///./backend/mi_navigator.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()
try:
    # Get all users
    results = db.execute(text("SELECT id, email, username FROM users LIMIT 20")).fetchall()
    print(f"Found {len(results)} users:")
    for row in results:
        print(f"  ID: {row[0]}, Email: {row[1]}, Username: {row[2]}")

    # Total count
    count = db.execute(text("SELECT COUNT(*) FROM users")).fetchone()[0]
    print(f"\nTotal users in database: {count}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
