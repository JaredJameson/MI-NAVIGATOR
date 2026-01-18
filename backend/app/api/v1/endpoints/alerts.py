"""
Alerts API Endpoints
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


# Alert severity levels
SEVERITY_LEVELS = {
    "high": {"label": "Wysoki", "color": "red", "indicator": "🔴"},
    "medium": {"label": "Średni", "color": "yellow", "indicator": "🟡"},
    "low": {"label": "Niski", "color": "green", "indicator": "🟢"},
}


# Mock alerts storage per user
def generate_mock_alerts() -> List[dict]:
    """Generate mock alerts with different severity levels."""
    now = datetime.now()

    return [
        {
            "id": "alert_001",
            "severity": "high",
            "title": "Konkurent X: nowy produkt",
            "description": "Wykryto ogłoszenie nowego produktu",
            "source": "Web monitoring",
            "company": "Konkurent X",
            "created_at": (now - timedelta(hours=1)).isoformat() + "Z",
            "read": False,
        },
        {
            "id": "alert_002",
            "severity": "medium",
            "title": "FADO: zmiana w zarządzie",
            "description": "Nowy członek zarządu",
            "source": "KRS monitoring",
            "company": "FADO Sp. z o.o.",
            "created_at": (now - timedelta(hours=3)).isoformat() + "Z",
            "read": False,
        },
        {
            "id": "alert_003",
            "severity": "low",
            "title": "Rynek +5% vs prognoza",
            "description": "Pozytywny trend rynkowy",
            "source": "Market analysis",
            "company": None,
            "created_at": (now - timedelta(hours=5)).isoformat() + "Z",
            "read": False,
        },
        {
            "id": "alert_004",
            "severity": "high",
            "title": "TechCorp: spadek przychodów",
            "description": "Wykryto znaczący spadek przychodów w ostatnim kwartale",
            "source": "Financial monitoring",
            "company": "TechCorp",
            "created_at": (now - timedelta(days=1)).isoformat() + "Z",
            "read": True,
        },
        {
            "id": "alert_005",
            "severity": "medium",
            "title": "Nowe regulacje branżowe",
            "description": "Planowane zmiany w przepisach od Q2 2024",
            "source": "Regulatory monitoring",
            "company": None,
            "created_at": (now - timedelta(days=2)).isoformat() + "Z",
            "read": True,
        },
    ]


# In-memory storage (keyed by user ID)
USER_ALERTS: dict = {}


def get_user_alerts(user_id: str) -> List[dict]:
    """Get alerts for a user, initializing with mock data if needed."""
    if user_id not in USER_ALERTS:
        USER_ALERTS[user_id] = generate_mock_alerts()
    return USER_ALERTS[user_id]


class AlertItem(BaseModel):
    id: str
    severity: str
    title: str
    description: str
    source: str
    company: Optional[str]
    created_at: str
    read: bool


class AlertsResponse(BaseModel):
    items: List[AlertItem]
    total: int
    unread_count: int


class AlertDetailsResponse(BaseModel):
    id: str
    severity: str
    severity_label: str
    severity_color: str
    severity_indicator: str
    title: str
    description: str
    source: str
    company: Optional[str]
    created_at: str
    read: bool


class MarkReadRequest(BaseModel):
    alert_ids: List[str]


class CreateAlertRequest(BaseModel):
    company_name: Optional[str] = None
    company_id: Optional[str] = None
    keyword: Optional[str] = None
    alert_type: str  # news, financial, competitor
    conditions: Optional[dict] = None


class AlertConfig(BaseModel):
    id: str
    user_id: str
    company_name: Optional[str]
    company_id: Optional[str]
    keyword: Optional[str]
    alert_type: str
    conditions: Optional[dict]
    is_active: bool
    created_at: str


# In-memory storage for alert configurations (keyed by user ID)
USER_ALERT_CONFIGS: dict = {}


def get_user_alert_configs(user_id: str) -> List[dict]:
    """Get alert configurations for a user."""
    if user_id not in USER_ALERT_CONFIGS:
        USER_ALERT_CONFIGS[user_id] = []
    return USER_ALERT_CONFIGS[user_id]


@router.get("/")
async def list_alerts(
    severity: Optional[str] = None,
    unread_only: bool = False,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """List user's alerts."""
    user_id = str(current_user.id)
    alerts = get_user_alerts(user_id)

    # Filter by severity if specified
    if severity:
        if severity not in SEVERITY_LEVELS:
            raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
        alerts = [a for a in alerts if a["severity"] == severity]

    # Filter by read status
    if unread_only:
        alerts = [a for a in alerts if not a["read"]]

    # Sort by created_at (most recent first)
    alerts.sort(
        key=lambda x: datetime.fromisoformat(x["created_at"].replace("Z", "+00:00")),
        reverse=True
    )

    # Apply limit
    items = alerts[:limit]

    # Count all unread alerts (not just filtered ones)
    all_alerts = get_user_alerts(user_id)
    unread_count = sum(1 for a in all_alerts if not a["read"])

    return AlertsResponse(
        items=[AlertItem(**a) for a in items],
        total=len(alerts),
        unread_count=unread_count
    )


