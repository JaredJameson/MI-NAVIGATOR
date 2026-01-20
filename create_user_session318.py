import sqlite3
import hashlib
import secrets
from datetime import datetime

# Connect to database
conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Generate test user
username = f"test_session318_{secrets.token_hex(4)}"
email = f"{username}@test.local"
password = "Test123!"
password_hash = hashlib.sha256(password.encode()).hexdigest()

# Insert user
cursor.execute("""
    INSERT INTO users (username, email, password_hash, role, created_at, email_verified)
    VALUES (?, ?, ?, 'user', ?, 1)
""", (username, email, password_hash, datetime.now().isoformat()))

user_id = cursor.lastrowid

conn.commit()
conn.close()

print(f"User created: {username}")
print(f"Email: {email}")
print(f"Password: {password}")
print(f"User ID: {user_id}")
