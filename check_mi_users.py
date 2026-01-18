import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()
cursor.execute('SELECT id, email, is_active FROM users LIMIT 10')
print("ID | Email | Active")
print("-" * 60)
for row in cursor.fetchall():
    print(f"{row[0]} | {row[1]} | {row[2]}")
conn.close()
