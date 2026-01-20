#!/usr/bin/env python3
"""Check report IDs in database for Session 328 regression investigation"""
import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Check current user
cursor.execute("SELECT id, email FROM users WHERE email = 'user@example.com'")
user = cursor.fetchone()
print(f"Current user: {user}")

# Check report IDs in database
cursor.execute("SELECT id, title, created_by FROM reports WHERE id LIKE 'pagination_test%' LIMIT 10")
reports = cursor.fetchall()
print(f"\nReports in DB (first 10):")
for r in reports:
    print(f"  ID: {r[0]}, Title: {r[1]}, Owner: {r[2]}")

# Count total pagination test reports
cursor.execute("SELECT COUNT(*) FROM reports WHERE id LIKE 'pagination_test%'")
count = cursor.fetchone()[0]
print(f"\nTotal pagination test reports: {count}")

conn.close()
