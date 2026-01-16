"""
Tags API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


# In-memory tag storage
MOCK_TAGS = [
    {
        "id": "tag_001",
        "name": "Priorytet wysoki",
        "color": "#EF4444",  # red-500
        "description": "Raporty wymagające pilnej uwagi",
        "created_at": "2026-01-10T10:00:00Z",
        "user_id": "1",
    },
    {
        "id": "tag_002",
        "name": "Do przeglądu",
        "color": "#F59E0B",  # amber-500
        "description": "Raporty oczekujące na przegląd",
        "created_at": "2026-01-11T14:30:00Z",
        "user_id": "1",
    },
    {
        "id": "tag_003",
        "name": "Zaakceptowany",
        "color": "#10B981",  # green-500
        "description": "Raporty zatwierdzone do użycia",
        "created_at": "2026-01-12T09:15:00Z",
        "user_id": "1",
    },
]

# In-memory report-tag assignments
REPORT_TAGS = {
    "report_001": ["tag_001", "tag_003"],
    "report_002": ["tag_002"],
}


class TagCreate(BaseModel):
    name: str
    color: str
    description: Optional[str] = None


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None


class Tag(BaseModel):
    id: str
    name: str
    color: str
    description: Optional[str]
    created_at: str
    user_id: str


class ReportTagAssignment(BaseModel):
    report_id: str
    tag_ids: List[str]


@router.get("/", response_model=List[Tag])
async def list_tags():  # current_user: User = Depends(get_current_user)  # Disabled for testing
    """List all tags for the current user."""
    # Filter tags by user_id - disabled for testing, return all tags
    user_tags = [
        Tag(**tag) for tag in MOCK_TAGS
        # if tag["user_id"] == str(current_user.id)
    ]
    return user_tags


@router.post("/", response_model=Tag)
async def create_tag(
    tag: TagCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new tag."""
    # Generate unique tag ID
    tag_id = f"tag_{len(MOCK_TAGS) + 1:03d}"

    new_tag = {
        "id": tag_id,
        "name": tag.name,
        "color": tag.color,
        "description": tag.description,
        "created_at": datetime.now().isoformat() + "Z",
        "user_id": str(current_user.id),
    }

    MOCK_TAGS.append(new_tag)

    return Tag(**new_tag)


@router.get("/{tag_id}", response_model=Tag)
async def get_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific tag."""
    for tag in MOCK_TAGS:
        if tag["id"] == tag_id and tag["user_id"] == str(current_user.id):
            return Tag(**tag)

    raise HTTPException(status_code=404, detail="Tag not found")


@router.put("/{tag_id}", response_model=Tag)
async def update_tag(
    tag_id: str,
    tag_update: TagUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a tag."""
    for tag in MOCK_TAGS:
        if tag["id"] == tag_id and tag["user_id"] == str(current_user.id):
            # Update fields
            if tag_update.name is not None:
                tag["name"] = tag_update.name
            if tag_update.color is not None:
                tag["color"] = tag_update.color
            if tag_update.description is not None:
                tag["description"] = tag_update.description

            return Tag(**tag)

    raise HTTPException(status_code=404, detail="Tag not found")


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a tag."""
    global MOCK_TAGS, REPORT_TAGS

    # Find and remove the tag
    tag_to_delete = None
    for i, tag in enumerate(MOCK_TAGS):
        if tag["id"] == tag_id and tag["user_id"] == str(current_user.id):
            tag_to_delete = tag
            MOCK_TAGS.pop(i)
            break

    if not tag_to_delete:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Remove tag assignments from all reports
    for report_id in list(REPORT_TAGS.keys()):
        if tag_id in REPORT_TAGS[report_id]:
            REPORT_TAGS[report_id].remove(tag_id)
            if not REPORT_TAGS[report_id]:
                del REPORT_TAGS[report_id]

    return {"message": "Tag deleted successfully", "deleted_id": tag_id}


@router.get("/reports/{report_id}", response_model=List[Tag])
async def get_report_tags(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all tags assigned to a specific report."""
    tag_ids = REPORT_TAGS.get(report_id, [])

    # Return full tag objects
    tags = []
    for tag in MOCK_TAGS:
        if tag["id"] in tag_ids and tag["user_id"] == str(current_user.id):
            tags.append(Tag(**tag))

    return tags


@router.post("/reports/{report_id}")
async def assign_tags_to_report(
    report_id: str,
    tag_ids: List[str],
    current_user: User = Depends(get_current_user)
):
    """Assign tags to a report. Replaces existing tags."""
    # Validate that all tag_ids exist and belong to the user
    valid_tag_ids = []
    for tag_id in tag_ids:
        tag_exists = any(
            tag["id"] == tag_id and tag["user_id"] == str(current_user.id)
            for tag in MOCK_TAGS
        )
        if tag_exists:
            valid_tag_ids.append(tag_id)

    if len(valid_tag_ids) != len(tag_ids):
        raise HTTPException(status_code=400, detail="Some tag IDs are invalid")

    # Assign tags to report
    REPORT_TAGS[report_id] = valid_tag_ids

    return {
        "message": f"Assigned {len(valid_tag_ids)} tags to report",
        "report_id": report_id,
        "tag_ids": valid_tag_ids
    }


@router.post("/reports/{report_id}/add")
async def add_tag_to_report(
    report_id: str,
    tag_id: str,
    current_user: User = Depends(get_current_user)
):
    """Add a single tag to a report (doesn't replace existing)."""
    # Validate tag exists and belongs to user
    tag_exists = any(
        tag["id"] == tag_id and tag["user_id"] == str(current_user.id)
        for tag in MOCK_TAGS
    )

    if not tag_exists:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Add tag to report (avoid duplicates)
    if report_id not in REPORT_TAGS:
        REPORT_TAGS[report_id] = []

    if tag_id not in REPORT_TAGS[report_id]:
        REPORT_TAGS[report_id].append(tag_id)

    return {
        "message": "Tag added to report",
        "report_id": report_id,
        "tag_id": tag_id
    }


@router.delete("/reports/{report_id}/tags/{tag_id}")
async def remove_tag_from_report(
    report_id: str,
    tag_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove a specific tag from a report."""
    if report_id not in REPORT_TAGS or tag_id not in REPORT_TAGS[report_id]:
        raise HTTPException(status_code=404, detail="Tag assignment not found")

    REPORT_TAGS[report_id].remove(tag_id)

    # Clean up if no tags left
    if not REPORT_TAGS[report_id]:
        del REPORT_TAGS[report_id]

    return {
        "message": "Tag removed from report",
        "report_id": report_id,
        "tag_id": tag_id
    }
