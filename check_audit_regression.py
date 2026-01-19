import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Check reports
print("=== REPORTS ===")
cursor.execute("SELECT id, title, type, created_at FROM reports ORDER BY created_at DESC LIMIT 5")
reports = cursor.fetchall()
for r in reports:
    print(f"ID: {r[0]}, Title: {r[1]}, Type: {r[2]}, Created: {r[3]}")

print("\n=== AUDIT LOGS ===")
# Check if audit_logs table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_logs'")
if cursor.fetchone():
    cursor.execute("SELECT id, user_id, action, resource_type, resource_id, created_at FROM audit_logs ORDER BY created_at DESC LIMIT 10")
    logs = cursor.fetchall()
    if logs:
        for log in logs:
            print(f"ID: {log[0]}, User: {log[1]}, Action: {log[2]}, Resource: {log[3]}/{log[4]}, Time: {log[5]}")
    else:
        print("No audit logs found")
else:
    print("audit_logs table does not exist")

conn.close()
