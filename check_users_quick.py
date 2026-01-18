import sqlite3

conn = sqlite3.connect('assistant.db')
cursor = conn.cursor()
cursor.execute('SELECT id, email FROM users LIMIT 5')
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]}")
conn.close()
