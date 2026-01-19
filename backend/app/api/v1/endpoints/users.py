"""
User API Endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import json
from datetime import datetime

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User, UserRole
from app.models.audit_log import AuditLog
from app.models.report_template import ReportTemplate
from app.services.auth import AuthService
from app.services.audit_service import log_audit

router = APIRouter()


class UserProfileResponse(BaseModel):
    """User profile response."""
    id: str
    email: str
    name: Optional[str] = None
    role: str = "user"  # User role: guest, user, admin
    industry: Optional[str] = None
    industry_segment: Optional[str] = None
    user_role: Optional[str] = None
    use_cases: Optional[list[str]] = None
    preferred_language: str = "pl"
    preferred_depth: str = "standard"
    preferred_format: str = "pdf"
    preferred_currency: str = "PLN"
    timezone: str = "Europe/Warsaw"
    onboarding_completed: bool = False
    created_at: datetime
    last_login_at: Optional[datetime] = None

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
    preferred_currency: str
    timezone: str


class UserPreferencesUpdate(BaseModel):
    """User preferences update request."""
    preferred_language: Optional[str] = None
    preferred_depth: Optional[str] = None
    preferred_format: Optional[str] = None
    preferred_currency: Optional[str] = None
    timezone: Optional[str] = None


class NotificationPreferencesResponse(BaseModel):
    """Notification preferences response."""
    email_notifications: bool = True
    in_app_notifications: bool = True
    email_report_ready: bool = True
    email_alert_triggered: bool = True
    email_weekly_digest: bool = False
    in_app_report_ready: bool = True
    in_app_alert_triggered: bool = True
    in_app_project_updates: bool = True


class NotificationPreferencesUpdate(BaseModel):
    """Notification preferences update request."""
    email_notifications: Optional[bool] = None
    in_app_notifications: Optional[bool] = None
    email_report_ready: Optional[bool] = None
    email_alert_triggered: Optional[bool] = None
    email_weekly_digest: Optional[bool] = None
    in_app_report_ready: Optional[bool] = None
    in_app_alert_triggered: Optional[bool] = None
    in_app_project_updates: Optional[bool] = None


class PasswordChangeRequest(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str
    refresh_token: str  # Current session's refresh token to preserve


class PasswordChangeResponse(BaseModel):
    """Password change response."""
    message: str
    sessions_invalidated: int


class AccountDeletionRequest(BaseModel):
    """Account deletion request."""
    password: str
    confirmation_text: str  # User must type "DELETE" to confirm


class AccountDeletionResponse(BaseModel):
    """Account deletion response."""
    message: str
    deleted_at: str


# In-memory storage for notification preferences (mock)
NOTIFICATION_PREFS: dict = {}


@router.get("/me", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile."""
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        industry=current_user.industry,
        industry_segment=current_user.industry_segment,
        user_role=current_user.user_role,
        preferred_language=current_user.preferred_language or "pl",
        preferred_depth=current_user.preferred_depth or "standard",
        preferred_format=current_user.preferred_format or "pdf",
        preferred_currency=current_user.preferred_currency or "PLN",
        timezone=current_user.timezone or "Europe/Warsaw",
        onboarding_completed=current_user.onboarding_completed or False,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
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
        role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        industry=current_user.industry,
        industry_segment=current_user.industry_segment,
        user_role=current_user.user_role,
        preferred_language=current_user.preferred_language or "pl",
        preferred_depth=current_user.preferred_depth or "standard",
        preferred_format=current_user.preferred_format or "pdf",
        preferred_currency=current_user.preferred_currency or "PLN",
        timezone=current_user.timezone or "Europe/Warsaw",
        onboarding_completed=current_user.onboarding_completed or False,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at
    )


