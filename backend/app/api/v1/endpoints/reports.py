"""
Reports API Endpoints
"""

from fastapi import APIRouter, Query, Depends
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


# Mock reports database
MOCK_REPORTS = [
    {
        "id": "report_001",
        "title": "Analiza profilu FADO Sp. z o.o.",
        "type": "company_profile",
        "company": "FADO Sp. z o.o.",
        "created_at": "2026-01-14T10:30:00Z",
        "updated_at": "2026-01-14T14:22:00Z",
        "status": "completed",
        "summary": "Kompleksowa analiza profilu firmy FADO Sp. z o.o. - lidera w produkcji tworzyw sztucznych.",
        "sections": [
            {
                "id": "section_1",
                "title": "Informacje podstawowe",
                "content": """FADO Sp. z o.o. to polska firma założona w 1998 roku, specjalizująca się w produkcji wyrobów z tworzyw sztucznych. Firma posiada siedzibę w Warszawie przy ul. Przemysłowej 15.

**Dane rejestrowe:**
- NIP: 5260016831
- REGON: 012567834
- KRS: 0000145732
- Forma prawna: Spółka z ograniczoną odpowiedzialnością

**Główna działalność (PKD):**
- 22.21.Z - Produkcja płyt, arkuszy, rur i kształtowników z tworzyw sztucznych
- 22.22.Z - Produkcja opakowań z tworzyw sztucznych
- 22.29.Z - Produkcja pozostałych wyrobów z tworzyw sztucznych

Firma zatrudnia około 150 pracowników i posiada nowoczesny park maszynowy o łącznej mocy produkcyjnej 5000 ton rocznie."""
            },
            {
                "id": "section_2",
                "title": "Analiza finansowa",
                "content": """**Przychody i rentowność (2023):**
- Przychody ze sprzedaży: 45,2 mln PLN
- Wzrost r/r: +12,3%
- Marża brutto: 28,5%
- Zysk netto: 4,8 mln PLN

**Wskaźniki finansowe:**
- ROE (Return on Equity): 18,2%
- ROA (Return on Assets): 9,4%
- Wskaźnik płynności bieżącej: 2,1
- Wskaźnik zadłużenia: 32%

**Trend przychodów (mln PLN):**
- 2021: 35,8 mln PLN
- 2022: 40,2 mln PLN
- 2023: 45,2 mln PLN

Firma wykazuje stabilny wzrost przychodów na poziomie 10-15% rocznie. Marża brutto utrzymuje się na poziomie konkurencyjnym dla branży."""
            },
            {
                "id": "section_3",
                "title": "Pozycja rynkowa",
                "content": """**Udział w rynku:**
FADO zajmuje pozycję wśród Top 10 producentów tworzyw sztucznych w Polsce, z szacowanym udziałem w rynku na poziomie 3,5%.

**Główni konkurenci:**
1. Splast S.A. - lider rynku z udziałem 8%
2. PlastPak Sp. z o.o. - 4,2% rynku
3. PolyTech Sp. z o.o. - 3,8% rynku

**Przewagi konkurencyjne:**
- Nowoczesny park maszynowy
- Certyfikaty jakości ISO 9001 i ISO 14001
- Elastyczność w realizacji zamówień
- Własne centrum R&D

**Wyzwania:**
- Rosnące ceny surowców
- Presja regulacyjna na plastik
- Konkurencja ze strony importu z Azji"""
            },
            {
                "id": "section_4",
                "title": "Analiza SWOT",
                "content": """**Mocne strony (Strengths):**
- Doświadczenie 25+ lat na rynku
- Wykwalifikowana kadra
- Nowoczesna infrastruktura
- Certyfikaty jakości
- Stabilna baza klientów

**Słabe strony (Weaknesses):**
- Koncentracja na rynku polskim
- Zależność od kilku głównych dostawców
- Brak własnej sieci dystrybucji

**Szanse (Opportunities):**
- Rozwój rynku opakowań biodegradowalnych
- Ekspansja na rynki CEE
- Rosnący popyt na plastik recyklingowy
- Digitalizacja procesów produkcyjnych

**Zagrożenia (Threats):**
- Regulacje antyplastikowe EU
- Wahania cen ropy naftowej
- Konkurencja z krajów o niższych kosztach pracy
- Spowolnienie gospodarcze"""
            }
        ],
        "sources": [
            {"name": "KRS", "confidence": 0.95, "url": "https://api.krs.pl"},
            {"name": "e-sprawozdania", "confidence": 0.90, "url": "https://ekrs.ms.gov.pl"},
            {"name": "Analiza branżowa PZPTS", "confidence": 0.85, "url": "https://pzpts.pl"}
        ]
    },
    {
        "id": "report_002",
        "title": "Analiza rynku tworzyw sztucznych w Polsce",
        "type": "market_analysis",
        "company": None,
        "created_at": "2026-01-13T09:15:00Z",
        "updated_at": "2026-01-13T16:45:00Z",
        "status": "completed",
        "summary": "Kompleksowa analiza rynku produkcji tworzyw sztucznych w Polsce - trendy, gracze, prognozy.",
        "sections": [
            {
                "id": "section_1",
                "title": "Wielkość i struktura rynku",
                "content": """**Wielkość rynku (2023):**
- Wartość rynku: 12,8 mld PLN
- Wolumen produkcji: 3,2 mln ton
- Liczba przedsiębiorstw: ~2,500
- Zatrudnienie w sektorze: ~45,000 osób

**Struktura rynku według segmentów:**
- Opakowania: 42%
- Budownictwo: 23%
- Motoryzacja: 15%
- AGD i elektronika: 12%
- Pozostałe: 8%

**Dynamika wzrostu:**
Rynek tworzyw sztucznych w Polsce rośnie średnio o 4-6% rocznie. Głównym motorem wzrostu jest sektor opakowaniowy oraz budownictwo."""
            },
            {
                "id": "section_2",
                "title": "Kluczowi gracze",
                "content": """**Top 10 producentów tworzyw sztucznych w Polsce:**

1. **Grupa Azoty Polyolefins** - 15% rynku
   - Lider w produkcji polipropylenu
   - Przychody: ~2 mld PLN

2. **Splast S.A.** - 8% rynku
   - Specjalizacja: opakowania przemysłowe
   - Przychody: ~900 mln PLN

3. **PolyTech Sp. z o.o.** - 5% rynku
   - Komponenty motoryzacyjne
   - Przychody: ~600 mln PLN

4. **PlastPak Sp. z o.o.** - 4,2% rynku
   - Opakowania konsumenckie
   - Przychody: ~500 mln PLN

5. **FADO Sp. z o.o.** - 3,5% rynku
   - Profile i rury
   - Przychody: ~450 mln PLN"""
            }
        ],
        "sources": [
            {"name": "GUS", "confidence": 0.95, "url": "https://stat.gov.pl"},
            {"name": "PZPTS", "confidence": 0.90, "url": "https://pzpts.pl"},
            {"name": "Plastics Europe", "confidence": 0.85, "url": "https://plasticseurope.org"}
        ]
    },
    {
        "id": "report_003",
        "title": "Due Diligence - TechSoft Sp. z o.o.",
        "type": "due_diligence",
        "company": "TechSoft Sp. z o.o.",
        "created_at": "2026-01-12T11:00:00Z",
        "updated_at": "2026-01-12T18:30:00Z",
        "status": "completed",
        "summary": "Raport due diligence dla TechSoft Sp. z o.o. - firmy IT specjalizującej się w rozwoju oprogramowania.",
        "sections": [
            {
                "id": "section_1",
                "title": "Profil firmy",
                "content": """**TechSoft Sp. z o.o.** to polska firma technologiczna założona w 2010 roku, specjalizująca się w rozwoju oprogramowania dla sektora enterprise.

**Dane rejestrowe:**
- NIP: 1234567890
- REGON: 345678901
- KRS: 0000345678
- Siedziba: Warszawa, ul. Marszałkowska 100

**Działalność (PKD):**
- 62.01.Z - Działalność związana z oprogramowaniem
- 62.02.Z - Działalność związana z doradztwem w zakresie informatyki
- 63.11.Z - Przetwarzanie danych; zarządzanie stronami internetowymi

**Zatrudnienie:** 85 osób (w tym 65 programistów)"""
            },
            {
                "id": "section_2",
                "title": "Ocena finansowa",
                "content": """**Przychody i wyniki finansowe:**
- Przychody 2023: 18,5 mln PLN
- Wzrost r/r: +25%
- EBITDA: 3,2 mln PLN
- Marża EBITDA: 17,3%

**Struktura przychodów:**
- Usługi programistyczne: 65%
- Utrzymanie i wsparcie: 25%
- Licencje własnych produktów: 10%

**Cash flow:**
- Operacyjny CF: 2,8 mln PLN
- Free Cash Flow: 1,9 mln PLN

Firma wykazuje zdrową strukturę finansową z rosnącymi przychodami i dodatnimi przepływami pieniężnymi."""
            }
        ],
        "sources": [
            {"name": "KRS", "confidence": 0.95, "url": "https://api.krs.pl"},
            {"name": "LinkedIn", "confidence": 0.75, "url": "https://linkedin.com"},
            {"name": "Strona firmowa", "confidence": 0.80, "url": "https://techsoft.pl"}
        ]
    }
]


