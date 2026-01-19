"""
Research API Endpoints
"""

from fastapi import APIRouter, Depends
from typing import List
from pydantic import BaseModel

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


class ResearchItem(BaseModel):
    id: str
    name: str
    status: str
    progress: int
    created_at: str


class ResearchResponse(BaseModel):
    items: List[ResearchItem]
    total: int


@router.get("/active")
async def get_active_research(current_user: User = Depends(get_current_user)):
    """Get user's active research sessions."""
    # TODO: Replace with real database queries
    # For now, return empty list to show proper empty states
    return ResearchResponse(
        items=[],
        total=0
    )
