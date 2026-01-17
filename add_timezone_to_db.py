#!/usr/bin/env python3
"""Add timezone column to users table"""
import sqlite3
import sys

DB_PATH = "backend/mi_navigator.db"

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'timezone' in columns:
        print("✓ Timezone column already exists")
    else:
        # Add timezone column
        cursor.execute("ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'Europe/Warsaw'")
        conn.commit()
        print("✓ Timezone column added successfully")

    # Verify
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'timezone' in columns:
        print("✓ Verified: timezone column exists")
    else:
        print("✗ Error: timezone column not found after adding")
        sys.exit(1)

    conn.close()
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
