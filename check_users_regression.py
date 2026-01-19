import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()
cursor.execute('SELECT id, email, role FROM users LIMIT 3')
users = cursor.fetchall()
for user in users:
    print(f"ID: {user[0]}, Email: {user[1]}, Role: {user[2]}")
conn.close()
