#!/usr/bin/env python3
"""
Add 99 analytics events using raw SQL to reach usage limit for testing Feature #211
"""
import asyncio
import uuid
from datetime import datetime
import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def add_events():
    """Add 99 ANALYSIS_COMPLETED events for session343@test.com user"""

    async with AsyncSessionLocal() as session:
        # Get user ID
        result = await session.execute(
            text("SELECT id, email FROM users WHERE email = :email"),
            {"email": "session343@test.com"}
        )
        user_row = result.first()

        if not user_row:
            print("ERROR: User session343@test.com not found!")
            return

        user_id = user_row[0]
        print(f"Found user: {user_row[1]} (ID: {user_id})")

        # Check current count
        result = await session.execute(
            text("""
                SELECT COUNT(*) FROM analytics_events
                WHERE user_id = :user_id
                AND event_type = :event_type
                AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
            """),
            {"user_id": user_id, "event_type": "analysis_completed"}
        )
        current_count = result.scalar()
        print(f"Current ANALYSIS_COMPLETED events this month: {current_count}")

        # Add events to reach 100 total
        events_to_add = 100 - current_count

        if events_to_add <= 0:
            print(f"Already at or above limit! Current: {current_count}")
            return

        print(f"Adding {events_to_add} events...")

        for i in range(events_to_add):
            event_id = str(uuid.uuid4())
            await session.execute(
                text("""
                    INSERT INTO analytics_events
                    (id, event_type, event_name, user_id, event_metadata, created_at)
                    VALUES (:id, :event_type, :event_name, :user_id, :metadata, :created_at)
                """),
                {
                    "id": event_id,
                    "event_type": "analysis_completed",
                    "event_name": "Market Analysis Completed",
                    "user_id": user_id,
                    "metadata": '{"test": true}',
                    "created_at": datetime.utcnow().isoformat()
                }
            )

        await session.commit()
        print(f"✅ Successfully added {events_to_add} events!")

        # Verify final count
        result = await session.execute(
            text("""
                SELECT COUNT(*) FROM analytics_events
                WHERE user_id = :user_id
                AND event_type = :event_type
                AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
            """),
            {"user_id": user_id, "event_type": "analysis_completed"}
        )
        final_count = result.scalar()
        print(f"Final ANALYSIS_COMPLETED events this month: {final_count}")

if __name__ == "__main__":
    asyncio.run(add_events())
