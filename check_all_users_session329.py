import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Sprawdź wszystkich użytkowników
cursor.execute('SELECT id, email, name, role FROM users')
users = cursor.fetchall()
print(f'All users in database: {len(users)}')
for user in users:
    print(f'  - {user}')

# Sprawdź przykładowe raporty
cursor.execute('SELECT id, title, owner_id FROM reports LIMIT 10')
reports = cursor.fetchall()
print(f'\nFirst 10 reports:')
for report in reports:
    print(f'  - {report}')

conn.close()
