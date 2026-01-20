import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Get the test user's preferences
cursor.execute("""
    SELECT email, preferred_depth, preferred_language, preferred_format
    FROM users
    WHERE email LIKE '%testuser328%' OR email LIKE '%user@example%'
    ORDER BY created_at DESC
    LIMIT 5
""")

rows = cursor.fetchall()
if rows:
    print("User preferences:")
    for row in rows:
        print(f"  Email: {row[0]}")
        print(f"  Preferred Depth: {row[1]}")
        print(f"  Preferred Language: {row[2]}")
        print(f"  Preferred Format: {row[3]}")
        print()
else:
    print("No users found")

conn.close()
