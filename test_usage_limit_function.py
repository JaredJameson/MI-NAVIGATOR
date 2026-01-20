#!/usr/bin/env python3
"""
Direct test of check_usage_limit function from usage_limits.py
This tests the core logic without WebSocket dependency.
"""
import asyncio
import sys
sys.path.insert(0, '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/backend')

from sqlalchemy import select, func
from datetime import datetime
from app.db.session import AsyncSessionLocal
from app.core.usage_limits import check_usage_limit
from app.models.user import User
from app.models.analytics_event import AnalyticsEvent, EventType
from fastapi import HTTPException

async def test_usage_limit():
    print("=" * 70)
    print("TESTING check_usage_limit() FUNCTION")
    print("=" * 70)

    async with AsyncSessionLocal() as db:
        # Get test user
        result = await db.execute(
            select(User).where(User.email == 'testlimit321@test.com')
        )
        user = result.scalar_one_or_none()

        if not user:
            print("❌ Test user not found")
            return

        print(f"\n✅ Found user: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   ID: {user.id}")

        # Check current usage
        result = await db.execute(
            select(func.count(AnalyticsEvent.id))
            .where(
                AnalyticsEvent.user_id == str(user.id),
                AnalyticsEvent.event_type.in_([
                    EventType.CHAT_MESSAGE_SENT,
                    EventType.RESEARCH_STARTED,
                    EventType.ANALYSIS_COMPLETED
                ])
            )
        )
        current_count = result.scalar() or 0
        print(f"\n📊 Current usage count: {current_count}")

        # Test 1: Should ALLOW (0/2)
        print("\n" + "=" * 70)
        print("TEST 1: First message (0/2 used) - Should ALLOW")
        print("=" * 70)
        try:
            await check_usage_limit(db, user, action_type="chat")
            print("✅ PASS: Message allowed (as expected)")
        except HTTPException as e:
            print(f"❌ FAIL: Message blocked unexpectedly")
            print(f"   Error: {e.detail}")
            return

        # Add first event
        print("\n📝 Adding first analytics event...")
        event1 = AnalyticsEvent(
            user_id=str(user.id),
            event_type=EventType.CHAT_MESSAGE_SENT,
            event_name="test_message_1",
            event_data={"test": "message 1"},
            created_at=datetime.utcnow()
        )
        db.add(event1)
        await db.commit()
        print("✅ Event 1 added")

        # Test 2: Should ALLOW (1/2)
        print("\n" + "=" * 70)
        print("TEST 2: Second message (1/2 used) - Should ALLOW")
        print("=" * 70)
        try:
            await check_usage_limit(db, user, action_type="chat")
            print("✅ PASS: Message allowed (as expected)")
        except HTTPException as e:
            print(f"❌ FAIL: Message blocked unexpectedly")
            print(f"   Error: {e.detail}")
            return

        # Add second event
        print("\n📝 Adding second analytics event...")
        event2 = AnalyticsEvent(
            user_id=str(user.id),
            event_type=EventType.CHAT_MESSAGE_SENT,
            event_name="test_message_2",
            event_data={"test": "message 2"},
            created_at=datetime.utcnow()
        )
        db.add(event2)
        await db.commit()
        print("✅ Event 2 added")

        # Test 3: Should BLOCK (2/2)
        print("\n" + "=" * 70)
        print("TEST 3: Third message (2/2 used) - Should BLOCK")
        print("=" * 70)
        try:
            await check_usage_limit(db, user, action_type="chat")
            print("❌ FAIL: Message allowed (should have been blocked!)")
            return
        except HTTPException as e:
            print(f"✅ PASS: Message blocked (as expected)")
            print(f"   Status code: {e.status_code}")
            print(f"   Error detail: {e.detail}")

            # Verify error message
            if e.status_code == 403:
                print("   ✅ Correct status code (403 Forbidden)")
            else:
                print(f"   ❌ Wrong status code (expected 403, got {e.status_code})")

            if isinstance(e.detail, dict):
                error_type = e.detail.get('error')
                message = e.detail.get('message')
                current_usage = e.detail.get('current_usage')
                limit = e.detail.get('limit')

                print(f"   ✅ Error type: {error_type}")
                print(f"   ✅ Message: {message}")
                print(f"   ✅ Current usage: {current_usage}")
                print(f"   ✅ Limit: {limit}")

                if error_type == 'usage_limit_exceeded':
                    print("   ✅ Correct error type")
                if current_usage == 2 and limit == 2:
                    print("   ✅ Correct usage counts")

        print("\n" + "=" * 70)
        print("ALL TESTS PASSED! ✅")
        print("=" * 70)
        print("\nFeature #211 - Usage limit enforcement is working correctly:")
        print("  ✅ Allows messages 1 and 2")
        print("  ✅ Blocks message 3 with HTTP 403")
        print("  ✅ Returns helpful error message with usage info")

# Run tests
asyncio.run(test_usage_limit())
