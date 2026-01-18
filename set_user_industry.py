#!/usr/bin/env python3
"""
Set user industry to plastics_processing for Feature #79 testing
"""
import sqlite3

# Connect to database
conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Check current user industry
cursor.execute("SELECT email, industry, industry_segment FROM users WHERE email='test2fa@test.com'")
user = cursor.fetchone()
print(f"Current user: {user}")

# Update user industry
cursor.execute("""
    UPDATE users
    SET industry = 'manufacturing',
        industry_segment = 'plastics_processing'
    WHERE email = 'test2fa@test.com'
""")

conn.commit()

# Verify update
cursor.execute("SELECT email, industry, industry_segment FROM users WHERE email='test2fa@test.com'")
user = cursor.fetchone()
print(f"Updated user: {user}")

conn.close()
print("\n✅ User industry updated to 'manufacturing' / 'plastics_processing'")
