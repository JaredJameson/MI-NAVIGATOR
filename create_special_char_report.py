import sqlite3
import uuid
from datetime import datetime

# Connect to database
conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Check current reports
cursor.execute("SELECT id, title FROM reports LIMIT 5")
print("Existing reports:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Get user ID (first user)
cursor.execute("SELECT id FROM users LIMIT 1")
user_id = cursor.fetchone()[0]
print(f"\nUser ID: {user_id}")

# Create report with special characters
report_id = f"report_{uuid.uuid4().hex[:8]}"
special_title = "Test @#$%^&*()_+ Raport Żółć <>{}[]|"
now = datetime.now().isoformat()

cursor.execute("""
    INSERT INTO reports (id, user_id, title, type, status, created_at, updated_at, content)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (report_id, user_id, special_title, 'market_analysis', 'completed', now, now, '{"summary": "Test with special chars"}'))

conn.commit()
print(f"\nCreated report: {report_id}")
print(f"Title: {special_title}")

# Verify
cursor.execute("SELECT id, title FROM reports WHERE id = ?", (report_id,))
result = cursor.fetchone()
print(f"\nVerified: {result}")

conn.close()
