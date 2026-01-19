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
    results = db.execute(text("SELECT id, email, role FROM users ORDER BY id DESC LIMIT 5")).fetchall()
    print("Last 5 users in database:")
    for row in results:
        print(f"  ID: {row[0]}, Email: {row[1]}, Role: {row[2]}")
finally:
    db.close()
