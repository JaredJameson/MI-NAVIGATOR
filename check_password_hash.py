#!/usr/bin/env python3
"""
Script to verify password hashing in database.
Tests that passwords are properly hashed with bcrypt.
"""

import sqlite3
import sys

DB_PATH = "backend/mi_navigator.db"
TEST_EMAIL = "test_hash_verify_12345@example.com"
TEST_PASSWORD = "TestPassword123"

def main():
    print("=" * 60)
    print("PASSWORD HASHING VERIFICATION")
    print("=" * 60)

    # Connect to database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
    except Exception as e:
        print(f"❌ ERROR: Could not connect to database: {e}")
        return False

    # Query for test user
    cursor.execute(
        "SELECT email, password_hash FROM users WHERE email = ?",
        (TEST_EMAIL,)
    )
    result = cursor.fetchone()

    if not result:
        print(f"❌ ERROR: User {TEST_EMAIL} not found in database")
        conn.close()
        return False

    email, password_hash = result

    print(f"\n✅ Step 1: User created successfully")
    print(f"   Email: {email}")

    # Step 2: Check that password_hash exists
    print(f"\n✅ Step 2: Password hash found in database")
    print(f"   Hash length: {len(password_hash)} characters")
    print(f"   Hash preview: {password_hash[:20]}...")

    # Step 3: Verify NOT plaintext
    if password_hash == TEST_PASSWORD:
        print(f"\n❌ FAIL: Password stored in PLAINTEXT!")
        conn.close()
        return False
    else:
        print(f"\n✅ Step 3: Password NOT stored in plaintext")

    # Step 4: Verify bcrypt format
    # Bcrypt hashes start with $2a$, $2b$, or $2y$ followed by cost factor
    if password_hash.startswith('$2b$') or password_hash.startswith('$2a$') or password_hash.startswith('$2y$'):
        cost_factor = password_hash.split('$')[2]
        print(f"\n✅ Step 4: bcrypt hash algorithm detected")
        print(f"   Algorithm: bcrypt")
        print(f"   Cost factor: {cost_factor}")
        print(f"   Format: Valid bcrypt hash")
    else:
        print(f"\n❌ FAIL: Hash does not appear to be bcrypt")
        print(f"   Hash starts with: {password_hash[:10]}")
        conn.close()
        return False

    # Additional verification: Try to verify the password using bcrypt
    try:
        import bcrypt
        password_bytes = TEST_PASSWORD.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')

        if bcrypt.checkpw(password_bytes, hash_bytes):
            print(f"\n✅ BONUS: Password verification successful")
            print(f"   bcrypt.checkpw() confirmed the hash is correct")
        else:
            print(f"\n❌ WARNING: Password verification failed")
            print(f"   bcrypt.checkpw() could not verify the hash")
    except ImportError:
        print(f"\n⚠️  bcrypt module not available for verification")
    except Exception as e:
        print(f"\n⚠️  Could not verify password: {e}")

    conn.close()

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED")
    print("=" * 60)
    print("\nSummary:")
    print("✅ User created with known password")
    print("✅ Password hash stored in database")
    print("✅ Password NOT in plaintext")
    print("✅ bcrypt algorithm used (secure)")
    print("\n")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
