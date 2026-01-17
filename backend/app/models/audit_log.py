"""
Audit Log Model - Track sensitive operations
"""

from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid
import json as json_lib

Base = declarative_base()


class AuditLog(Base):
    """
    Audit trail for sensitive operations

    Tracks:
    - User actions (who performed the action)
    - Action types (what was done)
    - Resource details (what was affected)
    - Metadata (IP address, user agent, location, etc.)
    - Timestamps (when it happened)
    """
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # User information
    user_id = Column(String(36), nullable=False, index=True)
    user_email = Column(String(255), nullable=False)

    # Action details
    action_type = Column(String(100), nullable=False, index=True)  # e.g., "report.delete", "report.share", "report.export", "user.delete", "settings.change"
    resource_type = Column(String(50), nullable=False)  # e.g., "report", "user", "project", "workspace"
    resource_id = Column(String(255), nullable=False, index=True)  # ID of the affected resource

    # Action description (human-readable)
    description = Column(Text, nullable=False)

    # Request metadata
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    user_agent = Column(Text, nullable=True)

    # Additional metadata (JSON stored as text for SQLite compatibility)
    _extra_data = Column("extra_data", Text, nullable=True)  # Can store: old_value, new_value, reason, etc.

    @property
    def extra_data(self):
        """Deserialize JSON from text"""
        if self._extra_data:
            return json_lib.loads(self._extra_data)
        return None

    @extra_data.setter
    def extra_data(self, value):
        """Serialize JSON to text"""
        if value is not None:
            self._extra_data = json_lib.dumps(value)
        else:
            self._extra_data = None

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action_type}, user={self.user_email}, resource={self.resource_type}:{self.resource_id})>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "user_email": self.user_email,
            "action_type": self.action_type,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "description": self.description,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None
        }
