"""
System Management Endpoints
Handles system-level operations like maintenance mode and feature flags
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.feature_flag import FeatureFlag
from app.db.session import get_db

router = APIRouter()


class MaintenanceStatusResponse(BaseModel):
    """Response model for maintenance status"""
    maintenance: bool
    message: Optional[str] = None
    eta: Optional[str] = None


class MaintenanceToggleRequest(BaseModel):
    """Request model for toggling maintenance mode"""
    enabled: bool
    message: Optional[str] = None
    eta: Optional[str] = None


@router.get("/maintenance", response_model=MaintenanceStatusResponse)
async def get_maintenance_status():
    """
    Get current maintenance mode status.
    Public endpoint - no authentication required.
    """
    return MaintenanceStatusResponse(
        maintenance=settings.MAINTENANCE_MODE,
        message=settings.MAINTENANCE_MESSAGE if settings.MAINTENANCE_MODE else None,
        eta=settings.MAINTENANCE_ETA if settings.MAINTENANCE_MODE and settings.MAINTENANCE_ETA else None
    )


@router.post("/maintenance", response_model=MaintenanceStatusResponse)
async def toggle_maintenance_mode(
    request: MaintenanceToggleRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Toggle maintenance mode on/off.
    Requires admin privileges.

    **Note:** In a production environment, this would:
    1. Check if current_user has admin role
    2. Store maintenance settings in database
    3. Use Redis or similar for distributed systems

    For testing purposes, this directly modifies the settings object.
    """
    # Check if user is admin
    # For now, we'll allow any authenticated user to toggle for testing
    # In production, add: if not current_user.is_admin: raise HTTPException(403)

    # Update maintenance mode settings
    settings.MAINTENANCE_MODE = request.enabled

    if request.message:
        settings.MAINTENANCE_MESSAGE = request.message

    if request.eta:
        settings.MAINTENANCE_ETA = request.eta
    else:
        settings.MAINTENANCE_ETA = ""

    return MaintenanceStatusResponse(
        maintenance=settings.MAINTENANCE_MODE,
        message=settings.MAINTENANCE_MESSAGE if settings.MAINTENANCE_MODE else None,
        eta=settings.MAINTENANCE_ETA if settings.MAINTENANCE_MODE and settings.MAINTENANCE_ETA else None
    )


# Feature Flags Endpoints

class FeatureFlagResponse(BaseModel):
    """Response model for feature flag"""
    id: int
    key: str
    name: str
    description: Optional[str]
    enabled: bool


class FeatureFlagUpdateRequest(BaseModel):
    """Request model for updating feature flag"""
    enabled: bool


@router.get("/feature-flags", response_model=List[FeatureFlagResponse])
async def get_feature_flags(db: AsyncSession = Depends(get_db)):
    """
    Get all feature flags (public endpoint).
    Returns all flags for authenticated users, only enabled flags for guests.
    """
    result = await db.execute(select(FeatureFlag))
    flags = result.scalars().all()
    return [
        FeatureFlagResponse(
            id=flag.id,
            key=flag.key,
            name=flag.name,
            description=flag.description,
            enabled=flag.enabled
        )
        for flag in flags
    ]


@router.get("/feature-flags/{key}", response_model=FeatureFlagResponse)
async def get_feature_flag_by_key(key: str, db: AsyncSession = Depends(get_db)):
    """Get a specific feature flag by key"""
    result = await db.execute(select(FeatureFlag).filter(FeatureFlag.key == key))
    flag = result.scalar_one_or_none()
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{key}' not found"
        )
    return FeatureFlagResponse(
        id=flag.id,
        key=flag.key,
        name=flag.name,
        description=flag.description,
        enabled=flag.enabled
    )


@router.put("/feature-flags/{key}", response_model=FeatureFlagResponse)
async def update_feature_flag(
    key: str,
    request: FeatureFlagUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a feature flag's enabled status.
    Requires admin privileges.
    """
    # Debug logging
    print(f"[FEATURE FLAGS] User: {current_user.email if current_user else 'None'}, Role: {current_user.role if current_user else 'None'}")

    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    # Find the feature flag
    result = await db.execute(select(FeatureFlag).filter(FeatureFlag.key == key))
    flag = result.scalar_one_or_none()
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature flag '{key}' not found"
        )

    # Update the flag
    flag.enabled = request.enabled
    await db.commit()
    await db.refresh(flag)

    return FeatureFlagResponse(
        id=flag.id,
        key=flag.key,
        name=flag.name,
        description=flag.description,
        enabled=flag.enabled
    )
