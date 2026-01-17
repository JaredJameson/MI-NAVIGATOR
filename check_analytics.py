#!/usr/bin/env python3
"""Check analytics events in database"""
import sqlite3
import json
from datetime import datetime

db_path = 'backend/mi_navigator.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analytics_events'")
table_exists = cursor.fetchone()

if table_exists:
    print("✓ analytics_events table exists")

    # Count events
    cursor.execute("SELECT COUNT(*) FROM analytics_events")
    count = cursor.fetchone()[0]
    print(f"✓ Total events: {count}")

    # Get recent events
    cursor.execute("""
        SELECT id, event_type, event_name, user_id, event_metadata, created_at
        FROM analytics_events
        ORDER BY created_at DESC
        LIMIT 10
    """)

    events = cursor.fetchall()

    if events:
        print("\n📊 Recent Analytics Events:")
        print("-" * 80)
        for event in events:
            event_id, event_type, event_name, user_id, metadata, created_at = event
            metadata_dict = json.loads(metadata) if metadata else {}
            print(f"Event: {event_name}")
            print(f"  Type: {event_type}")
            print(f"  User ID: {user_id}")
            print(f"  Metadata: {metadata_dict}")
            print(f"  Time: {created_at}")
            print()
    else:
        print("\n⚠️ No events found in database")
else:
    print("❌ analytics_events table does NOT exist")

conn.close()
