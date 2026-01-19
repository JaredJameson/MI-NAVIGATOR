import sqlite3
conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
for col in columns:
    print(f"{col[1]} - {col[2]}")
conn.close()
