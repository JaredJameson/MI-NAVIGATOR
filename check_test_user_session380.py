import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5439,
    database="minavigator",
    user="minavigator",
    password="minavigator"
)
cur = conn.cursor()

# Check if user exists
cur.execute("SELECT id, email, name, created_at FROM users WHERE email = 'test_regression_session380@example.com'")
user = cur.fetchone()

if user:
    print(f"✅ User found in database!")
    print(f"   ID: {user[0]}")
    print(f"   Email: {user[1]}")
    print(f"   Name: {user[2]}")
    print(f"   Created: {user[3]}")
else:
    print(f"❌ User NOT found in database!")

cur.close()
conn.close()
