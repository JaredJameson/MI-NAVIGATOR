"""
Analytics Event Model
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class EventType(str, enum.Enum):
    """Analytics event type enumeration."""
    # Authentication events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_SIGNUP = "user_signup"

    # Research events
    RESEARCH_STARTED = "research_started"
    RESEARCH_COMPLETED = "research_completed"

    # Analysis events
    ANALYSIS_COMPLETED = "analysis_completed"

    # Report events
    REPORT_CREATED = "report_created"
    REPORT_VIEWED = "report_viewed"
    REPORT_EXPORTED = "report_exported"

    # Search events
    SEARCH_PERFORMED = "search_performed"
    PKD_SEARCH = "pkd_search"

    # Company events
    COMPANY_ANALYZED = "company_analyzed"
    COMPETITOR_MAPPED = "competitor_mapped"

    # Chat events
    CHAT_MESSAGE_SENT = "chat_message_sent"

    # Other
    PAGE_VIEW = "page_view"
    ERROR_OCCURRED = "error_occurred"


class AnalyticsEvent(Base):
    """Analytics event model for tracking user actions."""

    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Event info
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    event_name = Column(String(100), nullable=False)  # Human-readable event name

    # User info (nullable for anonymous events)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Session info
    session_id = Column(String(100), nullable=True, index=True)

    # Event metadata (NO PII!)
    # Examples: {"research_type": "company_profile", "export_format": "pdf", "page_path": "/dashboard"}
    event_metadata = Column(JSONB, nullable=True)

    # Context
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    user_agent = Column(Text, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", backref="analytics_events")

    def __repr__(self):
        return f"<AnalyticsEvent {self.event_type} - {self.event_name}>"
