import sqlite3

conn = sqlite3.connect('backend/mi_navigator.db')
cursor = conn.cursor()

# Check sessions
cursor.execute("""
SELECT s.id, u.email, s.expires_at, s.created_at 
FROM sessions s 
JOIN users u ON s.user_id = u.id 
WHERE u.email LIKE '%test%' OR u.email = 'user@example.com'
ORDER BY s.created_at DESC 
LIMIT 5
""")

sessions = cursor.fetchall()
print("Recent sessions:")
for s in sessions:
    print(f"  - {s[1]} | Expires: {s[2]} | Created: {s[3]}")

conn.close()
