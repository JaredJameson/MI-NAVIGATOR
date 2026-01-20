#!/usr/bin/env python3
import sqlite3
import bcrypt

# Create regression test user for session 307
conn = sqlite3.connect('backend/mi_navigator.db')
cursor = conn.cursor()

email = 'regression307@test.com'
password = 'Test123456'
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Delete user if exists
cursor.execute('DELETE FROM users WHERE email = ?', (email,))

# Insert new user
cursor.execute('''
    INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified)
    VALUES (?, ?, ?, ?, ?, ?)
''', (email, hashed, 'Regression Test User 307', 'user', 1, 1))

conn.commit()
user_id = cursor.lastrowid
print(f"Created user: {email} with ID: {user_id}")
conn.close()
