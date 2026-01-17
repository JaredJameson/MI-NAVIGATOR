"""
Error log model for tracking frontend and backend errors.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from app.db.base import Base


class ErrorLog(Base):
    """Model for storing application errors."""
    __tablename__ = "error_logs"

    id = Column(String(36), primary_key=True, index=True)

    # Error details
    error_type = Column(String(100), nullable=False)  # JavaScript Error, TypeError, etc.
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)

    # Context
    source = Column(String(20), nullable=False)  # 'frontend' or 'backend'
    url = Column(String(500), nullable=True)  # URL where error occurred
    user_agent = Column(String(500), nullable=True)

    # User context (if logged in)
    user_id = Column(String(36), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)

    # Additional metadata
    error_metadata = Column(JSON, nullable=True)  # Browser info, component stack, etc.

    # Status
    resolved = Column(Boolean, default=False, index=True)

    # Timestamps
    occurred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
