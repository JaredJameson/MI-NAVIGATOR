import sqlite3

conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db')
cursor = conn.cursor()

cursor.execute("SELECT id, email, role FROM users LIMIT 10")
users = cursor.fetchall()

print("Users in database:")
for user_id, email, role in users:
    print(f"  {email} ({role}) - ID: {user_id}")

conn.close()
