import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()
cursor.execute("SELECT email, preferred_language FROM users WHERE email LIKE 'testuser%' LIMIT 5")
for row in cursor.fetchall():
    print(f"Email: {row[0]}, Language: {row[1]}")
conn.close()
