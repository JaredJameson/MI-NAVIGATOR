"""
System Management Endpoints
Handles system-level operations like maintenance mode
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from app.core.config import settings
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

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
