import sqlite3

conn = sqlite3.connect('backend/mi_navigator.db')
cursor = conn.cursor()

cursor.execute('SELECT id, email, name, role FROM users LIMIT 10')
users = cursor.fetchall()

print("Existing users:")
for user in users:
    print(f"ID: {user[0]}, Email: {user[1]}, Name: {user[2]}, Role: {user[3]}")

conn.close()
