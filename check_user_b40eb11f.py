import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

user_id = "b40eb11f-7118-4e66-b2cd-a5c130283 9cc"
cursor.execute("SELECT id, email, name, role FROM users WHERE id = ?", (user_id,))
user = cursor.fetchone()
print(f"User: {user}")

conn.close()
