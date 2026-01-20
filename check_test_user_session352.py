import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    dbname="mi_navigator",
    user="mi_user",
    password="mi_password",
    host="localhost",
    port="5432"
)

cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute("SELECT id, email, name, role FROM users WHERE email LIKE '%test%' OR email LIKE '%session%' ORDER BY created_at DESC LIMIT 5;")
users = cur.fetchall()

print(f"\n=== Test Users (Last 5) ===")
for user in users:
    print(f"ID: {user['id']}")
    print(f"Email: {user['email']}")
    print(f"Name: {user['name']}")
    print(f"Role: {user['role']}")
    print("-" * 40)

cur.close()
conn.close()
