import sqlite3

conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT email, name, two_factor_enabled 
    FROM users 
    WHERE two_factor_enabled = 0 OR two_factor_enabled IS NULL
    LIMIT 5
""")
users = cursor.fetchall()

print("Users without 2FA:")
for user in users:
    print(f"  Email: {user[0]} | Name: {user[1]}")

conn.close()
