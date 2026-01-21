import psycopg2

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port=5439,
    database="market_intelligence",
    user="mi_user",
    password="mi_password"
)
cur = conn.cursor()

# Get first 5 users
cur.execute("SELECT id, email, role, name FROM users ORDER BY created_at DESC LIMIT 5")
users = cur.fetchall()
print("Available test users:")
for user in users:
    print(f"  - {user[1]} (role: {user[2]}, name: {user[3]})")

cur.close()
conn.close()
