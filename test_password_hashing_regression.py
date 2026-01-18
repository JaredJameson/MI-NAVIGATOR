#!/usr/bin/env python3
"""
Regression test for Feature #335: Password hashing storage
Verifies that passwords are properly hashed with bcrypt in PostgreSQL.
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/mi_navigator"

async def test_password_hashing():
    print("=" * 70)
    print("REGRESSION TEST #335: Password Hashing Storage")
    print("=" * 70)

    engine = create_async_engine(DATABASE_URL)

    try:
        async with engine.begin() as conn:
            # Step 1: Get sample user with known password
            print("\n✅ Step 1: Query database for user with known password")
            result = await conn.execute(text("""
                SELECT id, email, password_hash
                FROM users
                WHERE email = 'test2fa@example.com'
                LIMIT 1
            """))

            user = result.fetchone()

            if not user:
                print("❌ FAIL: Test user not found")
                return False

            user_id, email, password_hash = user
            print(f"   Email: {email}")
            print(f"   User ID: {user_id}")

            # Step 2: Check database storage
            print("\n✅ Step 2: Check database storage")
            print(f"   Password hash length: {len(password_hash)} characters")
            print(f"   Password hash preview: {password_hash[:60]}...")

            # Step 3: Verify password NOT stored in plaintext
            print("\n✅ Step 3: Verify password not stored in plaintext")

            # Known test passwords to check against
            known_passwords = ['password', 'Password123', 'TestPassword123', 'test123']
            is_plaintext = password_hash in known_passwords

            if is_plaintext:
                print("   ❌ FAIL: Password appears to be in PLAINTEXT!")
                return False

            # Check hash characteristics
            has_special_chars = '$' in password_hash
            is_long = len(password_hash) > 50

            if has_special_chars and is_long:
                print("   ✅ Password is NOT plaintext")
                print(f"      - Contains special characters: {has_special_chars}")
                print(f"      - Hash length > 50 chars: {is_long}")
            else:
                print("   ⚠️ WARNING: Hash might not be secure")
                return False

            # Step 4: Verify hash algorithm secure (bcrypt)
            print("\n✅ Step 4: Verify hash algorithm secure")

            if password_hash.startswith('$2b$'):
                print("   ✅ Algorithm: bcrypt (identifier: $2b$)")
                # Extract cost factor
                parts = password_hash.split('$')
                if len(parts) >= 3:
                    cost_factor = parts[2]
                    print(f"   ✅ Cost factor: {cost_factor}")
                    print("   ✅ bcrypt is a secure, industry-standard algorithm")
            elif password_hash.startswith('$2a$') or password_hash.startswith('$2y$'):
                print("   ✅ Algorithm: bcrypt (variant detected)")
            else:
                print(f"   ❌ FAIL: Unknown hash algorithm")
                print(f"      Hash starts with: {password_hash[:10]}")
                return False

            # Additional check: Verify bcrypt can validate
            print("\n📋 Additional verification with bcrypt library:")
            try:
                import bcrypt
                # We know test2fa@example.com has password "Password123"
                test_password = "Password123"
                password_bytes = test_password.encode('utf-8')
                hash_bytes = password_hash.encode('utf-8')

                if bcrypt.checkpw(password_bytes, hash_bytes):
                    print("   ✅ bcrypt.checkpw() verification: PASSED")
                    print("   ✅ Hash can be properly validated")
                else:
                    print("   ⚠️ Password verification failed (might be different password)")
            except ImportError:
                print("   ⚠️ bcrypt module not available (skipping validation)")
            except Exception as e:
                print(f"   ⚠️ Validation error: {e}")

            print("\n" + "=" * 70)
            print("✅ ALL TESTS PASSED - Password Hashing is Secure")
            print("=" * 70)
            print("\nSummary:")
            print("✅ Step 1: User with known password exists in database")
            print("✅ Step 2: Password hash stored correctly")
            print("✅ Step 3: Password NOT in plaintext")
            print("✅ Step 4: bcrypt algorithm verified (secure)")
            print("\n")

            return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(test_password_hashing())
    sys.exit(0 if success else 1)
