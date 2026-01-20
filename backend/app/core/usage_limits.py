"""
Usage Limit Enforcement

This module provides utilities to enforce usage limits for users based on their role.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.analytics_event import AnalyticsEvent, EventType


async def check_usage_limit(
    db: AsyncSession,
    user: User,
    action_type: str = "analysis"
) -> None:
    """
    Check if user has exceeded their usage limit for the specified action.

    Raises HTTPException(403) if limit is exceeded.

    Args:
        db: Database session
        user: Current user
        action_type: Type of action being performed (e.g., "analysis", "chat", "research")

    Raises:
        HTTPException: 403 Forbidden if usage limit exceeded
    """
    # Get start of current month
    now = datetime.utcnow()
    start_date = datetime(now.year, now.month, 1)

    # Count user's analyses this month
    result = await db.execute(
        select(func.count(AnalyticsEvent.id))
        .where(
            and_(
                AnalyticsEvent.user_id == str(user.id),
                AnalyticsEvent.event_type.in_([
                    EventType.CHAT_MESSAGE_SENT,
                    EventType.RESEARCH_STARTED,
                    EventType.ANALYSIS_COMPLETED
                ]),
                AnalyticsEvent.created_at >= start_date
            )
        )
    )
    current_usage = result.scalar() or 0

    # Determine limit based on role
    if user.role == UserRole.ADMIN:
        limit = 1000
    else:
        limit = 100  # Standard limit for regular users

    # Check if limit exceeded
    if current_usage >= limit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "usage_limit_exceeded",
                "message": f"You have reached your monthly limit of {limit} analyses. Please upgrade your plan or wait until next month.",
                "current_usage": current_usage,
                "limit": limit,
                "reset_date": datetime(now.year, now.month + 1 if now.month < 12 else 1, 1).isoformat()
            }
        )


async def get_usage_stats(
    db: AsyncSession,
    user_id: str
) -> dict:
    """
    Get current usage statistics for a user.

    Returns:
        dict with usage counts and limits
    """
    now = datetime.utcnow()
    start_date = datetime(now.year, now.month, 1)

    result = await db.execute(
        select(func.count(AnalyticsEvent.id))
        .where(
            and_(
                AnalyticsEvent.user_id == user_id,
                AnalyticsEvent.event_type.in_([
                    EventType.CHAT_MESSAGE_SENT,
                    EventType.RESEARCH_STARTED,
                    EventType.ANALYSIS_COMPLETED
                ]),
                AnalyticsEvent.created_at >= start_date
            )
        )
    )
    current_usage = result.scalar() or 0

    return {
        "current_usage": current_usage,
        "limit": 1000,  # Will be set properly based on user role
        "period": "monthly",
        "reset_date": datetime(now.year, now.month + 1 if now.month < 12 else 1, 1).isoformat()
    }
