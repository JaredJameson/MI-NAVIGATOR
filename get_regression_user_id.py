import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()
cursor.execute("SELECT id, email FROM users WHERE email = 'regression_test@test.com'")
result = cursor.fetchone()
if result:
    print(f"User ID: {result[0]}")
    print(f"Email: {result[1]}")
else:
    print("User not found")
conn.close()