class ReportSummary(BaseModel):
    id: str
    title: str
    type: str
    company: Optional[str]
    created_at: str
    status: str
    summary: str


class ReportSection(BaseModel):
    id: str
    title: str
    content: str


class ReportSource(BaseModel):
    name: str
    confidence: float
    url: str


class ReportDetail(BaseModel):
    id: str
    title: str
    type: str
    company: Optional[str]
    created_at: str
    updated_at: str
    status: str
    summary: str
    sections: List[ReportSection]
    sources: List[ReportSource]


@router.get("/")
async def list_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    type: Optional[str] = None,
    search: Optional[str] = None,
    project_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """List user's reports with filtering and pagination."""
    filtered_reports = MOCK_REPORTS

    # Filter by type
    if type:
        filtered_reports = [r for r in filtered_reports if r["type"] == type]

    # Filter by search query
    if search:
        search_lower = search.lower()
        filtered_reports = [
            r for r in filtered_reports
            if search_lower in r["title"].lower()
            or search_lower in r["summary"].lower()
            or (r["company"] and search_lower in r["company"].lower())
        ]

    total = len(filtered_reports)
    start = (page - 1) * limit
    end = start + limit
    items = filtered_reports[start:end]

    return {
        "items": [
            ReportSummary(
                id=r["id"],
                title=r["title"],
                type=r["type"],
                company=r["company"],
                created_at=r["created_at"],
                status=r["status"],
                summary=r["summary"]
            ) for r in items
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


@router.post("/")
async def create_report(current_user: User = Depends(get_current_user)):
    """Create a new report."""
    return {"id": "report_123", "status": "created"}


@router.get("/{report_id}")
async def get_report(report_id: str, current_user: User = Depends(get_current_user)):
    """Get report details."""
    for report in MOCK_REPORTS:
        if report["id"] == report_id:
            return ReportDetail(
                id=report["id"],
                title=report["title"],
                type=report["type"],
                company=report["company"],
                created_at=report["created_at"],
                updated_at=report["updated_at"],
                status=report["status"],
                summary=report["summary"],
                sections=[ReportSection(**s) for s in report["sections"]],
                sources=[ReportSource(**s) for s in report["sources"]]
            )

    return {"error": "Report not found"}


@router.put("/{report_id}")
async def update_report(report_id: str):
    """Update report content."""
    # TODO: Implement report update
    return {"message": "Report updated successfully"}


@router.delete("/{report_id}")
async def delete_report(report_id: str):
    """Delete a report."""
    # TODO: Implement report deletion
    return {"message": "Report deleted successfully"}


@router.post("/{report_id}/export")
async def export_report(report_id: str, format: str = "pdf"):
    """Export report to specified format."""
    # TODO: Implement report export
    return {"download_url": f"/exports/report_{report_id}.{format}"}


@router.post("/{report_id}/share")
async def share_report(report_id: str):
    """Generate share link for report."""
    # TODO: Implement report sharing
    return {
        "share_url": f"https://app.minavigator.com/share/{report_id}",
        "expires_at": "2024-02-01T00:00:00Z"
    }


# In-memory annotation storage (per user, per report)
REPORT_ANNOTATIONS: dict = {}


class AnnotationCreate(BaseModel):
    section_id: str
    selected_text: str
    start_offset: int
    end_offset: int
    comment: str


class Annotation(BaseModel):
    id: str
    report_id: str
    section_id: str
    selected_text: str
    start_offset: int
    end_offset: int
    comment: str
    created_at: str
    user_id: str


@router.get("/{report_id}/annotations")
async def get_annotations(report_id: str, current_user: User = Depends(get_current_user)):
    """Get all annotations for a report."""
    user_key = f"{current_user.id}:{report_id}"
    annotations = REPORT_ANNOTATIONS.get(user_key, [])
    return {"annotations": annotations}


@router.post("/{report_id}/annotations")
async def create_annotation(
    report_id: str,
    annotation: AnnotationCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new annotation for a report."""
    user_key = f"{current_user.id}:{report_id}"

    if user_key not in REPORT_ANNOTATIONS:
        REPORT_ANNOTATIONS[user_key] = []

    # Generate unique ID
    annotation_id = f"ann_{len(REPORT_ANNOTATIONS[user_key]) + 1}_{int(datetime.now().timestamp())}"

    new_annotation = Annotation(
        id=annotation_id,
        report_id=report_id,
        section_id=annotation.section_id,
        selected_text=annotation.selected_text,
        start_offset=annotation.start_offset,
        end_offset=annotation.end_offset,
        comment=annotation.comment,
        created_at=datetime.now().isoformat() + "Z",
        user_id=str(current_user.id)
    )

    REPORT_ANNOTATIONS[user_key].append(new_annotation.model_dump())

    return new_annotation


@router.delete("/{report_id}/annotations/{annotation_id}")
async def delete_annotation(
    report_id: str,
    annotation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an annotation."""
    user_key = f"{current_user.id}:{report_id}"

    if user_key not in REPORT_ANNOTATIONS:
        return {"error": "Annotation not found"}

    annotations = REPORT_ANNOTATIONS[user_key]
    REPORT_ANNOTATIONS[user_key] = [a for a in annotations if a["id"] != annotation_id]

    return {"message": "Annotation deleted successfully"}


# Version history mock data
REPORT_VERSIONS = {
    "report_001": [
        {
            "version": 3,
            "created_at": "2026-01-14T14:22:00Z",
            "author": "Jan Kowalski",
            "changes": "Dodano sekcje Analiza SWOT",
            "is_current": True
        },
        {
            "version": 2,
            "created_at": "2026-01-14T12:15:00Z",
            "author": "Jan Kowalski",
            "changes": "Zaktualizowano dane finansowe",
            "is_current": False,
            "sections": [
                {
                    "id": "section_1",
                    "title": "Informacje podstawowe",
                    "content": """FADO Sp. z o.o. to polska firma założona w 1998 roku, specjalizująca się w produkcji wyrobów z tworzyw sztucznych. Firma posiada siedzibę w Warszawie przy ul. Przemysłowej 15.

**Dane rejestrowe:**
- NIP: 5260016831
- REGON: 012567834
- KRS: 0000145732
- Forma prawna: Spółka z ograniczoną odpowiedzialnością

Firma zatrudnia około 120 pracowników."""
                },
                {
                    "id": "section_2",
                    "title": "Analiza finansowa",
                    "content": """**Przychody i rentowność (2022):**
- Przychody ze sprzedaży: 40,2 mln PLN
- Wzrost r/r: +8,5%
- Marża brutto: 26,2%
- Zysk netto: 3,9 mln PLN

Firma wykazuje stabilny wzrost przychodów."""
                }
            ]
        },
        {
            "version": 1,
            "created_at": "2026-01-13T09:30:00Z",
            "author": "System",
            "changes": "Utworzono raport",
            "is_current": False,
            "sections": [
                {
                    "id": "section_1",
                    "title": "Informacje podstawowe",
                    "content": """FADO Sp. z o.o. to polska firma założona w 1998 roku.

**Dane rejestrowe:**
- NIP: 5260016831
- REGON: 012567834
- KRS: 0000145732

Wstępne dane firmy."""
                }
            ]
        }
    ],
    "report_002": [
        {
            "version": 1,
            "created_at": "2026-01-13T09:15:00Z",
            "author": "System",
            "changes": "Utworzono raport",
            "is_current": True
        }
    ],
    "report_003": [
        {
            "version": 1,
            "created_at": "2026-01-12T11:00:00Z",
            "author": "System",
            "changes": "Utworzono raport",
            "is_current": True
        }
    ]
}


class ReportVersion(BaseModel):
    version: int
    created_at: str
    author: str
    changes: str
    is_current: bool


class ReportVersionDetail(BaseModel):
    version: int
    created_at: str
    author: str
    changes: str
    is_current: bool
    sections: Optional[List[ReportSection]] = None


@router.get("/{report_id}/versions")
async def get_report_versions(report_id: str, current_user: User = Depends(get_current_user)):
    """Get version history for a report."""
    versions = REPORT_VERSIONS.get(report_id, [])
    return {
        "versions": [
            ReportVersion(
                version=v["version"],
                created_at=v["created_at"],
                author=v["author"],
                changes=v["changes"],
                is_current=v["is_current"]
            ) for v in versions
        ]
    }


@router.get("/{report_id}/versions/{version}")
async def get_report_version(
    report_id: str,
    version: int,
    current_user: User = Depends(get_current_user)
):
    """Get a specific version of a report."""
    versions = REPORT_VERSIONS.get(report_id, [])

    for v in versions:
        if v["version"] == version:
            # If it's the current version, return the main report
            if v["is_current"]:
                for report in MOCK_REPORTS:
                    if report["id"] == report_id:
                        return ReportDetail(
                            id=report["id"],
                            title=report["title"] + f" (wersja {version})",
                            type=report["type"],
                            company=report["company"],
                            created_at=v["created_at"],
                            updated_at=v["created_at"],
                            status=report["status"],
                            summary=report["summary"],
                            sections=[ReportSection(**s) for s in report["sections"]],
                            sources=[ReportSource(**s) for s in report["sources"]]
                        )
            else:
                # Return the historical version
                for report in MOCK_REPORTS:
                    if report["id"] == report_id:
                        return ReportDetail(
                            id=report["id"],
                            title=report["title"] + f" (wersja {version})",
                            type=report["type"],
                            company=report["company"],
                            created_at=v["created_at"],
                            updated_at=v["created_at"],
                            status="archived",
                            summary=report["summary"],
                            sections=[ReportSection(**s) for s in v.get("sections", [])],
                            sources=[ReportSource(**s) for s in report["sources"]]
                        )

    return {"error": "Version not found"}


class RestoreVersionRequest(BaseModel):
    version: int


@router.post("/{report_id}/versions/restore")
async def restore_report_version(
    report_id: str,
    request: RestoreVersionRequest,
    current_user: User = Depends(get_current_user)
):
    """Restore a report to a previous version.

    This creates a new version with the content from the specified historical version.
    """
    versions = REPORT_VERSIONS.get(report_id, [])

    if not versions:
        return {"error": "Report not found"}

    # Find the version to restore
    version_to_restore = None
    for v in versions:
        if v["version"] == request.version:
            version_to_restore = v
            break

    if not version_to_restore:
        return {"error": "Version not found"}

    # Get the current max version
    max_version = max(v["version"] for v in versions)

    # Mark all versions as not current
    for v in versions:
        v["is_current"] = False

    # Create new version with restored content
    new_version = {
        "version": max_version + 1,
        "created_at": datetime.now().isoformat() + "Z",
        "author": current_user.name or current_user.email,
        "changes": f"Przywrócono wersję {request.version}",
        "is_current": True,
    }

    # Copy sections from the restored version if it has them
    if "sections" in version_to_restore:
        new_version["sections"] = version_to_restore["sections"].copy()

    # Add the new version at the beginning (most recent first)
    REPORT_VERSIONS[report_id].insert(0, new_version)

    return {
        "message": "Wersja przywrócona pomyślnie",
        "new_version": new_version["version"],
        "restored_from": request.version
    }
