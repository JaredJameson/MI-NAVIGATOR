#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend/mi_navigator.db')
cursor = conn.cursor()

# Check if feature_flags table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feature_flags'")
table = cursor.fetchone()

if table:
    print("✓ feature_flags table exists")

    # Get all feature flags
    cursor.execute("SELECT key, name, enabled FROM feature_flags")
    flags = cursor.fetchall()

    print(f"\nFound {len(flags)} feature flags:")
    for key, name, enabled in flags:
        status = "ENABLED" if enabled else "DISABLED"
        print(f"  - {key}: {name} [{status}]")
else:
    print("✗ feature_flags table does not exist")

conn.close()
