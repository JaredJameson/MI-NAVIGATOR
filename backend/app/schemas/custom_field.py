"""
Custom Field Schemas
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class FieldTypeEnum(str):
    """Field type options"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    MULTISELECT = "multiselect"
    URL = "url"
    EMAIL = "email"


class CustomFieldDefinitionCreate(BaseModel):
    """Schema for creating a custom field definition."""
    name: str = Field(..., min_length=1, max_length=100, description="Field name")
    field_type: str = Field(..., description="Field type (text, number, date, select, multiselect, url, email)")
    description: Optional[str] = Field(None, description="Field description")
    is_required: bool = Field(False, description="Whether this field is required")
    options: Optional[List[str]] = Field(None, description="Options for select/multiselect fields")


class CustomFieldDefinitionUpdate(BaseModel):
    """Schema for updating a custom field definition."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    field_type: Optional[str] = None
    description: Optional[str] = None
    is_required: Optional[bool] = None
    is_active: Optional[bool] = None
    options: Optional[List[str]] = None
    display_order: Optional[int] = None


class CustomFieldDefinitionResponse(BaseModel):
    """Schema for custom field definition response."""
    id: UUID
    user_id: UUID
    name: str
    field_type: str
    description: Optional[str]
    is_required: bool
    is_active: bool
    options: Optional[List[str]]
    display_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomFieldValueSet(BaseModel):
    """Schema for setting a custom field value."""
    field_definition_id: UUID
    value: Optional[str] = None  # For text, number, date, url, email, single select
    value_json: Optional[List[str]] = None  # For multiselect


class CustomFieldValueResponse(BaseModel):
    """Schema for custom field value response."""
    id: UUID
    field_definition_id: UUID
    company_id: str
    value: Optional[str]
    value_json: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyCustomFieldsResponse(BaseModel):
    """Schema for company custom fields response with definitions and values."""
    field_definition: CustomFieldDefinitionResponse
    value: Optional[str]
    value_json: Optional[List[str]]
