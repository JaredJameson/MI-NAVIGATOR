import asyncio
import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

from sqlalchemy import select
from app.database import async_session_maker
from app.models.user import User

async def check_user():
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.email == 'session187test@example.com')
        )
        user = result.scalar_one_or_none()
        if user:
            print(f'Email: {user.email}')
            print(f'Industry: {user.industry}')
            print(f'Industry Segment: {user.industry_segment}')
            print(f'User Role: {user.user_role}')
            print(f'Onboarding Completed: {user.onboarding_completed}')
        else:
            print('User not found')

asyncio.run(check_user())
