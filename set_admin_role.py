#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend/mi_navigator.db')
cursor = conn.cursor()

# Update user to admin
cursor.execute("UPDATE users SET role = 'admin' WHERE email = 'testregression@example.com'")
conn.commit()

# Verify
cursor.execute("SELECT email, role FROM users WHERE email = 'testregression@example.com'")
user = cursor.fetchone()

if user:
    print(f"✓ Updated {user[0]} to role: {user[1]}")
else:
    print("✗ User not found")

conn.close()
