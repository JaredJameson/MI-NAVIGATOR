"""
Custom Fields API Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.custom_field import CustomFieldDefinition, CustomFieldValue, FieldType
from app.schemas.custom_field import (
    CustomFieldDefinitionCreate,
    CustomFieldDefinitionUpdate,
    CustomFieldDefinitionResponse,
    CustomFieldValueSet,
    CustomFieldValueResponse,
    CompanyCustomFieldsResponse,
)

router = APIRouter()


@router.get("/definitions", response_model=List[CustomFieldDefinitionResponse])
def get_custom_field_definitions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    include_inactive: bool = False,
):
    """Get all custom field definitions for the current user."""
    query = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.user_id == current_user.id
    )

    if not include_inactive:
        query = query.filter(CustomFieldDefinition.is_active == True)

    definitions = query.order_by(CustomFieldDefinition.display_order).all()
    return definitions


@router.post("/definitions", response_model=CustomFieldDefinitionResponse, status_code=status.HTTP_201_CREATED)
def create_custom_field_definition(
    field_data: CustomFieldDefinitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new custom field definition."""

    # Validate field_type
    valid_types = [ft.value for ft in FieldType]
    if field_data.field_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid field_type. Must be one of: {', '.join(valid_types)}"
        )

    # Validate options for select/multiselect
    if field_data.field_type in ["select", "multiselect"]:
        if not field_data.options or len(field_data.options) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Options are required for select and multiselect fields"
            )

    # Get max display_order
    max_order = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.user_id == current_user.id
    ).count()

    # Create definition
    definition = CustomFieldDefinition(
        user_id=current_user.id,
        name=field_data.name,
        field_type=FieldType(field_data.field_type),
        description=field_data.description,
        is_required=field_data.is_required,
        options=field_data.options,
        display_order=max_order,
    )

    db.add(definition)
    db.commit()
    db.refresh(definition)

    return definition


@router.get("/definitions/{field_id}", response_model=CustomFieldDefinitionResponse)
def get_custom_field_definition(
    field_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific custom field definition."""
    definition = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.id == field_id,
        CustomFieldDefinition.user_id == current_user.id,
    ).first()

    if not definition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom field definition not found"
        )

    return definition


@router.put("/definitions/{field_id}", response_model=CustomFieldDefinitionResponse)
def update_custom_field_definition(
    field_id: UUID,
    field_data: CustomFieldDefinitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a custom field definition."""
    definition = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.id == field_id,
        CustomFieldDefinition.user_id == current_user.id,
    ).first()

    if not definition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom field definition not found"
        )

    # Update fields
    update_data = field_data.dict(exclude_unset=True)

    # Validate field_type if provided
    if "field_type" in update_data:
        valid_types = [ft.value for ft in FieldType]
        if update_data["field_type"] not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid field_type. Must be one of: {', '.join(valid_types)}"
            )

    for key, value in update_data.items():
        setattr(definition, key, value)

    db.commit()
    db.refresh(definition)

    return definition


@router.delete("/definitions/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_custom_field_definition(
    field_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a custom field definition (and all its values)."""
    definition = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.id == field_id,
        CustomFieldDefinition.user_id == current_user.id,
    ).first()

    if not definition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom field definition not found"
        )

    db.delete(definition)
    db.commit()

    return None


@router.post("/values/{company_id}", response_model=CustomFieldValueResponse, status_code=status.HTTP_201_CREATED)
def set_custom_field_value(
    company_id: str,
    value_data: CustomFieldValueSet,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Set a custom field value for a company."""

    # Verify field definition belongs to user
    definition = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.id == value_data.field_definition_id,
        CustomFieldDefinition.user_id == current_user.id,
    ).first()

    if not definition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Custom field definition not found"
        )

    # Check if value already exists
    existing_value = db.query(CustomFieldValue).filter(
        CustomFieldValue.field_definition_id == value_data.field_definition_id,
        CustomFieldValue.company_id == company_id,
    ).first()

    if existing_value:
        # Update existing value
        existing_value.value = value_data.value
        existing_value.value_json = value_data.value_json
        db.commit()
        db.refresh(existing_value)
        return existing_value
    else:
        # Create new value
        new_value = CustomFieldValue(
            field_definition_id=value_data.field_definition_id,
            company_id=company_id,
            value=value_data.value,
            value_json=value_data.value_json,
        )
        db.add(new_value)
        db.commit()
        db.refresh(new_value)
        return new_value


@router.get("/values/{company_id}", response_model=List[CompanyCustomFieldsResponse])
def get_company_custom_fields(
    company_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all custom fields for a company with their values."""

    # Get all active field definitions for user
    definitions = db.query(CustomFieldDefinition).filter(
        CustomFieldDefinition.user_id == current_user.id,
        CustomFieldDefinition.is_active == True,
    ).order_by(CustomFieldDefinition.display_order).all()

    result = []
    for definition in definitions:
        # Get value for this field if it exists
        value = db.query(CustomFieldValue).filter(
            CustomFieldValue.field_definition_id == definition.id,
            CustomFieldValue.company_id == company_id,
        ).first()

        result.append(CompanyCustomFieldsResponse(
            field_definition=definition,
            value=value.value if value else None,
            value_json=value.value_json if value else None,
        ))

    return result
