import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()
cursor.execute("SELECT id, email, name, role FROM users LIMIT 10")
users = cursor.fetchall()

print("=== EXISTING USERS IN DATABASE ===")
for user in users:
    print(f"ID: {user[0]}")
    print(f"Email: {user[1]}")
    print(f"Name: {user[2]}")
    print(f"Role: {user[3]}")
    print("-" * 50)

print(f"\nTotal users: {len(users)}")
conn.close()
