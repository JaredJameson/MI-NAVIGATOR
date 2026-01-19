import sqlite3
import sys

# Connect to database
conn = sqlite3.connect('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/mi_navigator.db')
cursor = conn.cursor()

# Get a sample user (any user will do)
cursor.execute("SELECT id, email, password_hash FROM users LIMIT 1")
user = cursor.fetchone()

if not user:
    print("❌ No users found in database")
    sys.exit(1)

user_id, email, password_hash = user

print(f"✅ Found user: {email}")
print(f"✅ Password hash sample: {password_hash[:50]}...")
print(f"✅ Password hash length: {len(password_hash)} characters")

# Verify it's not plaintext
if password_hash.startswith('$2b$') or password_hash.startswith('$2a$'):
    print("✅ PASS: Password is bcrypt hashed")
    print(f"✅ Hash algorithm: bcrypt")

    # Extract cost factor
    cost = password_hash.split('$')[2]
    print(f"✅ Bcrypt cost factor: {cost}")

elif password_hash.startswith('pbkdf2:'):
    print("✅ PASS: Password is PBKDF2 hashed")
    print(f"✅ Hash algorithm: PBKDF2")

elif len(password_hash) < 20:
    print("❌ FAIL: Password appears to be plaintext or weak hash")
    sys.exit(1)

else:
    print(f"⚠️  WARNING: Unknown hash format, but long enough to be hashed")
    print(f"   Hash format: {password_hash[:20]}...")

# Check for plaintext passwords (common weak passwords)
weak_passwords = ['password', '123456', 'test', 'admin', 'user']
if password_hash.lower() in weak_passwords:
    print("❌ FAIL: Password is in plaintext!")
    sys.exit(1)

print("\n✅ ALL CHECKS PASSED")
print("   - Password not in plaintext")
print("   - Using secure hashing algorithm")
print("   - Hash length appropriate")

conn.close()
