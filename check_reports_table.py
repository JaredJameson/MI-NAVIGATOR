import sqlite3
conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%report%'")
tables = cursor.fetchall()
for table in tables:
    print(table[0])
conn.close()
