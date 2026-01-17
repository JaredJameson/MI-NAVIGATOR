import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sys
sys.path.insert(0, './backend')

from app.models.user import User
from app.core.security import get_password_hash
import uuid
from datetime import datetime

async def create_test_user():
    # Connect to database
    engine = create_async_engine("sqlite+aiosqlite:///./backend/test.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create test user with known password
        test_email = f"regression_335_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "TestPassword123!"

        user = User(
            id=str(uuid.uuid4()),
            email=test_email,
            name="Regression Test User 335",
            password_hash=get_password_hash(test_password),
            role="user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        print(f"Created user: {user.email}")
        print(f"User ID: {user.id}")
        print(f"Plain password: {test_password}")
        print(f"Password hash: {user.password_hash}")
        print(f"Hash length: {len(user.password_hash)}")
        print(f"Hash algorithm: bcrypt (starts with $2b$)")

        # Verify it's hashed
        if test_password in user.password_hash:
            print("❌ FAILED: Password stored in plaintext!")
        else:
            print("✅ PASSED: Password is hashed")

        if user.password_hash.startswith("$2b$"):
            print("✅ PASSED: Using bcrypt algorithm")
        else:
            print("❌ FAILED: Not using bcrypt")

        return user.email, user.id

asyncio.run(create_test_user())
