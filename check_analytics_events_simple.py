#!/usr/bin/env python3
import sys
sys.path.insert(0, './backend')

import asyncio
from sqlalchemy import text
from app.db.session import engine

async def check_analytics():
    async with engine.begin() as conn:
        # Check if table exists
        result = await conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='analytics_events'"
        ))
        tables = result.fetchall()
        print(f"Tables found: {tables}")

        if tables:
            # Count events
            result = await conn.execute(text("SELECT COUNT(*) FROM analytics_events"))
            count = result.scalar()
            print(f"\nTotal analytics events: {count}")

            if count > 0:
                # Show last 5 events
                result = await conn.execute(text(
                    "SELECT id, event_type, event_name, user_id, created_at FROM analytics_events ORDER BY created_at DESC LIMIT 5"
                ))
                events = result.fetchall()
                print("\nLast 5 events:")
                for event in events:
                    print(f"  {event}")
        else:
            print("\n❌ analytics_events table does NOT exist!")
            print("   This explains why usage counters are not working.")

if __name__ == "__main__":
    asyncio.run(check_analytics())
