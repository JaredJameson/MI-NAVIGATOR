import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

cursor.execute("SELECT id, email, role, is_active FROM users ORDER BY created_at DESC LIMIT 10")
users = cursor.fetchall()

print("Users in database:")
for user in users:
    print(f"  ID: {user[0]}")
    print(f"  Email: {user[1]}")
    print(f"  Role: {user[2]}")
    print(f"  Active: {user[3]}")
    print()

conn.close()
