import sqlite3

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Use known bcrypt hash for "TestPass123"
known_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgOq8/F8i"

cursor.execute("""
    UPDATE users
    SET password_hash = ?,
        is_active = 1,
        email_verified = 1,
        two_factor_enabled = 0
    WHERE email = 'feature211test@example.com'
""", (known_hash,))

conn.commit()

print("✓ Password set to: TestPass123")
print("  Email: feature211test@example.com")

conn.close()
