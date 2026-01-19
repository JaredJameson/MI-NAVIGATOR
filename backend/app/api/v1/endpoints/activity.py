"""
Activity Log API Endpoints
"""

from fastapi import APIRouter, Query, Depends
from fastapi.responses import StreamingResponse
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
import io
import csv

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


# Activity types
ACTIVITY_TYPES = {
    "report_created": {"label": "Raport utworzony", "icon": "document-add", "color": "green"},
    "report_viewed": {"label": "Raport wyswietlony", "icon": "eye", "color": "blue"},
    "report_exported": {"label": "Raport wyeksportowany", "icon": "download", "color": "purple"},
    "report_deleted": {"label": "Raport usuniety", "icon": "trash", "color": "red"},
    "search_performed": {"label": "Wyszukiwanie", "icon": "search", "color": "gray"},
    "project_created": {"label": "Projekt utworzony", "icon": "folder-add", "color": "green"},
    "project_updated": {"label": "Projekt zaktualizowany", "icon": "folder", "color": "yellow"},
    "comment_added": {"label": "Komentarz dodany", "icon": "chat", "color": "blue"},
    "login": {"label": "Logowanie", "icon": "login", "color": "green"},
    "logout": {"label": "Wylogowanie", "icon": "logout", "color": "gray"},
    "settings_updated": {"label": "Ustawienia zmienione", "icon": "cog", "color": "yellow"},
    "alert_triggered": {"label": "Alert wyzwolony", "icon": "bell", "color": "orange"},
}


