import sqlite3

conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db')
cursor = conn.cursor()

cursor.execute("SELECT id, email, name, role FROM users LIMIT 10")
users = cursor.fetchall()

print(f"Total users: {len(users)}")
for user in users:
    print(f"ID: {user[0][:20]}... | Email: {user[1]} | Name: {user[2]} | Role: {user[3]}")

conn.close()
