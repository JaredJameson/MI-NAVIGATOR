"""
API Key Model for programmatic access
"""

import uuid
import secrets
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class APIKey(Base):
    """API Key model for programmatic API access."""

    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # The actual API key (hashed for security)
    key_hash = Column(String(255), nullable=False, unique=True, index=True)

    # Key prefix (first 8 chars) - shown to user for identification
    key_prefix = Column(String(16), nullable=False)

    # Optional name/description for the key
    name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration

    # Relationships
    user = relationship("User", back_populates="api_keys")

    @staticmethod
    def generate_key() -> str:
        """Generate a secure random API key."""
        # Generate a 32-character random key
        return f"mi_nav_{secrets.token_urlsafe(32)}"

    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key for storage using SHA-256."""
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()

    @staticmethod
    def verify_key(plain_key: str, hashed_key: str) -> bool:
        """Verify an API key against its hash."""
        import hashlib
        return hashlib.sha256(plain_key.encode()).hexdigest() == hashed_key
