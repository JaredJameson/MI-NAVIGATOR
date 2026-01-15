"""
User API Endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


class UserProfileResponse(BaseModel):
    """User profile response."""
    id: str
    email: str
    name: Optional[str] = None
    industry: Optional[str] = None
    industry_segment: Optional[str] = None
    user_role: Optional[str] = None
    preferred_language: str = "pl"
    preferred_depth: str = "standard"
    preferred_format: str = "pdf"
    onboarding_completed: bool = False

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """User profile update request."""
    name: Optional[str] = None
    industry: Optional[str] = None
    industry_segment: Optional[str] = None
    user_role: Optional[str] = None


class UserPreferencesResponse(BaseModel):
    """User preferences response."""
    preferred_language: str
    preferred_depth: str
    preferred_format: str


class UserPreferencesUpdate(BaseModel):
    """User preferences update request."""
    preferred_language: Optional[str] = None
    preferred_depth: Optional[str] = None
    preferred_format: Optional[str] = None


@router.get("/me", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile."""
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        industry=current_user.industry,
        industry_segment=current_user.industry_segment,
        user_role=current_user.user_role,
        preferred_language=current_user.preferred_language or "pl",
        preferred_depth=current_user.preferred_depth or "standard",
        preferred_format=current_user.preferred_format or "pdf",
        onboarding_completed=current_user.onboarding_completed or False
    )


@router.put("/me", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile."""
    if profile_data.name is not None:
        current_user.name = profile_data.name
    if profile_data.industry is not None:
        current_user.industry = profile_data.industry
    if profile_data.industry_segment is not None:
        current_user.industry_segment = profile_data.industry_segment
    if profile_data.user_role is not None:
        current_user.user_role = profile_data.user_role

    await db.commit()
    await db.refresh(current_user)

    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        industry=current_user.industry,
        industry_segment=current_user.industry_segment,
        user_role=current_user.user_role,
        preferred_language=current_user.preferred_language or "pl",
        preferred_depth=current_user.preferred_depth or "standard",
        preferred_format=current_user.preferred_format or "pdf",
        onboarding_completed=current_user.onboarding_completed or False
    )


@router.get("/me/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: User = Depends(get_current_user)
):
    """Get user preferences."""
    return UserPreferencesResponse(
        preferred_language=current_user.preferred_language or "pl",
        preferred_depth=current_user.preferred_depth or "standard",
        preferred_format=current_user.preferred_format or "pdf"
    )


@router.put("/me/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(
    prefs_data: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user preferences."""
    if prefs_data.preferred_language is not None:
        current_user.preferred_language = prefs_data.preferred_language
    if prefs_data.preferred_depth is not None:
        current_user.preferred_depth = prefs_data.preferred_depth
    if prefs_data.preferred_format is not None:
        current_user.preferred_format = prefs_data.preferred_format

    await db.commit()
    await db.refresh(current_user)

    return UserPreferencesResponse(
        preferred_language=current_user.preferred_language or "pl",
        preferred_depth=current_user.preferred_depth or "standard",
        preferred_format=current_user.preferred_format or "pdf"
    )
