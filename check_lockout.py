import sqlite3
import sys
from datetime import datetime, timedelta

conn = sqlite3.connect('backend/mi_navigator.db')
cursor = conn.cursor()

if len(sys.argv) > 1 and sys.argv[1] == 'reset':
    email = sys.argv[2] if len(sys.argv) > 2 else "test@example.com"
    cursor.execute('UPDATE users SET failed_login_attempts=0, account_locked_until=NULL WHERE email=?', (email,))
    conn.commit()
    print(f"Reset successful for {email}")
elif len(sys.argv) > 1 and sys.argv[1] == 'expire':
    email = sys.argv[2] if len(sys.argv) > 2 else "test@example.com"
    # Set lockout to past (1 minute ago) to simulate expiration
    past_time = (datetime.utcnow() - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('UPDATE users SET account_locked_until=? WHERE email=?', (past_time, email))
    conn.commit()
    print(f"Set lockout expiry to past for {email}: {past_time}")
else:
    email = sys.argv[1] if len(sys.argv) > 1 else "test@example.com"
    cursor.execute('SELECT email, failed_login_attempts, account_locked_until FROM users WHERE email=?', (email,))
    result = cursor.fetchone()
    if result:
        print(f"Email: {result[0]}")
        print(f"Failed attempts: {result[1]}")
        print(f"Locked until: {result[2]}")
    else:
        print("User not found")

conn.close()
