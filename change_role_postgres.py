import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="minavigator",
    user="minavigator",
    password="minavigator"
)

cursor = conn.cursor()

user_id = "ca99baa1-8d19-4466-bbb4-5bfbcc9afc3b"

cursor.execute("""
    UPDATE users 
    SET role = 'user'
    WHERE id = %s
""", (user_id,))

conn.commit()

if cursor.rowcount > 0:
    print("✓ Role changed to 'user'")
    
    # Verify
    cursor.execute("SELECT email, role FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    print(f"  Email: {user[0]}")
    print(f"  Role: {user[1]}")
else:
    print("✗ User not found")

cursor.close()
conn.close()
