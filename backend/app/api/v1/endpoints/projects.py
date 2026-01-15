"""
Projects API Endpoints
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


# Models
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: str = "research"  # research, due_diligence, market_analysis, competitive


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None


class BulkAssignRequest(BaseModel):
    report_ids: List[str]
    project_id: str


# Mock projects database (global storage)
MOCK_PROJECTS = {
    "project_001": {
        "id": "project_001",
        "name": "Due Diligence - FADO",
        "description": "Kompleksowy due diligence firmy FADO Sp. z o.o. w celu oceny inwestycyjnej.",
        "type": "due_diligence",
        "created_at": "2026-01-10T09:00:00Z",
        "updated_at": "2026-01-14T15:30:00Z",
        "status": "active",
        "owner_id": "user_001",
        "report_ids": ["report_001"],
    },
    "project_002": {
        "id": "project_002",
        "name": "Analiza rynku tworzyw sztucznych",
        "description": "Badanie rynku tworzyw sztucznych w Polsce i Europie.",
        "type": "market_analysis",
        "created_at": "2026-01-08T11:00:00Z",
        "updated_at": "2026-01-13T14:20:00Z",
        "status": "active",
        "owner_id": "user_001",
        "report_ids": ["report_002"],
    },
    "project_003": {
        "id": "project_003",
        "name": "Monitoring konkurencji IT",
        "description": "Stałe monitorowanie konkurentów w sektorze IT.",
        "type": "competitive",
        "created_at": "2026-01-05T08:30:00Z",
        "updated_at": "2026-01-12T10:45:00Z",
        "status": "active",
        "owner_id": "user_001",
        "report_ids": ["report_003"],
    },
}

# Counter for new project IDs
project_counter = 4


@router.get("/")
async def list_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """List user's research projects."""
    projects = list(MOCK_PROJECTS.values())

    # Paginate
    start = (page - 1) * limit
    end = start + limit
    paginated = projects[start:end]

    return {
        "items": paginated,
        "total": len(projects),
        "page": page,
        "limit": limit
    }


@router.post("/")
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new research project."""
    global project_counter

    project_id = f"project_{project_counter:03d}"
    project_counter += 1

    new_project = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "type": project.type,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "status": "active",
        "owner_id": str(current_user.id),
        "report_ids": [],
    }

    MOCK_PROJECTS[project_id] = new_project

    return new_project


@router.get("/{project_id}")
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get project details."""
    if project_id not in MOCK_PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    return MOCK_PROJECTS[project_id]


@router.put("/{project_id}")
async def update_project(
    project_id: str,
    project: ProjectUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update project details."""
    if project_id not in MOCK_PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    existing = MOCK_PROJECTS[project_id]

    if project.name is not None:
        existing["name"] = project.name
    if project.description is not None:
        existing["description"] = project.description
    if project.type is not None:
        existing["type"] = project.type

    existing["updated_at"] = datetime.utcnow().isoformat() + "Z"

    return existing


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a project."""
    if project_id not in MOCK_PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    del MOCK_PROJECTS[project_id]

    return {"message": "Project deleted successfully"}


@router.get("/{project_id}/activity")
async def get_project_activity(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get project activity feed."""
    if project_id not in MOCK_PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    # Mock activity data
    activities = [
        {
            "id": "activity_001",
            "type": "report_added",
            "description": "Dodano raport do projektu",
            "user": "Jan Kowalski",
            "timestamp": "2026-01-14T15:30:00Z"
        },
        {
            "id": "activity_002",
            "type": "project_updated",
            "description": "Zaktualizowano opis projektu",
            "user": "Jan Kowalski",
            "timestamp": "2026-01-14T10:00:00Z"
        }
    ]

    return {"activities": activities}


@router.post("/{project_id}/reports")
async def add_report_to_project(
    project_id: str,
    report_id: str = Query(..., description="ID of the report to add"),
    current_user: User = Depends(get_current_user)
):
    """Add a report to project."""
    if project_id not in MOCK_PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    project = MOCK_PROJECTS[project_id]

    if report_id not in project["report_ids"]:
        project["report_ids"].append(report_id)
        project["updated_at"] = datetime.utcnow().isoformat() + "Z"

    return {"message": "Report added to project", "report_ids": project["report_ids"]}


@router.delete("/{project_id}/reports/{report_id}")
async def remove_report_from_project(
    project_id: str,
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove a report from project."""
    if project_id not in MOCK_PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    project = MOCK_PROJECTS[project_id]

    if report_id in project["report_ids"]:
        project["report_ids"].remove(report_id)
        project["updated_at"] = datetime.utcnow().isoformat() + "Z"

    return {"message": "Report removed from project", "report_ids": project["report_ids"]}


@router.post("/bulk-assign")
async def bulk_assign_reports(
    request: BulkAssignRequest,
    current_user: User = Depends(get_current_user)
):
    """Assign multiple reports to a project at once."""
    if request.project_id not in MOCK_PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    project = MOCK_PROJECTS[request.project_id]

    added_count = 0
    for report_id in request.report_ids:
        if report_id not in project["report_ids"]:
            project["report_ids"].append(report_id)
            added_count += 1

    project["updated_at"] = datetime.utcnow().isoformat() + "Z"

    return {
        "message": f"Przypisano {added_count} raportów do projektu",
        "project_id": request.project_id,
        "report_ids": project["report_ids"],
        "added_count": added_count
    }


@router.get("/{project_id}/reports")
async def get_project_reports(
    project_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all reports in a project."""
    if project_id not in MOCK_PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    project = MOCK_PROJECTS[project_id]

    # Import MOCK_REPORTS from reports module to get report details
    from app.api.v1.endpoints.reports import MOCK_REPORTS

    reports = []
    for report_id in project["report_ids"]:
        for report in MOCK_REPORTS:
            if report["id"] == report_id:
                reports.append({
                    "id": report["id"],
                    "title": report["title"],
                    "type": report["type"],
                    "company": report.get("company"),
                    "status": report["status"],
                    "updated_at": report["updated_at"]
                })
                break

    return {"reports": reports, "count": len(reports)}
