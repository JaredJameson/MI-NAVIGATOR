"""
Admin Panel Endpoints
Provides admin-only functionality for user management and system statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserRole
from app.db.session import get_db

router = APIRouter()


# Dependency to ensure user is admin
async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that verifies the current user has admin role.
    Raises 403 if user is not an admin.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to access this resource"
        )
    return current_user


# Response Models
class SystemStatsResponse(BaseModel):
    """System-wide statistics for admin dashboard"""
    total_users: int
    active_users: int
    total_reports: int
    total_searches: int
    total_analyses: int


class UserListItem(BaseModel):
    """User item in list view"""
    id: str
    email: str
    name: Optional[str]
    role: str
    is_active: bool
    email_verified: bool
    two_factor_enabled: bool
    created_at: datetime
    last_login_at: Optional[datetime]


class UserDetailResponse(BaseModel):
    """Detailed user information"""
    id: str
    email: str
    name: Optional[str]
    role: str
    is_active: bool
    email_verified: bool
    two_factor_enabled: bool
    industry: Optional[str]
    industry_segment: Optional[str]
    user_role: Optional[str]
    preferred_language: str
    timezone: str
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]


class UpdateUserRoleRequest(BaseModel):
    """Request to update user role"""
    role: UserRole


class UpdateUserStatusRequest(BaseModel):
    """Request to update user active status"""
    is_active: bool


# Admin Endpoints

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Get system-wide statistics.

    Returns:
        - Total number of users
        - Number of active users
        - Total reports created
        - Total searches performed
        - Total analyses completed

    **Requires admin role**
    """
    # Count total users
    total_users_result = await db.execute(select(func.count()).select_from(User))
    total_users = total_users_result.scalar() or 0

    # Count active users
    active_users_result = await db.execute(
        select(func.count()).select_from(User).filter(User.is_active == True)
    )
    active_users = active_users_result.scalar() or 0

    # For now, return placeholder values for reports/searches/analyses
    # In a real implementation, these would query their respective tables
    total_reports = 0
    total_searches = 0
    total_analyses = 0

    return SystemStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_reports=total_reports,
        total_searches=total_searches,
        total_analyses=total_analyses
    )


@router.get("/users", response_model=List[UserListItem])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    List all users with pagination.

    Query Parameters:
        - skip: Number of users to skip (default: 0)
        - limit: Maximum number of users to return (default: 100, max: 1000)

    **Requires admin role**
    """
    # Limit validation
    if limit > 1000:
        limit = 1000

    # Query users
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()

    return [
        UserListItem(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role.value,
            is_active=user.is_active,
            email_verified=user.email_verified,
            two_factor_enabled=user.two_factor_enabled,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
        for user in users
    ]


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_details(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Get detailed information about a specific user.

    **Requires admin role**
    """
    # Find user
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found"
        )

    return UserDetailResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role.value,
        is_active=user.is_active,
        email_verified=user.email_verified,
        two_factor_enabled=user.two_factor_enabled,
        industry=user.industry,
        industry_segment=user.industry_segment,
        user_role=user.user_role,
        preferred_language=user.preferred_language,
        timezone=user.timezone,
        onboarding_completed=user.onboarding_completed,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at
    )


@router.put("/users/{user_id}/role", response_model=UserDetailResponse)
async def update_user_role(
    user_id: str,
    request: UpdateUserRoleRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Update a user's role.

    **Requires admin role**

    Warning: Be careful when changing admin roles. Ensure you don't lock yourself out!
    """
    # Find user
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found"
        )

    # Prevent admin from demoting themselves (safety check)
    if str(admin_user.id) == user_id and request.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote your own admin account. Use another admin account to change this."
        )

    # Update role
    user.role = request.role
    await db.commit()
    await db.refresh(user)

    return UserDetailResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role.value,
        is_active=user.is_active,
        email_verified=user.email_verified,
        two_factor_enabled=user.two_factor_enabled,
        industry=user.industry,
        industry_segment=user.industry_segment,
        user_role=user.user_role,
        preferred_language=user.preferred_language,
        timezone=user.timezone,
        onboarding_completed=user.onboarding_completed,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at
    )


@router.put("/users/{user_id}/status", response_model=UserDetailResponse)
async def update_user_status(
    user_id: str,
    request: UpdateUserStatusRequest,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Enable or disable a user account.

    **Requires admin role**

    Warning: Disabling a user will prevent them from logging in.
    """
    # Find user
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found"
        )

    # Prevent admin from disabling themselves (safety check)
    if str(admin_user.id) == user_id and not request.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disable your own admin account. Use another admin account to do this."
        )

    # Update status
    user.is_active = request.is_active
    await db.commit()
    await db.refresh(user)

    return UserDetailResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role.value,
        is_active=user.is_active,
        email_verified=user.email_verified,
        two_factor_enabled=user.two_factor_enabled,
        industry=user.industry,
        industry_segment=user.industry_segment,
        user_role=user.user_role,
        preferred_language=user.preferred_language,
        timezone=user.timezone,
        onboarding_completed=user.onboarding_completed,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at
    )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """
    Delete a user account permanently.

    **Requires admin role**

    Warning: This action is irreversible. All user data will be permanently deleted.
    """
    # Find user
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id '{user_id}' not found"
        )

    # Prevent admin from deleting themselves (safety check)
    if str(admin_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own admin account. Use another admin account to do this."
        )

    # Delete user (cascade will delete sessions, etc.)
    await db.delete(user)
    await db.commit()

    return {"message": f"User {user.email} has been deleted successfully"}