# Mock activity data
def generate_mock_activities() -> List[dict]:
    """Generate realistic mock activity data."""
    now = datetime.now()

    activities = [
        {
            "id": "act_001",
            "type": "report_created",
            "title": "Utworzono raport",
            "description": "Analiza profilu FADO Sp. z o.o.",
            "metadata": {"report_id": "report_001", "report_title": "Analiza profilu FADO Sp. z o.o."},
            "timestamp": (now - timedelta(hours=2)).isoformat() + "Z",
        },
        {
            "id": "act_002",
            "type": "search_performed",
            "title": "Wyszukiwanie PKD",
            "description": "Wyszukano firmy z kodem PKD 22.21.Z",
            "metadata": {"query": "22.21.Z", "results_count": 15},
            "timestamp": (now - timedelta(hours=3)).isoformat() + "Z",
        },
        {
            "id": "act_003",
            "type": "report_exported",
            "title": "Wyeksportowano raport",
            "description": "Raport FADO wyeksportowany do Excel",
            "metadata": {"report_id": "report_001", "format": "xlsx"},
            "timestamp": (now - timedelta(hours=4)).isoformat() + "Z",
        },
        {
            "id": "act_004",
            "type": "comment_added",
            "title": "Dodano komentarz",
            "description": "Komentarz do raportu Due Diligence TechSoft",
            "metadata": {"report_id": "report_003", "comment_preview": "Swietna analiza finansowa!"},
            "timestamp": (now - timedelta(hours=5)).isoformat() + "Z",
        },
        {
            "id": "act_005",
            "type": "project_created",
            "title": "Utworzono projekt",
            "description": "Due Diligence - FADO",
            "metadata": {"project_id": "project_001", "project_name": "Due Diligence - FADO"},
            "timestamp": (now - timedelta(hours=6)).isoformat() + "Z",
        },
        {
            "id": "act_006",
            "type": "login",
            "title": "Zalogowano",
            "description": "Logowanie z przegladarki Chrome",
            "metadata": {"browser": "Chrome", "os": "Windows 11", "ip": "192.168.1.100"},
            "timestamp": (now - timedelta(hours=8)).isoformat() + "Z",
        },
        {
            "id": "act_007",
            "type": "alert_triggered",
            "title": "Alert wyzwolony",
            "description": "Konkurent X: nowy produkt wykryty",
            "metadata": {"alert_name": "Monitoring konkurencji", "severity": "high"},
            "timestamp": (now - timedelta(hours=10)).isoformat() + "Z",
        },
        {
            "id": "act_008",
            "type": "report_viewed",
            "title": "Wyswietlono raport",
            "description": "Analiza rynku tworzyw sztucznych w Polsce",
            "metadata": {"report_id": "report_002", "duration_seconds": 180},
            "timestamp": (now - timedelta(hours=12)).isoformat() + "Z",
        },
        {
            "id": "act_009",
            "type": "settings_updated",
            "title": "Zaktualizowano ustawienia",
            "description": "Zmieniono preferencje jezyka na Polski",
            "metadata": {"setting": "preferred_language", "old_value": "en", "new_value": "pl"},
            "timestamp": (now - timedelta(days=1)).isoformat() + "Z",
        },
        {
            "id": "act_010",
            "type": "search_performed",
            "title": "Wyszukiwanie firmy",
            "description": "Wyszukano 'Splast S.A.'",
            "metadata": {"query": "Splast S.A.", "results_count": 1},
            "timestamp": (now - timedelta(days=1, hours=2)).isoformat() + "Z",
        },
        {
            "id": "act_011",
            "type": "report_created",
            "title": "Utworzono raport",
            "description": "Due Diligence - TechSoft Sp. z o.o.",
            "metadata": {"report_id": "report_003", "report_title": "Due Diligence - TechSoft Sp. z o.o."},
            "timestamp": (now - timedelta(days=1, hours=5)).isoformat() + "Z",
        },
        {
            "id": "act_012",
            "type": "project_updated",
            "title": "Zaktualizowano projekt",
            "description": "Dodano 2 raporty do projektu Market Analysis",
            "metadata": {"project_id": "project_002", "reports_added": 2},
            "timestamp": (now - timedelta(days=2)).isoformat() + "Z",
        },
        {
            "id": "act_013",
            "type": "report_deleted",
            "title": "Usunieto raport",
            "description": "Stary raport testowy",
            "metadata": {"report_id": "report_old_001", "report_title": "Test Report"},
            "timestamp": (now - timedelta(days=2, hours=3)).isoformat() + "Z",
        },
        {
            "id": "act_014",
            "type": "login",
            "title": "Zalogowano",
            "description": "Logowanie z urzadzenia mobilnego",
            "metadata": {"browser": "Safari", "os": "iOS 17", "ip": "192.168.1.101"},
            "timestamp": (now - timedelta(days=3)).isoformat() + "Z",
        },
        {
            "id": "act_015",
            "type": "alert_triggered",
            "title": "Alert wyzwolony",
            "description": "FADO: zmiana w zarzadzie",
            "metadata": {"alert_name": "Monitoring firmy FADO", "severity": "medium"},
            "timestamp": (now - timedelta(days=3, hours=5)).isoformat() + "Z",
        },
    ]

    return activities


MOCK_ACTIVITIES = generate_mock_activities()


class ActivityItem(BaseModel):
    id: str
    type: str
    title: str
    description: str
    metadata: dict
    timestamp: str


class ActivityResponse(BaseModel):
    items: List[ActivityItem]
    total: int
    page: int
    limit: int
    pages: int


class ActivityTypeInfo(BaseModel):
    type: str
    label: str
    icon: str
    color: str
    count: int


