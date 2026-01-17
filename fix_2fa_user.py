#!/usr/bin/env python3
"""
Fix 2FA configuration for test2fa@example.com user
"""
import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

import asyncio
from app.db.session import get_db
from app.models.user import User
from sqlalchemy import select

async def fix_2fa_user():
    async for db in get_db():
        # Get test2fa user
        result = await db.execute(
            select(User).where(User.email == 'test2fa@example.com')
        )
        user = result.scalar_one_or_none()

        if not user:
            print("❌ User test2fa@example.com not found!")
            break

        print(f"\n📋 Current state:")
        print(f"   Email: {user.email}")
        print(f"   two_factor_enabled: {user.two_factor_enabled}")
        print(f"   totp_secret: {'SET' if user.totp_secret else 'NULL'}")
        if user.totp_secret:
            print(f"   totp_secret value: {user.totp_secret}")

        # Fix: Enable 2FA if totp_secret is set
        if user.totp_secret and not user.two_factor_enabled:
            print(f"\n🔧 Fixing: Enabling two_factor_enabled...")
            user.two_factor_enabled = True
            await db.commit()
            await db.refresh(user)
            print(f"✅ Fixed! two_factor_enabled = {user.two_factor_enabled}")
        elif not user.totp_secret:
            print(f"\n⚠️  totp_secret is NULL - setting it...")
            # Use the same secret from generate_totp.py
            user.totp_secret = "RWLS2I4IEEDKXZ4T3HWZLZ5ZV5ALACK2"
            user.two_factor_enabled = True
            await db.commit()
            await db.refresh(user)
            print(f"✅ Fixed! totp_secret and two_factor_enabled both set")
        else:
            print(f"\n✅ Already configured correctly!")

        break

if __name__ == "__main__":
    asyncio.run(fix_2fa_user())
