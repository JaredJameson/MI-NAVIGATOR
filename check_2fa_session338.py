import sqlite3

conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT email, two_factor_enabled, totp_secret 
    FROM users 
    WHERE email = 'test@example.com'
""")
user = cursor.fetchone()

if user:
    print(f"Email: {user[0]}")
    print(f"2FA Enabled: {user[1]}")
    print(f"TOTP Secret: {user[2]}")
else:
    print("User not found")

conn.close()
