"""
Feedback API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


# Feedback types
FEEDBACK_TYPES = {
    "bug": {"label": "Zgłoszenie błędu", "icon": "bug"},
    "feature": {"label": "Propozycja funkcji", "icon": "lightbulb"},
    "improvement": {"label": "Sugestia ulepszenia", "icon": "arrow-up"},
    "question": {"label": "Pytanie", "icon": "question"},
    "other": {"label": "Inne", "icon": "chat"},
}


# In-memory storage for feedback
FEEDBACK_STORAGE: List[dict] = []


class FeedbackSubmission(BaseModel):
    type: str
    message: str
    page_context: Optional[str] = None


class FeedbackItem(BaseModel):
    id: str
    type: str
    type_label: str
    message: str
    page_context: Optional[str]
    user_id: str
    user_email: str
    created_at: str
    status: str


class FeedbackResponse(BaseModel):
    id: str
    message: str


class FeedbackListResponse(BaseModel):
    items: List[FeedbackItem]
    total: int


@router.get("/types")
async def get_feedback_types(current_user: User = Depends(get_current_user)):
    """Get available feedback types."""
    return {
        "types": [
            {"id": type_id, "label": info["label"], "icon": info["icon"]}
            for type_id, info in FEEDBACK_TYPES.items()
        ]
    }


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackSubmission,
    current_user: User = Depends(get_current_user)
):
    """Submit user feedback."""
    if feedback.type not in FEEDBACK_TYPES:
        raise HTTPException(status_code=400, detail="Invalid feedback type")

    if not feedback.message or len(feedback.message.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Feedback message must be at least 10 characters"
        )

    feedback_id = f"feedback_{len(FEEDBACK_STORAGE) + 1:04d}"

    feedback_item = {
        "id": feedback_id,
        "type": feedback.type,
        "type_label": FEEDBACK_TYPES[feedback.type]["label"],
        "message": feedback.message.strip(),
        "page_context": feedback.page_context,
        "user_id": str(current_user.id),
        "user_email": current_user.email,
        "created_at": datetime.now().isoformat() + "Z",
        "status": "new"
    }

    FEEDBACK_STORAGE.append(feedback_item)

    return FeedbackResponse(
        id=feedback_id,
        message="Dziękujemy za przesłanie opinii! Twoja wiadomość została zapisana."
    )


@router.get("/", response_model=FeedbackListResponse)
async def list_feedback(
    current_user: User = Depends(get_current_user)
):
    """List user's submitted feedback."""
    user_id = str(current_user.id)
    user_feedback = [
        FeedbackItem(**f) for f in FEEDBACK_STORAGE
        if f["user_id"] == user_id
    ]

    # Sort by created_at descending
    user_feedback.sort(
        key=lambda x: datetime.fromisoformat(x.created_at.replace("Z", "+00:00")),
        reverse=True
    )

    return FeedbackListResponse(
        items=user_feedback,
        total=len(user_feedback)
    )


@router.get("/{feedback_id}")
async def get_feedback(
    feedback_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific feedback item."""
    user_id = str(current_user.id)

    for feedback in FEEDBACK_STORAGE:
        if feedback["id"] == feedback_id and feedback["user_id"] == user_id:
            return FeedbackItem(**feedback)

    raise HTTPException(status_code=404, detail="Feedback not found")
