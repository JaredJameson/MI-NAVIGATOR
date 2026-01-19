#!/usr/bin/env python3
"""Mark Feature #91 as failing due to regression test failure."""

import sqlite3

# Connect to features database
conn = sqlite3.connect('features.db')
cursor = conn.cursor()

# Update feature #91 to failing
cursor.execute("UPDATE features SET passes = 0 WHERE id = 91")
conn.commit()

# Verify the change
cursor.execute("SELECT id, name, passes, in_progress FROM features WHERE id = 91")
result = cursor.fetchone()
print(f"Feature #{result[0]}: {result[1]}")
print(f"Passes: {result[2]}")
print(f"In Progress: {result[3]}")

conn.close()
