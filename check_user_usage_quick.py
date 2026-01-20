import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Get user info
cursor.execute("SELECT id, email, usage_count, usage_limit FROM users WHERE email = 'user@example.com'")
user = cursor.fetchone()

if user:
    print(f"User ID: {user[0]}")
    print(f"Email: {user[1]}")
    print(f"Usage Count: {user[2]}")
    print(f"Usage Limit: {user[3]}")
    print(f"Remaining: {user[3] - user[2]}")
else:
    print("User not found")

conn.close()
