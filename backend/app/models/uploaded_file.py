"""
Uploaded File Model
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class UploadedFile(Base):
    """Uploaded file model for storing file metadata and extracted content."""

    __tablename__ = "uploaded_files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # File information
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Relative path in storage
    file_type = Column(String(50), nullable=False)  # MIME type
    file_size = Column(Integer, nullable=False)  # Size in bytes

    # Extracted content
    extracted_content = Column(Text, nullable=True)  # Text extracted from file

    # File metadata
    file_metadata = Column(JSON, nullable=True)  # Additional file metadata (pages, dimensions, etc.)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Optional: link to conversation
    conversation_id = Column(String(255), nullable=True, index=True)
