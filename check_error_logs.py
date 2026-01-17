#!/usr/bin/env python3
import sqlite3
import json

conn = sqlite3.connect('backend/mi_navigator.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, error_type, error_message,
           CASE WHEN stack_trace IS NOT NULL THEN 'YES' ELSE 'NO' END as has_stack,
           source, user_agent, error_metadata, occurred_at
    FROM error_logs
    ORDER BY occurred_at DESC
    LIMIT 3
""")

rows = cursor.fetchall()

print(f"\n{'='*80}")
print(f"ERRORS IN DATABASE: {len(rows)} recent entries")
print(f"{'='*80}\n")

for row in rows:
    print(f"ID: {row[0]}")
    print(f"Type: {row[1]}")
    print(f"Message: {row[2]}")
    print(f"Has Stack Trace: {row[3]}")
    print(f"Source: {row[4]}")
    print(f"User Agent: {row[5]}")
    if row[6]:
        try:
            metadata = json.loads(row[6])
            print(f"Metadata: {json.dumps(metadata, indent=2)}")
        except:
            print(f"Metadata: {row[6]}")
    print(f"Occurred At: {row[7]}")
    print(f"{'-'*80}\n")

conn.close()
