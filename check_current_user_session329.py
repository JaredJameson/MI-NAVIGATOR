import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Sprawdź wszystkich użytkowników z email zawierającym "user"
cursor.execute("SELECT id, email, name, role FROM users WHERE email LIKE '%user%' ORDER BY email")
users = cursor.fetchall()
print("Users with 'user' in email:")
for user in users:
    print(f"  {user}")

conn.close()
