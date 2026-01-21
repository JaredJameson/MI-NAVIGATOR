import asyncio
import asyncpg

# All columns from User model (line numbers from user.py)
REQUIRED_COLUMNS = {
    'id': 'UUID PRIMARY KEY',
    'email': 'VARCHAR(255) UNIQUE NOT NULL',
    'password_hash': 'VARCHAR(255) NOT NULL',
    'name': 'VARCHAR(255)',
    'avatar_url': 'VARCHAR(500)',
    'role': "VARCHAR(20) DEFAULT 'user' NOT NULL",
    'industry': 'VARCHAR(100)',
    'industry_segment': 'VARCHAR(100)',
    'user_role': 'VARCHAR(50)',
    'preferred_language': "VARCHAR(5) DEFAULT 'pl'",
    'preferred_depth': "VARCHAR(20) DEFAULT 'standard'",
    'preferred_format': "VARCHAR(10) DEFAULT 'pdf'",
    'preferred_currency': "VARCHAR(3) DEFAULT 'PLN' NOT NULL",
    'timezone': "VARCHAR(50) DEFAULT 'Europe/Warsaw' NOT NULL",
    'report_branding': 'BOOLEAN DEFAULT true NOT NULL',
    'onboarding_completed': 'BOOLEAN DEFAULT false',
    'is_active': 'BOOLEAN DEFAULT true',
    'email_verified': 'BOOLEAN DEFAULT false',
    'failed_login_attempts': 'INTEGER DEFAULT 0',
    'account_locked_until': 'TIMESTAMP',
    'totp_secret': 'VARCHAR(32)',
    'two_factor_enabled': 'BOOLEAN DEFAULT false',
    'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
    'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
    'last_login_at': 'TIMESTAMP'
}

async def sync_columns():
    conn = await asyncpg.connect(
        host='localhost',
        port=5439,
        user='minavigator',
        password='minavigator',
        database='minavigator'
    )
    
    try:
        # Get existing columns
        existing = await conn.fetch("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'users'
        """)
        existing_cols = {row['column_name'] for row in existing}
        
        print(f"Existing columns: {len(existing_cols)}")
        print(f"Required columns: {len(REQUIRED_COLUMNS)}")
        
        # Find missing columns
        missing = set(REQUIRED_COLUMNS.keys()) - existing_cols
        
        if not missing:
            print("✅ All columns exist!")
            return
        
        print(f"\n❌ Missing {len(missing)} columns: {sorted(missing)}\n")
        
        # Add missing columns
        for col in sorted(missing):
            col_def = REQUIRED_COLUMNS[col]
            try:
                await conn.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col} {col_def}")
                print(f"✅ Added: {col}")
            except Exception as e:
                print(f"❌ Failed to add {col}: {e}")
        
        print("\n✅ Sync complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()

asyncio.run(sync_columns())
