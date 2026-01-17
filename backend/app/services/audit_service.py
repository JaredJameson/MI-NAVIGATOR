"""
Audit Service - Helper functions for audit logging
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.audit_log import AuditLog
from app.models.user import User
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import Request


async def log_audit(
    db: AsyncSession,
    user: User,
    action_type: str,
    resource_type: str,
    resource_id: str,
    description: str,
    request: Optional[Request] = None,
    extra_data: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """
    Log an audit event to the database

    Args:
        db: Database session
        user: User performing the action
        action_type: Type of action (e.g., "report.delete", "report.share")
        resource_type: Type of resource (e.g., "report", "user", "project")
        resource_id: ID of the affected resource
        description: Human-readable description of the action
        request: FastAPI request object (optional, for IP/user-agent)
        extra_data: Additional metadata as dictionary (optional)

    Returns:
        AuditLog: Created audit log entry
    """
    # Extract request metadata
    ip_address = None
    user_agent = None

    if request:
        # Get client IP (handle proxies)
        ip_address = request.client.host if request.client else None

        # Handle X-Forwarded-For header for proxies
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip_address = forwarded_for.split(",")[0].strip()

        # Get user agent
        user_agent = request.headers.get("User-Agent")

    # Create audit log entry
    audit_log = AuditLog(
        user_id=str(user.id),
        user_email=user.email,
        action_type=action_type,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        extra_data=extra_data
    )

    db.add(audit_log)
    await db.commit()
    await db.refresh(audit_log)

    return audit_log


async def get_audit_logs(
    db: AsyncSession,
    user_id: Optional[str] = None,
    action_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> list[AuditLog]:
    """
    Query audit logs with filters

    Args:
        db: Database session
        user_id: Filter by user ID (optional)
        action_type: Filter by action type (optional)
        resource_type: Filter by resource type (optional)
        resource_id: Filter by resource ID (optional)
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        list[AuditLog]: List of audit log entries
    """
    query = select(AuditLog)

    # Apply filters
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if action_type:
        query = query.where(AuditLog.action_type == action_type)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    if resource_id:
        query = query.where(AuditLog.resource_id == resource_id)

    # Order by most recent first
    query = query.order_by(AuditLog.created_at.desc())

    # Pagination
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return result.scalars().all()


# Predefined action types for consistency
class AuditAction:
    """Audit action type constants"""

    # Report actions
    REPORT_CREATE = "report.create"
    REPORT_UPDATE = "report.update"
    REPORT_DELETE = "report.delete"
    REPORT_SHARE = "report.share"
    REPORT_EXPORT = "report.export"
    REPORT_ARCHIVE = "report.archive"
    REPORT_UNARCHIVE = "report.unarchive"

    # User actions
    USER_DELETE = "user.delete"
    USER_UPDATE = "user.update"
    USER_PASSWORD_CHANGE = "user.password_change"

    # Settings actions
    SETTINGS_CHANGE = "settings.change"
    SECURITY_CHANGE = "security.change"

    # Project actions
    PROJECT_DELETE = "project.delete"
    PROJECT_SHARE = "project.share"


# Predefined resource types
class ResourceType:
    """Resource type constants"""
    REPORT = "report"
    USER = "user"
    PROJECT = "project"
    WORKSPACE = "workspace"
    SETTINGS = "settings"
