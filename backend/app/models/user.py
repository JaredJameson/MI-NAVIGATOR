"""
User and Session Models
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """User model for authentication and profile."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    # Role and permissions
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)

    # Profile - from onboarding
    industry = Column(String(100), nullable=True)
    industry_segment = Column(String(100), nullable=True)
    user_role = Column(String(50), nullable=True)  # CEO, Sales, Analyst, etc.

    # Preferences
    preferred_language = Column(String(5), default="pl")
    preferred_depth = Column(String(20), default="standard")  # quick, standard, deep
    preferred_format = Column(String(10), default="pdf")  # pdf, docx, pptx

    # Status
    onboarding_completed = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"


class Session(Base):
    """Session model for JWT refresh tokens."""

    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)

    # Session metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<Session {self.id}>"


class PasswordResetToken(Base):
    """Password reset token model."""

    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<PasswordResetToken {self.id}>"
