import sqlite3
conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()
cursor.execute("SELECT email, preferred_depth FROM users WHERE email LIKE '%regression%' LIMIT 1")
result = cursor.fetchone()
if result:
    print(f"Email: {result[0]}, preferred_depth: {result[1]}")
else:
    print("No user found")
conn.close()
