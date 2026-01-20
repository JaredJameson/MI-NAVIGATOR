import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()
cursor.execute('SELECT email, role FROM users LIMIT 5')
users = cursor.fetchall()
for user in users:
    print(f'{user[0]} - {user[1]}')
conn.close()
