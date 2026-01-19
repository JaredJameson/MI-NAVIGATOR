#!/usr/bin/env python3
import sys
import os

# Check both databases
databases = [
    ("./mi_navigator.db", "Root DB"),
    ("./backend/mi_navigator.db", "Backend DB")
]

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

for db_path, db_name in databases:
    try:
        DATABASE_URL = f"sqlite:///{db_path}"
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        result = db.execute(text("SELECT id, email, role FROM users WHERE email = 'test210@test.com'")).fetchone()
        if result:
            print(f"✅ Found in {db_name}:")
            print(f"   Path: {db_path}")
            print(f"   ID: {result[0]}")
            print(f"   Email: {result[1]}")
            print(f"   Role: {result[2]}")
        else:
            print(f"❌ Not found in {db_name}")
        
        db.close()
    except Exception as e:
        print(f"❌ Error checking {db_name}: {e}")
