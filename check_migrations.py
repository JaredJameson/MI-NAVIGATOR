import asyncio
import asyncpg

async def check_migrations():
    try:
        conn = await asyncpg.connect(
            host='localhost',
            port=5439,
            user='postgres',
            password='postgres',
            database='mi_navigator'
        )

        # Check current migration version
        version = await conn.fetchval("SELECT version_num FROM alembic_version")
        print(f"Current migration version: {version}")

        # Check if preferred_currency column exists
        result = await conn.fetch("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'preferred_currency'
        """)

        if result:
            print("✅ preferred_currency column EXISTS")
        else:
            print("❌ preferred_currency column DOES NOT EXIST")

        # List all user columns
        columns = await conn.fetch("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """)
        print("\nAll user table columns:")
        for col in columns:
            print(f"  - {col['column_name']}")

        await conn.close()
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(check_migrations())
