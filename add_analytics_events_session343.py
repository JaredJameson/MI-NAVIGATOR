#!/usr/bin/env python3
"""
Add 99 analytics events to reach usage limit for testing Feature #211
"""
import asyncio
import sys
from datetime import datetime
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models.analytics_event import AnalyticsEvent, EventType

async def add_events():
    """Add 99 ANALYSIS_COMPLETED events for session343@test.com user"""

    # First get user ID for session343@test.com
    from sqlalchemy import select
    from app.models.user import User

    async with AsyncSessionLocal() as session:
        # Get user
        result = await session.execute(
            select(User).where(User.email == "session343@test.com")
        )
        user = result.scalar_one_or_none()

        if not user:
            print("ERROR: User session343@test.com not found!")
            return

        print(f"Found user: {user.email} (ID: {user.id})")

        # Check current count
        result = await session.execute(
            select(AnalyticsEvent).where(
                AnalyticsEvent.user_id == str(user.id),
                AnalyticsEvent.event_type == EventType.ANALYSIS_COMPLETED
            )
        )
        current_count = len(result.scalars().all())
        print(f"Current ANALYSIS_COMPLETED events: {current_count}")

        # Add 99 more events (we already have 1, so total will be 100)
        events_to_add = 100 - current_count

        if events_to_add <= 0:
            print(f"Already at or above limit! Current: {current_count}")
            return

        print(f"Adding {events_to_add} events...")

        for i in range(events_to_add):
            event = AnalyticsEvent(
                event_type=EventType.ANALYSIS_COMPLETED,
                event_name="Market Analysis Completed",
                user_id=str(user.id),
                event_metadata={"test": True, "batch": i + 1},
                created_at=datetime.utcnow()
            )
            session.add(event)

        await session.commit()
        print(f"✅ Successfully added {events_to_add} events!")

        # Verify
        result = await session.execute(
            select(AnalyticsEvent).where(
                AnalyticsEvent.user_id == str(user.id),
                AnalyticsEvent.event_type == EventType.ANALYSIS_COMPLETED
            )
        )
        final_count = len(result.scalars().all())
        print(f"Final ANALYSIS_COMPLETED events: {final_count}")

if __name__ == "__main__":
    asyncio.run(add_events())
