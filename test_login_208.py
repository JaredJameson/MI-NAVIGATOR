#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Find a user to test with
cursor.execute("""
    SELECT id, email, preferred_depth, two_factor_enabled
    FROM users
    WHERE email LIKE '%regression%' OR email LIKE '%test%'
    LIMIT 5
""")

users = cursor.fetchall()
if users:
    print("Found test users:")
    for user in users:
        print(f"  ID: {user[0]}")
        print(f"  Email: {user[1]}")
        print(f"  Preferred Depth: {user[2]}")
        print(f"  2FA: {user[3]}")
        print()
else:
    print("No test users found")

conn.close()
