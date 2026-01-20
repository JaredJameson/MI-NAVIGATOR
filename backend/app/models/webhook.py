"""
Webhook model for external integrations.

Supports retry mechanism with exponential backoff.
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.db.base import Base


class WebhookEvent(str, enum.Enum):
    """Webhook event types."""
    REPORT_CREATED = "report.created"
    REPORT_UPDATED = "report.updated"
    REPORT_DELETED = "report.deleted"
    ANALYSIS_COMPLETED = "analysis.completed"
    ALERT_TRIGGERED = "alert.triggered"


class WebhookStatus(str, enum.Enum):
    """Webhook delivery status."""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"


class Webhook(Base):
    """
    Webhook configuration and delivery tracking.

    Supports:
    - Multiple event types
    - Retry mechanism with exponential backoff
    - Delivery status tracking
    - Last error logging
    """
    __tablename__ = "webhooks"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)

    # Configuration
    url = Column(String, nullable=False)
    event_type = Column(SQLEnum(WebhookEvent), nullable=False)
    secret = Column(String, nullable=True)  # HMAC secret for signature verification
    is_active = Column(Boolean, default=True, nullable=False)

    # Retry configuration
    max_retries = Column(Integer, default=5, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)

    # Status tracking
    status = Column(SQLEnum(WebhookStatus), default=WebhookStatus.PENDING, nullable=False)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    last_delivered_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Webhook(id={self.id}, url={self.url}, event={self.event_type}, status={self.status})>"
