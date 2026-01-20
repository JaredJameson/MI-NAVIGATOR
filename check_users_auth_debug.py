import sqlite3

conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db')
cursor = conn.cursor()

# Check if users exist
cursor.execute("SELECT email, id, role, password_hash FROM users WHERE email IN ('user@example.com', 'regression_session313@test.com')")
results = cursor.fetchall()

print(f"Found {len(results)} users in database")
print("=" * 70)

for row in results:
    email, user_id, role, pwd_hash = row
    print(f"\nEmail: {email}")
    print(f"ID: {user_id}")
    print(f"Role: {role}")
    print(f"Password hash: {pwd_hash[:80] if pwd_hash else 'NULL'}...")
    print("-" * 70)

# Also check total user count
cursor.execute("SELECT COUNT(*) FROM users")
total = cursor.fetchone()[0]
print(f"\nTotal users in database: {total}")

conn.close()
