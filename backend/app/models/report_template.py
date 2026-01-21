"""
Report Template Model
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import json

from app.db.base import Base


class ReportTemplate(Base):
    """Report template model for saving reusable report structures."""

    __tablename__ = "report_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)  # company_profile, market_analysis, etc.

    # User who created the template
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Template structure (stored as JSON text for SQLite compatibility)
    sections = Column(Text, nullable=False, default='[]')

    # Metadata
    use_count = Column(Integer, default=0, nullable=False)
    last_used = Column(DateTime, nullable=True)

    # Original report reference (optional)
    original_report_id = Column(String(100), nullable=True)
    original_report_title = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User", backref="report_templates")
