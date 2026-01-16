"""
Workspace and WorkspaceMember Models
"""

import uuid
from datetime import datetime
from typing import Optional
import enum

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class WorkspaceMemberRole(str, enum.Enum):
    """Workspace member role enumeration."""
    OWNER = "owner"      # Full control, can delete workspace
    ADMIN = "admin"      # Can manage members and settings
    MEMBER = "member"    # Can view and edit workspace content
    VIEWER = "viewer"    # Read-only access


class Workspace(Base):
    """Workspace model for team collaboration."""

    __tablename__ = "workspaces"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Owner (creator)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Settings
    is_active = Column(Boolean, default=True)
    settings = Column(JSONB, nullable=True, default=dict)  # Custom workspace settings

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Workspace {self.name}>"


class WorkspaceMember(Base):
    """Workspace member model - links users to workspaces with roles."""

    __tablename__ = "workspace_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Role in this workspace
    role = Column(SQLEnum(WorkspaceMemberRole), default=WorkspaceMemberRole.MEMBER, nullable=False)

    # Invitation metadata
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    invitation_accepted = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_at = Column(DateTime, nullable=True)

    # Relationships
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
    inviter = relationship("User", foreign_keys=[invited_by])

    def __repr__(self):
        return f"<WorkspaceMember workspace={self.workspace_id} user={self.user_id} role={self.role}>"
