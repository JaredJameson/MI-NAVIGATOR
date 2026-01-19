import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Check for reports
cursor.execute("SELECT id, title, created_at FROM reports ORDER BY created_at DESC LIMIT 5")
reports = cursor.fetchall()

print("Reports in database:")
for report in reports:
    print(f"ID: {report[0]}, Title: {report[1]}, Created: {report[2]}")

print(f"\nTotal reports: {len(reports)}")

conn.close()
