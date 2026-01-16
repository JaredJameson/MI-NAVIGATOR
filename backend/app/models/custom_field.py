"""
Custom Field Models
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class FieldType(str, enum.Enum):
    """Custom field type enumeration."""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    MULTISELECT = "multiselect"
    URL = "url"
    EMAIL = "email"


class CustomFieldDefinition(Base):
    """Custom field definition model - defines available custom fields."""

    __tablename__ = "custom_field_definitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Field properties
    name = Column(String(100), nullable=False)
    field_type = Column(SQLEnum(FieldType), nullable=False)
    description = Column(Text, nullable=True)
    is_required = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # For select/multiselect types
    options = Column(JSONB, nullable=True)  # List of options: ["Option 1", "Option 2"]

    # Display order
    display_order = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")

    def __repr__(self):
        return f"<CustomFieldDefinition {self.name} ({self.field_type})>"


class CustomFieldValue(Base):
    """Custom field value model - stores actual values for companies."""

    __tablename__ = "custom_field_values"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_definition_id = Column(UUID(as_uuid=True), ForeignKey("custom_field_definitions.id", ondelete="CASCADE"), nullable=False)

    # Company identification (using company ID from FADO mock data)
    company_id = Column(String(100), nullable=False, index=True)

    # Value storage
    value = Column(Text, nullable=True)  # For text, number, date, url, email, single select
    value_json = Column(JSONB, nullable=True)  # For multiselect - array of selected options

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    field_definition = relationship("CustomFieldDefinition")

    def __repr__(self):
        return f"<CustomFieldValue {self.field_definition_id} for company {self.company_id}>"
