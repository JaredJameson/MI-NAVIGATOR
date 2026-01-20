import sqlite3
import uuid
from datetime import datetime
import hashlib

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Utwórz użytkownika
user_id = str(uuid.uuid4())
email = 'session329@test.com'
name = 'Session 329 Test'
# Hash hasła: testpass123
password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYk3H.S9Fqm'

cursor.execute('''
    INSERT INTO users (id, email, name, password_hash, role, is_active, email_verified, created_at, updated_at)
    VALUES (?, ?, ?, ?, 'USER', 1, 1, ?, ?)
''', (user_id, email, name, password_hash, datetime.now().isoformat(), datetime.now().isoformat()))

conn.commit()
print(f'User created: {user_id}, {email}')
conn.close()
