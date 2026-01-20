import sqlite3
import hashlib
import uuid
from datetime import datetime

# Connect to database
conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db')
cursor = conn.cursor()

# Create test user
user_id = str(uuid.uuid4())
email = 'feature211test@example.com'
password = 'TestPass123!'
password_hash = hashlib.sha256(password.encode()).hexdigest()

cursor.execute('''
INSERT INTO users (id, email, password_hash, name, role, email_verified, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (user_id, email, password_hash, 'Feature 211 Test User', 'user', 1, datetime.utcnow(), datetime.utcnow()))

conn.commit()
conn.close()

print(f"Created user: {email}")
print(f"Password: {password}")
print(f"User ID: {user_id}")
