import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

conn = sqlite3.connect('mi_navigator.db')
cursor = conn.cursor()

# Hash password
password = "test123"
hashed = pwd_context.hash(password)

# Update user
cursor.execute("""
    UPDATE users 
    SET password_hash = ?, 
        is_active = 1,
        email_verified = 1,
        two_factor_enabled = 0
    WHERE email = 'feature211test@example.com'
""", (hashed,))

conn.commit()

if cursor.rowcount > 0:
    print("✓ Password reset successful")
    print(f"  Email: feature211test@example.com")
    print(f"  Password: {password}")
else:
    print("✗ User not found")

conn.close()