@router.get("/me/preferences", response_model=UserPreferencesResponse)
async def get_user_preferences(
    current_user: User = Depends(get_current_user)
):
    """Get user preferences."""
    return UserPreferencesResponse(
        preferred_language=current_user.preferred_language or "pl",
        preferred_depth=current_user.preferred_depth or "standard",
        preferred_format=current_user.preferred_format or "pdf",
        preferred_currency=current_user.preferred_currency or "PLN",
        timezone=current_user.timezone or "Europe/Warsaw"
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
    if prefs_data.preferred_currency is not None:
        current_user.preferred_currency = prefs_data.preferred_currency
    if prefs_data.timezone is not None:
        current_user.timezone = prefs_data.timezone

    await db.commit()
    await db.refresh(current_user)

    return UserPreferencesResponse(
        preferred_language=current_user.preferred_language or "pl",
        preferred_depth=current_user.preferred_depth or "standard",
        preferred_format=current_user.preferred_format or "pdf",
        preferred_currency=current_user.preferred_currency or "PLN",
        timezone=current_user.timezone or "Europe/Warsaw"
    )


@router.get("/me/notifications", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(
    current_user: User = Depends(get_current_user)
):
    """Get notification preferences."""
    user_id = str(current_user.id)
    if user_id in NOTIFICATION_PREFS:
        return NotificationPreferencesResponse(**NOTIFICATION_PREFS[user_id])
    return NotificationPreferencesResponse()


@router.put("/me/notifications", response_model=NotificationPreferencesResponse)
async def update_notification_preferences(
    prefs_data: NotificationPreferencesUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update notification preferences."""
    user_id = str(current_user.id)

    # Get existing or default preferences
    if user_id not in NOTIFICATION_PREFS:
        NOTIFICATION_PREFS[user_id] = NotificationPreferencesResponse().model_dump()

    # Update only provided fields
    if prefs_data.email_notifications is not None:
        NOTIFICATION_PREFS[user_id]["email_notifications"] = prefs_data.email_notifications
    if prefs_data.in_app_notifications is not None:
        NOTIFICATION_PREFS[user_id]["in_app_notifications"] = prefs_data.in_app_notifications
    if prefs_data.email_report_ready is not None:
        NOTIFICATION_PREFS[user_id]["email_report_ready"] = prefs_data.email_report_ready
    if prefs_data.email_alert_triggered is not None:
        NOTIFICATION_PREFS[user_id]["email_alert_triggered"] = prefs_data.email_alert_triggered
    if prefs_data.email_weekly_digest is not None:
        NOTIFICATION_PREFS[user_id]["email_weekly_digest"] = prefs_data.email_weekly_digest
    if prefs_data.in_app_report_ready is not None:
        NOTIFICATION_PREFS[user_id]["in_app_report_ready"] = prefs_data.in_app_report_ready
    if prefs_data.in_app_alert_triggered is not None:
        NOTIFICATION_PREFS[user_id]["in_app_alert_triggered"] = prefs_data.in_app_alert_triggered
    if prefs_data.in_app_project_updates is not None:
        NOTIFICATION_PREFS[user_id]["in_app_project_updates"] = prefs_data.in_app_project_updates

    return NotificationPreferencesResponse(**NOTIFICATION_PREFS[user_id])


@router.put("/me/password", response_model=PasswordChangeResponse)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request_obj: Request = None
):
    """
    Change user password and invalidate all other sessions.

    This endpoint:
    1. Verifies the current password
    2. Updates to the new password
    3. Invalidates all sessions EXCEPT the current one (identified by refresh_token)
    4. Logs the password change

    Args:
        password_data: Current password, new password, and current refresh token
        current_user: Authenticated user
        db: Database session
        request_obj: HTTP request for audit logging

    Returns:
        PasswordChangeResponse with number of sessions invalidated

    Raises:
        HTTPException: If current password is incorrect or new password is invalid
    """
    # Verify current password
    if not AuthService.verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Validate new password (minimum 6 characters)
    if len(password_data.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long"
        )

    # Hash new password
    new_password_hash = AuthService.hash_password(password_data.new_password)

    # Update password
    current_user.password_hash = new_password_hash
    current_user.updated_at = datetime.utcnow()

    # Invalidate all other sessions (keep current session active)
    sessions_deleted = await AuthService.delete_other_user_sessions(
        db,
        current_user.id,
        password_data.refresh_token
    )

    await db.commit()

    # Log password change
    if request_obj:
        await log_audit(
            db=db,
            user=current_user,
            action_type="password_changed",
            resource_type="user",
            resource_id=str(current_user.id),
            description=f"Password changed for user '{current_user.email}'. {sessions_deleted} other session(s) invalidated.",
            request=request_obj,
            extra_data={"sessions_invalidated": sessions_deleted}
        )

    return PasswordChangeResponse(
        message="Password changed successfully. Other sessions have been invalidated.",
        sessions_invalidated=sessions_deleted
    )


@router.post("/me/export-data")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export all user data for GDPR compliance.
    Returns a JSON file with all user information.
    """
    # Fetch user's audit logs
    audit_stmt = select(AuditLog).where(AuditLog.user_id == current_user.id).order_by(AuditLog.created_at.desc())
    audit_result = await db.execute(audit_stmt)
    audit_logs = audit_result.scalars().all()

    # Build comprehensive data export
    export_data = {
        "user_profile": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name,
            "avatar_url": current_user.avatar_url,
            "role": current_user.role.value if current_user.role else None,
            "industry": current_user.industry,
            "industry_segment": current_user.industry_segment,
            "user_role": current_user.user_role,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
            "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
        },
        "preferences": {
            "preferred_language": current_user.preferred_language,
            "preferred_depth": current_user.preferred_depth,
            "preferred_format": current_user.preferred_format,
            "onboarding_completed": current_user.onboarding_completed,
            "email_verified": current_user.email_verified,
        },
        "security": {
            "two_factor_enabled": current_user.two_factor_enabled,
            "account_locked": current_user.account_locked_until.isoformat() if current_user.account_locked_until else None,
        },
        "activity_log": [
            {
                "action": log.action,
                "description": log.description,
                "ip_address": log.ip_address,
                "timestamp": log.created_at.isoformat() if log.created_at else None,
                "extra_data": log.extra_data,
            }
            for log in audit_logs
        ],
        "export_metadata": {
            "exported_at": datetime.utcnow().isoformat(),
            "export_format": "JSON",
            "data_version": "1.0",
        }
    }

    # Return as JSON download
    json_content = json.dumps(export_data, indent=2, ensure_ascii=False)
    filename = f"user_data_export_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

    return Response(
        content=json_content,
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.delete("/me", response_model=AccountDeletionResponse)
async def delete_user_account(
    deletion_request: AccountDeletionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    request_obj: Request = None
):
    """
    Delete user account and all associated data (GDPR compliance).

    This is a permanent action that:
    1. Verifies the user's password
    2. Checks confirmation text is "DELETE"
    3. Deletes all user data (audit logs, templates, etc.)
    4. Deletes the user account

    Args:
        deletion_request: Password and confirmation text
        current_user: Authenticated user
        db: Database session
        request_obj: HTTP request for audit logging

    Returns:
        AccountDeletionResponse with deletion timestamp

    Raises:
        HTTPException: If password is incorrect or confirmation text is wrong
    """
    # Verify password
    if not AuthService.verify_password(deletion_request.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    # Verify confirmation text
    if deletion_request.confirmation_text != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation text must be 'DELETE'"
        )

    user_id = current_user.id
    user_email = current_user.email
    deletion_time = datetime.utcnow()

    # Log account deletion before deleting
    if request_obj:
        await log_audit(
            db=db,
            user=current_user,
            action_type="account_deleted",
            resource_type="user",
            resource_id=str(user_id),
            description=f"User account '{user_email}' permanently deleted",
            request=request_obj,
            extra_data={"email": user_email, "deleted_at": deletion_time.isoformat()}
        )

    # Delete all related data
    # 1. Delete audit logs
    await db.execute(delete(AuditLog).where(AuditLog.user_id == user_id))

    # 2. Delete report templates
    await db.execute(delete(ReportTemplate).where(ReportTemplate.created_by == user_id))

    # 3. Delete user account
    await db.delete(current_user)

    # Commit all deletions
    await db.commit()

    return AccountDeletionResponse(
        message=f"Account {user_email} and all associated data have been permanently deleted",
        deleted_at=deletion_time.isoformat()
    )


class UserUsageStatsResponse(BaseModel):
    """User usage statistics response."""
    analyses_count: int
    analyses_limit: int
    analyses_percentage: float
    storage_used_bytes: int
    storage_limit_bytes: int
    storage_used_gb: float
    storage_limit_gb: float
    storage_percentage: float
    api_calls_count: int
    reports_count: int
    projects_count: int
    period: str  # e.g., "month", "all_time"


@router.get("/usage", response_model=UserUsageStatsResponse)
async def get_user_usage_stats(
    period: str = "month",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's usage statistics.

    Args:
        period: "month" for current month, "all_time" for all time stats

    Returns:
        Usage statistics including analyses count, storage, API calls
    """
    from datetime import datetime
    from sqlalchemy import func, and_
    from app.models.analytics_event import AnalyticsEvent

    user_id = current_user.id

    # Calculate date range based on period
    if period == "month":
        # Current month
        now = datetime.utcnow()
        start_date = datetime(now.year, now.month, 1)
    else:
        # All time
        start_date = datetime(2020, 1, 1)  # Arbitrary old date

    # Count analyses based on analytics events
    # Count events of type 'analysis', 'search', 'chat' as analyses
    analyses_result = await db.execute(
        select(func.count(AnalyticsEvent.id))
        .where(
            and_(
                AnalyticsEvent.user_id == str(user_id),
                AnalyticsEvent.created_at >= start_date,
                AnalyticsEvent.event_type.in_(['analysis', 'search', 'chat'])
            )
        )
    )
    analyses_count = analyses_result.scalar() or 0

    # Count API calls (all analytics events in period)
    api_calls_result = await db.execute(
        select(func.count(AnalyticsEvent.id))
        .where(
            and_(
                AnalyticsEvent.user_id == str(user_id),
                AnalyticsEvent.created_at >= start_date
            )
        )
    )
    api_calls_count = api_calls_result.scalar() or 0

    # For now, set reports and projects count to 0 (models not implemented yet)
    reports_count = 0
    projects_count = 0
    storage_used_bytes = 0

    # Set limits based on user role
    if current_user.role == UserRole.ADMIN:
        analyses_limit = 1000
        storage_limit_bytes = 100 * 1024 * 1024 * 1024  # 100 GB
    else:
        analyses_limit = 100
        storage_limit_bytes = 10 * 1024 * 1024 * 1024  # 10 GB

    # Calculate percentages
    analyses_percentage = (analyses_count / analyses_limit * 100) if analyses_limit > 0 else 0
    storage_percentage = (storage_used_bytes / storage_limit_bytes * 100) if storage_limit_bytes > 0 else 0

    # Convert bytes to GB
    storage_used_gb = storage_used_bytes / (1024 * 1024 * 1024)
    storage_limit_gb = storage_limit_bytes / (1024 * 1024 * 1024)

    return UserUsageStatsResponse(
        analyses_count=analyses_count,
        analyses_limit=analyses_limit,
        analyses_percentage=round(analyses_percentage, 1),
        storage_used_bytes=storage_used_bytes,
        storage_limit_bytes=storage_limit_bytes,
        storage_used_gb=round(storage_used_gb, 2),
        storage_limit_gb=round(storage_limit_gb, 0),
        storage_percentage=round(storage_percentage, 1),
        api_calls_count=api_calls_count,
        reports_count=reports_count,
        projects_count=projects_count,
        period=period
    )


class OnboardingDataRequest(BaseModel):
    """Onboarding data request."""
    industry: str
    industry_segment: Optional[str] = None
    user_role: str
    use_cases: Optional[list[str]] = None
    preferred_language: Optional[str] = "pl"
    preferred_depth: Optional[str] = "standard"
    preferred_format: Optional[str] = "pdf"


class OnboardingDataResponse(BaseModel):
    """Onboarding data response."""
    message: str
    profile: UserProfileResponse


# Helper function to make onboarding work without auth in dev mode
async def get_current_user_optional(db: AsyncSession = Depends(get_db)):
    """Get current user if authenticated, otherwise return None (dev mode)."""
    try:
        from app.api.v1.endpoints.auth import get_current_user
        user = await get_current_user(db=db)
        return user
    except:
        # Dev mode: return None or create a mock user
        return None


@router.post("/onboarding", response_model=OnboardingDataResponse)
async def save_onboarding_data(
    onboarding_data: OnboardingDataRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Save user onboarding data (industry, role, preferences).
    Requires authentication via JWT token.
    """
    # Update user profile with onboarding data
    current_user.industry = onboarding_data.industry
    current_user.industry_segment = onboarding_data.industry_segment
    current_user.user_role = onboarding_data.user_role

    # Update preferences
    if onboarding_data.preferred_language:
        current_user.preferred_language = onboarding_data.preferred_language
    if onboarding_data.preferred_depth:
        current_user.preferred_depth = onboarding_data.preferred_depth
    if onboarding_data.preferred_format:
        current_user.preferred_format = onboarding_data.preferred_format

    # Mark onboarding as completed
    current_user.onboarding_completed = True
    current_user.updated_at = datetime.utcnow()

    # Commit changes to database
    await db.commit()
    await db.refresh(current_user)

    # Return updated profile
    return OnboardingDataResponse(
        message="Onboarding data saved successfully",
        profile=UserProfileResponse(
            id=str(current_user.id),
            email=current_user.email,
            name=current_user.name,
            role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
            industry=current_user.industry,
            industry_segment=current_user.industry_segment,
            user_role=current_user.user_role,
            use_cases=onboarding_data.use_cases,  # Pass through from request (not stored in DB)
            preferred_language=current_user.preferred_language,
            preferred_depth=current_user.preferred_depth,
            preferred_format=current_user.preferred_format,
            timezone=current_user.timezone or "Europe/Warsaw",
            onboarding_completed=current_user.onboarding_completed
        )
    )


@router.get("/test-500-error")
async def test_500_error():
    """
    Test endpoint to trigger a 500 error for testing error handling.
    """
    raise HTTPException(
        status_code=500,
        detail="This is a test 500 error for testing error handling in the frontend"
    )
