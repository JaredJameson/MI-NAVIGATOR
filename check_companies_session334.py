import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()
cursor.execute('SELECT nip, name FROM companies LIMIT 10')
companies = cursor.fetchall()
print(f"Found {len(companies)} companies:")
for nip, name in companies:
    print(f"  {nip}: {name}")
conn.close()