@router.get("/")
async def list_activities(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """List user's activity log with filtering and pagination."""
    # TODO: Replace with real database queries per user
    # For now, return empty list to show proper empty states
    filtered_activities = []

    # Filter by activity type
    if type:
        filtered_activities = [a for a in filtered_activities if a["type"] == type]

    # Filter by date range
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
            filtered_activities = [
                a for a in filtered_activities
                if datetime.fromisoformat(a["timestamp"].replace("Z", "+00:00")) >= from_date
            ]
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to.replace("Z", "+00:00"))
            filtered_activities = [
                a for a in filtered_activities
                if datetime.fromisoformat(a["timestamp"].replace("Z", "+00:00")) <= to_date
            ]
        except ValueError:
            pass

    # Sort by timestamp (most recent first)
    filtered_activities.sort(
        key=lambda x: datetime.fromisoformat(x["timestamp"].replace("Z", "+00:00")),
        reverse=True
    )

    total = len(filtered_activities)
    start = (page - 1) * limit
    end = start + limit
    items = filtered_activities[start:end]

    return ActivityResponse(
        items=[ActivityItem(**a) for a in items],
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/types")
async def get_activity_types(current_user: User = Depends(get_current_user)):
    """Get available activity types with counts."""
    type_counts = {}
    for activity in MOCK_ACTIVITIES:
        activity_type = activity["type"]
        type_counts[activity_type] = type_counts.get(activity_type, 0) + 1

    types_with_info = []
    for type_key, type_info in ACTIVITY_TYPES.items():
        types_with_info.append(ActivityTypeInfo(
            type=type_key,
            label=type_info["label"],
            icon=type_info["icon"],
            color=type_info["color"],
            count=type_counts.get(type_key, 0)
        ))

    # Sort by count descending
    types_with_info.sort(key=lambda x: x.count, reverse=True)

    return {"types": types_with_info}


@router.get("/summary")
async def get_activity_summary(current_user: User = Depends(get_current_user)):
    """Get activity summary statistics."""
    now = datetime.now()

    # Count activities by time period
    today_count = 0
    week_count = 0
    month_count = 0

    for activity in MOCK_ACTIVITIES:
        activity_time = datetime.fromisoformat(activity["timestamp"].replace("Z", "+00:00")).replace(tzinfo=None)
        delta = now - activity_time

        if delta.days == 0:
            today_count += 1
        if delta.days < 7:
            week_count += 1
        if delta.days < 30:
            month_count += 1

    # Most common activity type
    type_counts = {}
    for activity in MOCK_ACTIVITIES:
        activity_type = activity["type"]
        type_counts[activity_type] = type_counts.get(activity_type, 0) + 1

    most_common_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None

    return {
        "total_activities": len(MOCK_ACTIVITIES),
        "today": today_count,
        "this_week": week_count,
        "this_month": month_count,
        "most_common_type": most_common_type,
        "most_common_type_label": ACTIVITY_TYPES.get(most_common_type, {}).get("label", "Nieznany")
    }


@router.get("/{activity_id}")
async def get_activity(activity_id: str, current_user: User = Depends(get_current_user)):
    """Get details of a specific activity."""
    for activity in MOCK_ACTIVITIES:
        if activity["id"] == activity_id:
            type_info = ACTIVITY_TYPES.get(activity["type"], {})
            return {
                **activity,
                "type_label": type_info.get("label", activity["type"]),
                "type_icon": type_info.get("icon", "document"),
                "type_color": type_info.get("color", "gray"),
            }

    return {"error": "Activity not found"}


@router.get("/export/csv")
async def export_activities_csv(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Export activities to CSV file with date range filtering."""
    filtered_activities = MOCK_ACTIVITIES.copy()

    # Filter by activity type
    if type:
        filtered_activities = [a for a in filtered_activities if a["type"] == type]

    # Filter by date range
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
            filtered_activities = [
                a for a in filtered_activities
                if datetime.fromisoformat(a["timestamp"].replace("Z", "+00:00")) >= from_date
            ]
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to.replace("Z", "+00:00"))
            filtered_activities = [
                a for a in filtered_activities
                if datetime.fromisoformat(a["timestamp"].replace("Z", "+00:00")) <= to_date
            ]
        except ValueError:
            pass

    # Sort by timestamp (most recent first)
    filtered_activities.sort(
        key=lambda x: datetime.fromisoformat(x["timestamp"].replace("Z", "+00:00")),
        reverse=True
    )

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["ID", "Data i czas", "Typ", "Typ (etykieta)", "Tytul", "Opis"])

    # Write data
    for activity in filtered_activities:
        type_info = ACTIVITY_TYPES.get(activity["type"], {})
        timestamp = datetime.fromisoformat(activity["timestamp"].replace("Z", "+00:00"))
        formatted_date = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        writer.writerow([
            activity["id"],
            formatted_date,
            activity["type"],
            type_info.get("label", activity["type"]),
            activity["title"],
            activity["description"]
        ])

    output.seek(0)

    # Generate filename with date range
    now = datetime.now()
    filename = f"activity-export-{now.strftime('%Y%m%d-%H%M%S')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
