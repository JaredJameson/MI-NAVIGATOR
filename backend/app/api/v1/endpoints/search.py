"""
Search API Endpoints - Quick search with suggestions
"""

from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from pydantic import BaseModel

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


class SearchSuggestion(BaseModel):
    id: str
    name: str
    type: str  # 'company', 'report', 'person', 'pkd'
    subtitle: Optional[str] = None
    url: str


class SuggestionsResponse(BaseModel):
    suggestions: List[SearchSuggestion]
    query: str


# Import mock data from other endpoints
MOCK_COMPANIES = [
    {"id": "1", "name": "FADO Sp. z o.o.", "nip": "5260016831", "type": "company"},
    {"id": "2", "name": "Splast S.A.", "nip": "6781234567", "type": "company"},
    {"id": "3", "name": "TechSoft Sp. z o.o.", "nip": "1234567890", "type": "company"},
    {"id": "4", "name": "LogiTrans S.A.", "nip": "9876543210", "type": "company"},
    {"id": "5", "name": "MetalPro Sp. z o.o.", "nip": "1122334455", "type": "company"},
    {"id": "6", "name": "ConsultPro Sp. z o.o.", "nip": "5566778899", "type": "company"},
    {"id": "7", "name": "PlastPak Sp. z o.o.", "nip": "9988776655", "type": "company"},
]

MOCK_REPORTS = [
    {"id": "report_001", "title": "Analiza profilu FADO Sp. z o.o.", "company": "FADO Sp. z o.o.", "type": "report"},
    {"id": "report_002", "title": "Analiza rynku tworzyw sztucznych", "company": None, "type": "report"},
    {"id": "report_003", "title": "Due Diligence TechSoft", "company": "TechSoft Sp. z o.o.", "type": "report"},
]

MOCK_PEOPLE = [
    {"id": "person_001", "name": "Jan Kowalski", "role": "CEO, FADO Sp. z o.o.", "type": "person"},
    {"id": "person_002", "name": "Anna Nowak", "role": "CFO, Splast S.A.", "type": "person"},
    {"id": "person_003", "name": "Piotr Wiśniewski", "role": "Prezes, TechSoft", "type": "person"},
]

PKD_SUGGESTIONS = [
    {"id": "22.21.Z", "name": "22.21.Z - Produkcja płyt, arkuszy, rur", "type": "pkd"},
    {"id": "22.22.Z", "name": "22.22.Z - Produkcja opakowań z tworzyw", "type": "pkd"},
    {"id": "62.01.Z", "name": "62.01.Z - Działalność związana z oprogramowaniem", "type": "pkd"},
    {"id": "62.02.Z", "name": "62.02.Z - Doradztwo w zakresie informatyki", "type": "pkd"},
    {"id": "49.41.Z", "name": "49.41.Z - Transport drogowy towarów", "type": "pkd"},
]


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(8, ge=1, le=20, description="Maximum number of suggestions"),
    current_user: User = Depends(get_current_user)
):
    """
    Get search suggestions for the quick search bar.
    Returns suggestions from companies, reports, people, and PKD codes.
    """
    q_lower = q.lower()
    suggestions: List[SearchSuggestion] = []

    # Search in companies
    for company in MOCK_COMPANIES:
        if q_lower in company["name"].lower() or q in company.get("nip", ""):
            suggestions.append(SearchSuggestion(
                id=company["id"],
                name=company["name"],
                type="company",
                subtitle=f"NIP: {company['nip']}",
                url=f"/companies/{company['id']}"
            ))

    # Search in reports
    for report in MOCK_REPORTS:
        if q_lower in report["title"].lower():
            suggestions.append(SearchSuggestion(
                id=report["id"],
                name=report["title"],
                type="report",
                subtitle=report.get("company"),
                url=f"/reports/{report['id']}"
            ))

    # Search in people
    for person in MOCK_PEOPLE:
        if q_lower in person["name"].lower():
            suggestions.append(SearchSuggestion(
                id=person["id"],
                name=person["name"],
                type="person",
                subtitle=person.get("role"),
                url=f"/people/{person['id']}"
            ))

    # Search in PKD codes
    for pkd in PKD_SUGGESTIONS:
        if q_lower in pkd["name"].lower() or q_lower in pkd["id"].lower():
            suggestions.append(SearchSuggestion(
                id=pkd["id"],
                name=pkd["name"],
                type="pkd",
                subtitle="Kod PKD",
                url=f"/search?pkd={pkd['id']}"
            ))

    # Sort: companies first, then reports, then people, then PKD
    type_order = {"company": 0, "report": 1, "person": 2, "pkd": 3}
    suggestions.sort(key=lambda x: type_order.get(x.type, 99))

    return SuggestionsResponse(
        suggestions=suggestions[:limit],
        query=q
    )
