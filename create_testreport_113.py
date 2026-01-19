import sqlite3
import uuid
from datetime import datetime

# Connect to database
conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Get user ID (first user)
cursor.execute("SELECT id FROM users LIMIT 1")
user_id = cursor.fetchone()[0]
print(f"User ID: {user_id}")

# Create report with exact name "TestReport" for case-insensitive search test
report_id = f"report_test113_{uuid.uuid4().hex[:8]}"
title = "TestReport"
now = datetime.now().isoformat()

cursor.execute("""
    INSERT INTO reports (id, user_id, title, type, status, created_at, updated_at, content)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (report_id, user_id, title, 'market_analysis', 'completed', now, now, '{"summary": "Test for case-insensitive search - Feature 113"}'))

conn.commit()
print(f"\nCreated report: {report_id}")
print(f"Title: {title}")

# Verify
cursor.execute("SELECT id, title FROM reports WHERE id = ?", (report_id,))
result = cursor.fetchone()
print(f"Verified: {result}")

conn.close()
