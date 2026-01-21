import asyncio
import asyncpg

async def add_columns():
    conn = await asyncpg.connect(
        host='localhost',
        port=5439,
        user='minavigator',
        password='minavigator',
        database='minavigator'
    )
    
    try:
        # Add timezone column
        await conn.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Europe/Warsaw' NOT NULL
        """)
        print("✅ Column 'timezone' added")
        
        # Add report_branding column
        await conn.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS report_branding BOOLEAN DEFAULT true NOT NULL
        """)
        print("✅ Column 'report_branding' added")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()

asyncio.run(add_columns())
