import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Get password hash from a working user
cursor.execute("SELECT password_hash FROM users WHERE email = 'simple@test.com' LIMIT 1")
result = cursor.fetchone()

if result:
    hash_to_copy = result[0]
    
    # Update feature211test user with this hash
    cursor.execute("""
        UPDATE users 
        SET password_hash = ?,
            is_active = 1,
            email_verified = 1,
            two_factor_enabled = 0
        WHERE email = 'feature211test@example.com'
    """, (hash_to_copy,))
    
    conn.commit()
    print(f"✓ Password hash copied")
    print(f"  Try logging in with the same password as simple@test.com")
else:
    print("Could not find source password")

conn.close()
