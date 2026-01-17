#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend/app.db')
cursor = conn.cursor()

# Get table info
cursor.execute("PRAGMA table_info(users);")
columns = cursor.fetchall()

print("Users table columns:")
for col in columns:
    print(f"  {col[1]} - {col[2]}")

# Check if timezone exists
has_timezone = any(col[1] == 'timezone' for col in columns)
print(f"\nTimezone column exists: {has_timezone}")

conn.close()
