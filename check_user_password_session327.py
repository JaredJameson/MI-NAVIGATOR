#!/usr/bin/env python3
import sqlite3

db_path = '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get user details
cursor.execute("SELECT id, email, password, role FROM users WHERE email = 'user@example.com'")
user = cursor.fetchone()

if user:
    print(f"User ID: {user[0]}")
    print(f"Email: {user[1]}")
    print(f"Password hash: {user[2][:50]}...")
    print(f"Role: {user[3]}")
else:
    print("User not found!")
    print("\nAll users:")
    cursor.execute("SELECT id, email, role FROM users LIMIT 5")
    for u in cursor.fetchall():
        print(f"  - {u[1]} ({u[2]})")

conn.close()
