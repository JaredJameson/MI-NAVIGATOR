#!/usr/bin/env python3
import sqlite3

db_path = '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get report details
print("=== Report Details ===")
cursor.execute("SELECT id, slug, title, user_id FROM reports WHERE slug = 'pagination_test_0001'")
report = cursor.fetchone()
if report:
    print(f"Report ID: {report[0]}")
    print(f"Slug: {report[1]}")
    print(f"Title: {report[2]}")
    print(f"Owner User ID: {report[3]}")
    owner_id = report[3]
else:
    print("Report not found!")
    exit(1)

# Get owner details
print("\n=== Report Owner ===")
cursor.execute("SELECT id, email, role FROM users WHERE id = ?", (owner_id,))
owner = cursor.fetchone()
if owner:
    print(f"User ID: {owner[0]}")
    print(f"Email: {owner[1]}")
    print(f"Role: {owner[2]}")

# Get current logged in user (user@example.com)
print("\n=== Current User (user@example.com) ===")
cursor.execute("SELECT id, email, role FROM users WHERE email = 'user@example.com'")
current = cursor.fetchone()
if current:
    print(f"User ID: {current[0]}")
    print(f"Email: {current[1]}")
    print(f"Role: {current[2]}")

    # Check if they match
    print("\n=== RESULT ===")
    if current[0] == owner_id:
        print("✅ SAME USER - User should be able to access this report")
        print("❌ 403 ERROR = REGRESSION!")
    else:
        print("✅ DIFFERENT USERS - 403 is correct behavior (data isolation working)")
        print(f"Current user ID: {current[0]}, Report owner ID: {owner_id}")
else:
    print("Current user not found!")

conn.close()
