import asyncio
import sys
sys.path.append('/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

from app.database import get_db
from sqlalchemy import select
from app.models.user import User

async def check_2fa_users():
    async for db in get_db():
        result = await db.execute(select(User).where(User.two_factor_enabled == True))
        users = result.scalars().all()
        print(f'Users with 2FA enabled: {len(users)}')
        for user in users:
            print(f'  - Email: {user.email}')
            print(f'    ID: {user.id}')
            print(f'    2FA Secret exists: {user.two_factor_secret is not None}')
            print()

        # Also show all users
        result = await db.execute(select(User))
        all_users = result.scalars().all()
        print(f'\nTotal users: {len(all_users)}')
        for user in all_users:
            print(f'  - {user.email} (2FA: {user.two_factor_enabled})')
        break

asyncio.run(check_2fa_users())
