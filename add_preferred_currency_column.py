import asyncio
import asyncpg

async def add_column():
    conn = await asyncpg.connect(
        host='localhost',
        port=5439,
        user='minavigator',
        password='minavigator',
        database='minavigator'
    )
    
    try:
        await conn.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS preferred_currency VARCHAR(3) DEFAULT 'PLN' NOT NULL
        """)
        print("✅ Column 'preferred_currency' added successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()

asyncio.run(add_column())
