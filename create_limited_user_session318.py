#!/usr/bin/env python3
"""Create user at usage limit to test enforcement"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.analytics_event import AnalyticsEvent, EventType
from app.core.security import get_password_hash
import uuid

DATABASE_URL = "sqlite:///./mi_navigator.db"

def create_limited_user():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create user at limit
        user_email = "limited_user@test.com"

        # Delete existing
        existing = session.execute(
            select(User).where(User.email == user_email)
        ).scalar_one_or_none()

        if existing:
            # Delete their events first
            session.execute(
                select(AnalyticsEvent).where(AnalyticsEvent.user_id == str(existing.id))
            )
            for event in session.execute(select(AnalyticsEvent).where(AnalyticsEvent.user_id == str(existing.id))).scalars():
                session.delete(event)

            session.delete(existing)
            session.commit()
            print(f"✓ Deleted existing user: {user_email}")

        # Create new user
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=user_email,
            password_hash=get_password_hash("Test123!"),
            name="Limited User",
            role="user",
            two_factor_enabled=False,
            is_active=True,
            email_verified=True,
            onboarding_completed=True
        )
        session.add(user)
        session.commit()

        # Create 100 analytics events (at limit)
        now = datetime.utcnow()
        for i in range(100):
            event = AnalyticsEvent(
                id=uuid.uuid4(),
                user_id=str(user_id),
                event_type=EventType.CHAT_MESSAGE_SENT,
                event_data={"test": True, "index": i},
                created_at=now
            )
            session.add(event)

        session.commit()

        print(f"✅ Created user: {user_email}")
        print(f"   Password: Test123!")
        print(f"   Analytics events: 100 (AT LIMIT)")
        print(f"   Role: user (limit: 100)")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    create_limited_user()
