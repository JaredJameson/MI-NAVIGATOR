"""
Notifications API Endpoints
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


# Notification types
NOTIFICATION_TYPES = {
    "report_ready": {"label": "Raport gotowy", "icon": "document", "color": "green"},
    "alert": {"label": "Alert", "icon": "bell", "color": "orange"},
    "project_update": {"label": "Aktualizacja projektu", "icon": "folder", "color": "blue"},
    "comment": {"label": "Komentarz", "icon": "chat", "color": "purple"},
    "system": {"label": "System", "icon": "info", "color": "gray"},
}


# Mock notifications storage per user
def generate_mock_notifications() -> List[dict]:
    """Generate mock notifications."""
    now = datetime.now()

    return [
        {
            "id": "notif_001",
            "type": "report_ready",
            "title": "Raport gotowy",
            "message": "Raport 'Analiza profilu FADO Sp. z o.o.' jest gotowy do przeglądu.",
            "link": "/reports/report_001",
            "read": False,
            "created_at": (now - timedelta(minutes=15)).isoformat() + "Z",
        },
        {
            "id": "notif_002",
            "type": "alert",
            "title": "Nowy alert",
            "message": "Wykryto nowy produkt konkurenta X.",
            "link": "/alerts/alert_001",
            "read": False,
            "created_at": (now - timedelta(hours=1)).isoformat() + "Z",
        },
        {
            "id": "notif_003",
            "type": "project_update",
            "title": "Projekt zaktualizowany",
            "message": "Dodano 2 nowe raporty do projektu 'Due Diligence - FADO'.",
            "link": "/projects/project_001",
            "read": False,
            "created_at": (now - timedelta(hours=3)).isoformat() + "Z",
        },
        {
            "id": "notif_004",
            "type": "comment",
            "title": "Nowy komentarz",
            "message": "Jan Kowalski skomentował raport 'Analiza rynku tworzyw'.",
            "link": "/reports/report_002",
            "read": True,
            "created_at": (now - timedelta(hours=5)).isoformat() + "Z",
        },
        {
            "id": "notif_005",
            "type": "system",
            "title": "Aktualizacja systemu",
            "message": "Nowe funkcje dostępne w panelu raportów.",
            "link": "/reports",
            "read": True,
            "created_at": (now - timedelta(days=1)).isoformat() + "Z",
        },
        {
            "id": "notif_006",
            "type": "report_ready",
            "title": "Raport gotowy",
            "message": "Raport 'Due Diligence - TechSoft' jest gotowy.",
            "link": "/reports/report_003",
            "read": False,
            "created_at": (now - timedelta(hours=2)).isoformat() + "Z",
        },
        {
            "id": "notif_007",
            "type": "alert",
            "title": "Alert cenowy",
            "message": "Zmiana cen u dostawcy ABC.",
            "link": "/alerts/alert_002",
            "read": True,
            "created_at": (now - timedelta(days=2)).isoformat() + "Z",
        },
    ]


# In-memory storage (keyed by user ID)
USER_NOTIFICATIONS: dict = {}


def get_user_notifications(user_id: str) -> List[dict]:
    """Get notifications for a user, initializing with mock data if needed."""
    if user_id not in USER_NOTIFICATIONS:
        USER_NOTIFICATIONS[user_id] = generate_mock_notifications()
    return USER_NOTIFICATIONS[user_id]


class NotificationItem(BaseModel):
    id: str
    type: str
    title: str
    message: str
    link: Optional[str]
    read: bool
    created_at: str


class NotificationsResponse(BaseModel):
    items: List[NotificationItem]
    total: int
    unread_count: int


class MarkReadRequest(BaseModel):
    notification_ids: List[str]


@router.get("/")
async def list_notifications(
    unread_only: bool = False,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """List user's notifications."""
    user_id = str(current_user.id)
    notifications = get_user_notifications(user_id)

    if unread_only:
        filtered = [n for n in notifications if not n["read"]]
    else:
        filtered = notifications

    # Sort by created_at (most recent first)
    filtered.sort(
        key=lambda x: datetime.fromisoformat(x["created_at"].replace("Z", "+00:00")),
        reverse=True
    )

    # Apply limit
    items = filtered[:limit]
    unread_count = sum(1 for n in notifications if not n["read"])

    return NotificationsResponse(
        items=[NotificationItem(**n) for n in items],
        total=len(notifications),
        unread_count=unread_count
    )


@router.get("/unread-count")
async def get_unread_count(current_user: User = Depends(get_current_user)):
    """Get count of unread notifications."""
    user_id = str(current_user.id)
    notifications = get_user_notifications(user_id)
    unread_count = sum(1 for n in notifications if not n["read"])
    return {"unread_count": unread_count}


@router.post("/mark-read")
async def mark_notifications_read(
    request: MarkReadRequest,
    current_user: User = Depends(get_current_user)
):
    """Mark specific notifications as read."""
    user_id = str(current_user.id)
    notifications = get_user_notifications(user_id)

    marked_count = 0
    for notification in notifications:
        if notification["id"] in request.notification_ids:
            if not notification["read"]:
                notification["read"] = True
                marked_count += 1

    unread_count = sum(1 for n in notifications if not n["read"])

    return {
        "marked_count": marked_count,
        "unread_count": unread_count
    }


@router.post("/mark-all-read")
async def mark_all_notifications_read(current_user: User = Depends(get_current_user)):
    """Mark all notifications as read."""
    user_id = str(current_user.id)
    notifications = get_user_notifications(user_id)

    marked_count = 0
    for notification in notifications:
        if not notification["read"]:
            notification["read"] = True
            marked_count += 1

    return {
        "marked_count": marked_count,
        "unread_count": 0
    }


@router.get("/{notification_id}")
async def get_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific notification and mark it as read."""
    user_id = str(current_user.id)
    notifications = get_user_notifications(user_id)

    for notification in notifications:
        if notification["id"] == notification_id:
            # Mark as read when viewed
            was_unread = not notification["read"]
            notification["read"] = True

            type_info = NOTIFICATION_TYPES.get(notification["type"], {})
            unread_count = sum(1 for n in notifications if not n["read"])

            return {
                **notification,
                "type_label": type_info.get("label", notification["type"]),
                "type_icon": type_info.get("icon", "bell"),
                "type_color": type_info.get("color", "gray"),
                "was_unread": was_unread,
                "unread_count": unread_count
            }

    raise HTTPException(status_code=404, detail="Notification not found")
