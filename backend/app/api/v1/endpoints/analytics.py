"""
Analytics Endpoints
Handles analytics event tracking and viewing
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserRole
from app.models.analytics_event import AnalyticsEvent, EventType
from app.db.session import get_db
from app.services.analytics_service import get_events, get_event_stats

router = APIRouter()


class EventResponse(BaseModel):
    """Response model for analytics event"""
    id: str
    event_type: str
    event_name: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, event: AnalyticsEvent):
        """Convert AnalyticsEvent to EventResponse"""
        return cls(
            id=str(event.id),
            event_type=event.event_type.value if isinstance(event.event_type, EventType) else event.event_type,
            event_name=event.event_name,
            user_id=event.user_id,
            session_id=event.session_id,
            metadata=json.loads(event.event_metadata) if event.event_metadata else None,
            created_at=event.created_at
        )


class EventStatsResponse(BaseModel):
    """Response model for event statistics"""
    total_events: int
    event_counts: Dict[str, int]
    days: int
    start_date: str
    end_date: str


@router.get("/events", response_model=List[EventResponse])
async def list_analytics_events(
    event_type: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List analytics events for the current user.

    Users can only see their own events.
    Admins can see all events if user_id is not provided.
    """
    # Regular users can only see their own events
    user_id_filter = str(current_user.id)

    # Admins can see all events if they want (by not providing user_id)
    # For this implementation, we'll keep it simple and show only current user's events

    # Convert event_type string to enum if provided
    event_type_enum = None
    if event_type:
        try:
            event_type_enum = EventType(event_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event_type: {event_type}"
            )

    events = await get_events(
        db=db,
        user_id=user_id_filter,
        event_type=event_type_enum,
        session_id=session_id,
        limit=limit,
        offset=offset
    )

    return [EventResponse.from_orm(event) for event in events]


@router.get("/stats", response_model=EventStatsResponse)
async def get_analytics_stats(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get aggregated analytics statistics for the current user.

    Args:
        days: Number of days to look back (default: 30)
    """
    if days < 1 or days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days must be between 1 and 365"
        )

    stats = await get_event_stats(
        db=db,
        user_id=str(current_user.id),
        days=days
    )

    return EventStatsResponse(**stats)


@router.get("/admin/events", response_model=List[EventResponse])
async def list_all_analytics_events(
    user_id: Optional[str] = None,
    event_type: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all analytics events (admin only).

    Admins can filter by user_id, event_type, and session_id.
    """
    # Check if user is admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view all analytics events"
        )

    # Convert event_type string to enum if provided
    event_type_enum = None
    if event_type:
        try:
            event_type_enum = EventType(event_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event_type: {event_type}"
            )

    events = await get_events(
        db=db,
        user_id=user_id,
        event_type=event_type_enum,
        session_id=session_id,
        limit=limit,
        offset=offset
    )

    return [EventResponse.from_orm(event) for event in events]


@router.get("/admin/stats", response_model=EventStatsResponse)
async def get_all_analytics_stats(
    user_id: Optional[str] = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get aggregated analytics statistics for all users or specific user (admin only).

    Args:
        user_id: Optional user ID to filter by
        days: Number of days to look back (default: 30)
    """
    # Check if user is admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can view analytics statistics"
        )

    if days < 1 or days > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days must be between 1 and 365"
        )

    stats = await get_event_stats(
        db=db,
        user_id=user_id,
        days=days
    )

    return EventStatsResponse(**stats)
