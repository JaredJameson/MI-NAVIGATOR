import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Check for test users
cursor.execute("""
    SELECT email, id, role
    FROM users
    WHERE email LIKE '%session%' OR email LIKE '%test%'
    ORDER BY created_at DESC
    LIMIT 5
""")

users = cursor.fetchall()
if users:
    print("Available test users:")
    for email, user_id, role in users:
        print(f"  - {email} (ID: {user_id[:8]}..., Role: {role})")
else:
    print("No test users found")

conn.close()
