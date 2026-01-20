import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Find user by email
cursor.execute("SELECT id, email, role FROM users WHERE email = 'testlimit320@test.com'")
user = cursor.fetchone()

if user:
    print(f"Found user:")
    print(f"  ID: {user[0]}")
    print(f"  Email: {user[1]}")
    print(f"  Role: {user[2]}")
else:
    print("User not found")
    
    # Show last 5 users
    print("\nLast 5 users:")
    cursor.execute("SELECT id, email, role FROM users ORDER BY created_at DESC LIMIT 5")
    for u in cursor.fetchall():
        print(f"  {u[1]} (role: {u[2]})")

conn.close()
