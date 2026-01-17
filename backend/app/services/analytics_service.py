"""
Analytics Service - Helper functions for tracking user events
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.analytics_event import AnalyticsEvent, EventType
from app.models.user import User
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Request
import json


async def track_event(
    db: AsyncSession,
    event_type: EventType,
    event_name: str,
    user: Optional[User] = None,
    session_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None
) -> AnalyticsEvent:
    """
    Track an analytics event to the database

    IMPORTANT: Never include PII (Personally Identifiable Information) in metadata!
    - ✅ OK: {"research_type": "company_profile", "export_format": "pdf"}
    - ❌ NOT OK: {"email": "user@example.com", "company_name": "ACME Corp"}

    Args:
        db: Database session
        event_type: Type of event (from EventType enum)
        event_name: Human-readable event name
        user: User performing the action (optional for anonymous events)
        session_id: Session identifier (optional)
        metadata: Additional metadata as dictionary (NO PII!)
        request: FastAPI request object (optional, for IP/user-agent)

    Returns:
        AnalyticsEvent: Created analytics event entry
    """
    # Extract request metadata
    ip_address = None
    user_agent = None

    if request:
        # Get client IP (handle proxies)
        ip_address = request.client.host if request.client else None

        # Handle X-Forwarded-For header for proxies
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip_address = forwarded_for.split(",")[0].strip()

        # Get user agent
        user_agent = request.headers.get("User-Agent")

    # Create analytics event entry
    event = AnalyticsEvent(
        event_type=event_type,
        event_name=event_name,
        user_id=str(user.id) if user else None,
        session_id=session_id,
        event_metadata=json.dumps(metadata) if metadata else None,
        ip_address=ip_address,
        user_agent=user_agent
    )

    db.add(event)
    await db.commit()
    await db.refresh(event)

    return event


async def get_events(
    db: AsyncSession,
    user_id: Optional[str] = None,
    event_type: Optional[EventType] = None,
    session_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> list[AnalyticsEvent]:
    """
    Query analytics events with filters

    Args:
        db: Database session
        user_id: Filter by user ID (optional)
        event_type: Filter by event type (optional)
        session_id: Filter by session ID (optional)
        start_date: Filter events after this date (optional)
        end_date: Filter events before this date (optional)
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        list[AnalyticsEvent]: List of analytics event entries
    """
    query = select(AnalyticsEvent)

    # Apply filters
    if user_id:
        query = query.where(AnalyticsEvent.user_id == user_id)
    if event_type:
        query = query.where(AnalyticsEvent.event_type == event_type)
    if session_id:
        query = query.where(AnalyticsEvent.session_id == session_id)
    if start_date:
        query = query.where(AnalyticsEvent.created_at >= start_date)
    if end_date:
        query = query.where(AnalyticsEvent.created_at <= end_date)

    # Order by most recent first
    query = query.order_by(AnalyticsEvent.created_at.desc())

    # Pagination
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return result.scalars().all()


async def get_event_stats(
    db: AsyncSession,
    user_id: Optional[str] = None,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get aggregated statistics for events

    Args:
        db: Database session
        user_id: Filter by user ID (optional)
        days: Number of days to look back (default: 30)

    Returns:
        Dict with event statistics
    """
    start_date = datetime.utcnow() - timedelta(days=days)

    # Base query
    query = select(
        AnalyticsEvent.event_type,
        func.count(AnalyticsEvent.id).label('count')
    ).where(AnalyticsEvent.created_at >= start_date)

    if user_id:
        query = query.where(AnalyticsEvent.user_id == user_id)

    query = query.group_by(AnalyticsEvent.event_type)

    result = await db.execute(query)
    rows = result.all()

    # Convert to dict
    event_counts = {row.event_type: row.count for row in rows}

    # Total events
    total_events = sum(event_counts.values())

    return {
        "total_events": total_events,
        "event_counts": event_counts,
        "days": days,
        "start_date": start_date.isoformat(),
        "end_date": datetime.utcnow().isoformat()
    }
