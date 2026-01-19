#!/usr/bin/env python3
"""Create test project and report for regression testing"""
import sqlite3
import uuid
from datetime import datetime

db_path = 'mi_navigator.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get user ID
cursor.execute("SELECT id FROM users WHERE email = 'user@example.com'")
user_result = cursor.fetchone()
if not user_result:
    print("ERROR: User not found")
    exit(1)

user_id = user_result[0]
print(f"User ID: {user_id}")

# Check if test project exists
cursor.execute("SELECT id FROM projects WHERE name = 'Regression Test Project'")
project_result = cursor.fetchone()

if project_result:
    project_id = project_result[0]
    print(f"Test project already exists: {project_id}")
else:
    # Create test project
    project_id = str(uuid.uuid4()).replace('-', '')
    cursor.execute("""
        INSERT INTO projects (id, name, type, description, user_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        project_id,
        'Regression Test Project',
        'due_diligence',
        'For regression testing features #49 and #242',
        user_id,
        datetime.utcnow().isoformat(),
        datetime.utcnow().isoformat()
    ))
    print(f"Created test project: {project_id}")

# Check if test report exists
cursor.execute("SELECT id FROM reports WHERE title = 'Regression Test Report'")
report_result = cursor.fetchone()

if report_result:
    report_id = report_result[0]
    print(f"Test report already exists: {report_id}")
else:
    # Create test report
    report_id = str(uuid.uuid4()).replace('-', '')
    report_content = {
        "summary": "This is a test report for regression testing",
        "sections": [
            {
                "title": "Overview",
                "content": "Test content for comment and embed features"
            }
        ]
    }

    cursor.execute("""
        INSERT INTO reports (id, title, type, status, content, project_id, user_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        report_id,
        'Regression Test Report',
        'due_diligence',
        'completed',
        str(report_content),
        project_id,
        user_id,
        datetime.utcnow().isoformat(),
        datetime.utcnow().isoformat()
    ))
    print(f"Created test report: {report_id}")

conn.commit()
conn.close()

print("\nTest data created successfully!")
print(f"Project ID: {project_id}")
print(f"Report ID: {report_id}")
print(f"You can now access the report at: http://localhost:3000/reports/{report_id}")
