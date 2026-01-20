"""
A/B Testing Router
Handles variant assignment and tracking for experiments
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import hashlib
import random
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user_optional

router = APIRouter()


def get_or_assign_variant(
    user_id: Optional[str],
    session_id: str,
    experiment_name: str = "default_experiment"
) -> str:
    """
    Assign a variant (A or B) to a user/session.
    Uses consistent hashing to ensure the same user/session always gets the same variant.
    """
    # Create a deterministic hash based on user_id or session_id
    identifier = user_id if user_id else session_id
    hash_input = f"{experiment_name}:{identifier}"
    hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)

    # Use modulo to split 50/50 between A and B
    variant = "B" if hash_value % 2 == 0 else "A"

    return variant


@router.get("/variant")
async def get_variant(
    request: Request,
    response: Response,
    experiment: str = "default_experiment",
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get or assign A/B test variant for the current user/session.
    Returns consistent variant based on user ID or session ID.
    """
    # Get or create session ID from cookie
    session_id = request.cookies.get("ab_session_id")
    if not session_id:
        # Generate new session ID
        session_id = hashlib.md5(f"{datetime.utcnow().isoformat()}:{random.random()}".encode()).hexdigest()
        # Set cookie (expires in 30 days)
        response.set_cookie(
            key="ab_session_id",
            value=session_id,
            max_age=30 * 24 * 60 * 60,  # 30 days
            httponly=True,
            samesite="lax"
        )

    # Get user ID if authenticated
    user_id = str(current_user.id) if current_user else None

    # Assign variant
    variant = get_or_assign_variant(user_id, session_id, experiment)

    return {
        "experiment": experiment,
        "variant": variant,
        "session_id": session_id,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/track")
async def track_event(
    request: Request,
    experiment: str,
    variant: str,
    event_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Track an A/B test event (e.g., conversion, click, etc.)
    """
    session_id = request.cookies.get("ab_session_id")
    user_id = str(current_user.id) if current_user else None

    # Log the event (in a real system, this would be stored in a database)
    # For MVP, we just acknowledge the tracking
    print(f"[A/B Test Tracking] experiment={experiment}, variant={variant}, event={event_name}, user_id={user_id}, session_id={session_id}")

    return {
        "status": "tracked",
        "experiment": experiment,
        "variant": variant,
        "event": event_name,
        "timestamp": datetime.utcnow().isoformat()
    }
