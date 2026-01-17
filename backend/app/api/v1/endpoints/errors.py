"""
Error tracking endpoints.
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from app.db.session import get_db
from app.models.error_log import ErrorLog
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


class ErrorLogRequest(BaseModel):
    """Request model for logging an error."""
    error_type: str = Field(..., description="Type of error (e.g., TypeError, ReferenceError)")
    error_message: str = Field(..., description="Error message")
    stack_trace: Optional[str] = Field(None, description="Stack trace")
    url: Optional[str] = Field(None, description="URL where error occurred")
    metadata: Optional[dict] = Field(None, description="Additional metadata (component, props, etc.)")


class ErrorLogResponse(BaseModel):
    """Response model for error log."""
    id: str
    error_type: str
    error_message: str
    stack_trace: Optional[str]
    source: str
    url: Optional[str]
    user_email: Optional[str]
    resolved: bool
    occurred_at: datetime

    class Config:
        from_attributes = True


@router.post("/log", status_code=201)
async def log_error(
    error: ErrorLogRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Log a frontend error.

    This endpoint is public (doesn't require authentication) to catch errors
    that occur before/during login.
    """
    # For now, errors are logged without user context
    # (can be enhanced later to extract user from JWT token if present)
    current_user = None

    # Create error log
    error_log = ErrorLog(
        id=str(uuid.uuid4()),
        error_type=error.error_type,
        error_message=error.error_message,
        stack_trace=error.stack_trace,
        source="frontend",
        url=error.url,
        user_agent=request.headers.get("user-agent"),
        user_id=current_user.id if current_user else None,
        user_email=current_user.email if current_user else None,
        error_metadata=error.metadata,
        resolved=False
    )

    db.add(error_log)
    db.commit()
    db.refresh(error_log)

    return {"id": error_log.id, "message": "Error logged successfully"}


@router.get("/errors", response_model=List[ErrorLogResponse])
async def get_errors(
    resolved: Optional[bool] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get error logs (admin only).

    Filters:
    - resolved: Filter by resolved status
    - limit: Maximum number of errors to return (default 50)
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    query = db.query(ErrorLog)

    if resolved is not None:
        query = query.filter(ErrorLog.resolved == resolved)

    query = query.order_by(ErrorLog.occurred_at.desc())
    query = query.limit(limit)

    errors = query.all()
    return errors


@router.get("/errors/my", response_model=List[ErrorLogResponse])
async def get_my_errors(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get errors for the current user."""
    errors = db.query(ErrorLog)\
        .filter(ErrorLog.user_id == current_user.id)\
        .order_by(ErrorLog.occurred_at.desc())\
        .limit(limit)\
        .all()

    return errors


@router.patch("/errors/{error_id}/resolve")
async def resolve_error(
    error_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark an error as resolved (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    error = db.query(ErrorLog).filter(ErrorLog.id == error_id).first()

    if not error:
        raise HTTPException(status_code=404, detail="Error not found")

    error.resolved = True
    db.commit()

    return {"message": "Error marked as resolved"}


@router.get("/errors/stats")
async def get_error_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get error statistics (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    total_errors = db.query(ErrorLog).count()
    unresolved_errors = db.query(ErrorLog).filter(ErrorLog.resolved == False).count()
    resolved_errors = db.query(ErrorLog).filter(ErrorLog.resolved == True).count()

    # Group by error type
    from sqlalchemy import func
    error_types = db.query(
        ErrorLog.error_type,
        func.count(ErrorLog.id).label('count')
    ).group_by(ErrorLog.error_type).all()

    return {
        "total": total_errors,
        "unresolved": unresolved_errors,
        "resolved": resolved_errors,
        "by_type": {et.error_type: et.count for et in error_types}
    }