@router.get("/configs")
async def list_alert_configs(
    current_user: User = Depends(get_current_user)
):
    """List user's alert configurations."""
    user_id = str(current_user.id)
    configs = get_user_alert_configs(user_id)

    # Sort by created_at (most recent first)
    configs.sort(
        key=lambda x: datetime.fromisoformat(x["created_at"].replace("Z", "+00:00")),
        reverse=True
    )

    return {
        "items": [AlertConfig(**c) for c in configs],
        "total": len(configs)
    }


@router.delete("/configs/{config_id}")
async def delete_alert_config(
    config_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an alert configuration."""
    user_id = str(current_user.id)
    configs = get_user_alert_configs(user_id)

    for i, config in enumerate(configs):
        if config["id"] == config_id:
            del configs[i]
            return {"success": True, "message": "Alert configuration deleted"}

    raise HTTPException(status_code=404, detail="Alert configuration not found")


@router.get("/{alert_id}")
async def get_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific alert and mark it as read."""
    user_id = str(current_user.id)
    alerts = get_user_alerts(user_id)

    for alert in alerts:
        if alert["id"] == alert_id:
            # Mark as read when viewed
            was_unread = not alert["read"]
            alert["read"] = True

            severity_info = SEVERITY_LEVELS.get(alert["severity"], {})

            return AlertDetailsResponse(
                **alert,
                severity_label=severity_info.get("label", alert["severity"]),
                severity_color=severity_info.get("color", "gray"),
                severity_indicator=severity_info.get("indicator", "⚪"),
            )

    raise HTTPException(status_code=404, detail="Alert not found")


@router.post("/mark-read")
async def mark_alerts_read(
    request: MarkReadRequest,
    current_user: User = Depends(get_current_user)
):
    """Mark specific alerts as read."""
    user_id = str(current_user.id)
    alerts = get_user_alerts(user_id)

    marked_count = 0
    for alert in alerts:
        if alert["id"] in request.alert_ids:
            if not alert["read"]:
                alert["read"] = True
                marked_count += 1

    unread_count = sum(1 for a in alerts if not a["read"])

    return {
        "marked_count": marked_count,
        "unread_count": unread_count
    }


@router.post("/mark-all-read")
async def mark_all_alerts_read(current_user: User = Depends(get_current_user)):
    """Mark all alerts as read."""
    user_id = str(current_user.id)
    alerts = get_user_alerts(user_id)

    marked_count = 0
    for alert in alerts:
        if not alert["read"]:
            alert["read"] = True
            marked_count += 1

    return {
        "marked_count": marked_count,
        "unread_count": 0
    }


@router.post("/create")
async def create_alert(
    request: CreateAlertRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new alert configuration."""
    import uuid

    user_id = str(current_user.id)

    # Validate alert type
    valid_types = ["news", "financial", "competitor"]
    if request.alert_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid alert_type. Must be one of: {', '.join(valid_types)}"
        )

    # At least one of company_name/company_id or keyword must be provided
    if not request.company_name and not request.company_id and not request.keyword:
        raise HTTPException(
            status_code=400,
            detail="Must provide at least one of: company_name, company_id, or keyword"
        )

    # Create new alert configuration
    alert_config = {
        "id": f"alert_config_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "company_name": request.company_name,
        "company_id": request.company_id,
        "keyword": request.keyword,
        "alert_type": request.alert_type,
        "conditions": request.conditions or {},
        "is_active": True,
        "created_at": datetime.now().isoformat() + "Z"
    }

    # Add to user's alert configs
    configs = get_user_alert_configs(user_id)
    configs.append(alert_config)

    return AlertConfig(**alert_config)

