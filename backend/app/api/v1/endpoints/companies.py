"""
Companies API Endpoints
"""

from fastapi import APIRouter, Query, Depends
from typing import Optional, List
from pydantic import BaseModel

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()


# PKD Codes Database (Polish Classification of Activities)
PKD_CODES = {
    "01.11.Z": {"name": "Uprawa zbóż, roślin strączkowych i roślin oleistych na nasiona", "category": "Rolnictwo"},
    "10.71.Z": {"name": "Produkcja pieczywa i wyrobów cukierniczych", "category": "Produkcja"},
    "22.21.Z": {"name": "Produkcja płyt, arkuszy, rur i kształtowników z tworzyw sztucznych", "category": "Produkcja"},
    "22.22.Z": {"name": "Produkcja opakowań z tworzyw sztucznych", "category": "Produkcja"},
    "22.29.Z": {"name": "Produkcja pozostałych wyrobów z tworzyw sztucznych", "category": "Produkcja"},
    "25.62.Z": {"name": "Obróbka mechaniczna elementów metalowych", "category": "Produkcja"},
    "25.73.Z": {"name": "Produkcja narzędzi", "category": "Produkcja"},
    "28.22.Z": {"name": "Produkcja urządzeń dźwigowych i chwytaków", "category": "Produkcja"},
    "28.29.Z": {"name": "Produkcja pozostałych maszyn ogólnego przeznaczenia", "category": "Produkcja"},
    "41.20.Z": {"name": "Roboty budowlane związane ze wznoszeniem budynków", "category": "Budownictwo"},
    "46.71.Z": {"name": "Sprzedaż hurtowa paliw i produktów pochodnych", "category": "Handel"},
    "46.73.Z": {"name": "Sprzedaż hurtowa drewna i materiałów budowlanych", "category": "Handel"},
    "47.11.Z": {"name": "Sprzedaż detaliczna w niewyspecjalizowanych sklepach", "category": "Handel"},
    "49.41.Z": {"name": "Transport drogowy towarów", "category": "Transport"},
    "52.10.B": {"name": "Magazynowanie i przechowywanie pozostałych towarów", "category": "Logistyka"},
    "52.29.C": {"name": "Działalność pozostałych agencji transportowych", "category": "Logistyka"},
    "62.01.Z": {"name": "Działalność związana z oprogramowaniem", "category": "IT"},
    "62.02.Z": {"name": "Działalność związana z doradztwem w zakresie informatyki", "category": "IT"},
    "62.03.Z": {"name": "Działalność związana z zarządzaniem urządzeniami informatycznymi", "category": "IT"},
    "62.09.Z": {"name": "Pozostała działalność usługowa w zakresie technologii informatycznych", "category": "IT"},
    "63.11.Z": {"name": "Przetwarzanie danych; zarządzanie stronami internetowymi", "category": "IT"},
    "69.10.Z": {"name": "Działalność prawnicza", "category": "Usługi profesjonalne"},
    "69.20.Z": {"name": "Działalność rachunkowo-księgowa; doradztwo podatkowe", "category": "Usługi profesjonalne"},
    "70.22.Z": {"name": "Pozostałe doradztwo w zakresie prowadzenia działalności gospodarczej", "category": "Usługi profesjonalne"},
    "71.12.Z": {"name": "Działalność w zakresie inżynierii i związane z nią doradztwo techniczne", "category": "Usługi profesjonalne"},
    "73.11.Z": {"name": "Działalność agencji reklamowych", "category": "Marketing"},
    "82.99.Z": {"name": "Pozostała działalność wspomagająca prowadzenie działalności gospodarczej", "category": "Usługi"},
}


# Mock company database
MOCK_COMPANIES = [
    {
        "id": "1",
        "name": "FADO Sp. z o.o.",
        "nip": "5260016831",
        "krs": "0000145732",
        "regon": "012567834",
        "address": {"city": "Warszawa", "street": "ul. Przemysłowa 15", "postal_code": "00-001"},
        "pkd_codes": ["22.21.Z", "22.22.Z", "22.29.Z"],
        "status": "active",
        "founded": "1998",
    },
    {
        "id": "2",
        "name": "Splast S.A.",
        "nip": "6781234567",
        "krs": "0000234567",
        "regon": "234567890",
        "address": {"city": "Kraków", "street": "ul. Fabryczna 42", "postal_code": "30-001"},
        "pkd_codes": ["22.21.Z", "22.29.Z"],
        "status": "active",
        "founded": "2005",
    },
    {
        "id": "3",
        "name": "TechSoft Sp. z o.o.",
        "nip": "1234567890",
        "krs": "0000345678",
        "regon": "345678901",
        "address": {"city": "Warszawa", "street": "ul. Marszałkowska 100", "postal_code": "00-002"},
        "pkd_codes": ["62.01.Z", "62.02.Z", "63.11.Z"],
        "status": "active",
        "founded": "2010",
    },
    {
        "id": "4",
        "name": "LogiTrans S.A.",
        "nip": "9876543210",
        "krs": "0000456789",
        "regon": "456789012",
        "address": {"city": "Gdańsk", "street": "ul. Portowa 8", "postal_code": "80-001"},
        "pkd_codes": ["49.41.Z", "52.10.B", "52.29.C"],
        "status": "active",
        "founded": "2003",
    },
    {
        "id": "5",
        "name": "MetalPro Sp. z o.o.",
        "nip": "1122334455",
        "krs": "0000567890",
        "regon": "567890123",
        "address": {"city": "Katowice", "street": "ul. Stalowa 25", "postal_code": "40-001"},
        "pkd_codes": ["25.62.Z", "25.73.Z", "28.29.Z"],
        "status": "active",
        "founded": "2008",
    },
    {
        "id": "6",
        "name": "ConsultPro Sp. z o.o.",
        "nip": "5566778899",
        "krs": "0000678901",
        "regon": "678901234",
        "address": {"city": "Poznań", "street": "ul. Biznesowa 12", "postal_code": "60-001"},
        "pkd_codes": ["69.20.Z", "70.22.Z"],
        "status": "active",
        "founded": "2015",
    },
    {
        "id": "7",
        "name": "PlastPak Sp. z o.o.",
        "nip": "9988776655",
        "krs": "0000789012",
        "regon": "789012345",
        "address": {"city": "Łódź", "street": "ul. Produkcyjna 33", "postal_code": "90-001"},
        "pkd_codes": ["22.22.Z", "22.29.Z"],
        "status": "active",
        "founded": "2012",
    },
]


class CompanySearchResult(BaseModel):
    id: str
    name: str
    nip: str
    address: dict
    pkd_codes: List[str]
    pkd_descriptions: List[dict]
    status: str


class PKDSearchResponse(BaseModel):
    pkd_code: str
    pkd_description: str
    pkd_category: str
    companies: List[CompanySearchResult]
    total_count: int


@router.get("/search")
async def search_companies(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50)
):
    """Search companies by name, NIP, or KRS."""
    q_lower = q.lower()
    results = []

    for company in MOCK_COMPANIES:
        if (q_lower in company["name"].lower() or
            q in company["nip"] or
            q in company.get("krs", "")):
            pkd_descriptions = []
            for pkd in company["pkd_codes"]:
                if pkd in PKD_CODES:
                    pkd_descriptions.append({
                        "code": pkd,
                        "name": PKD_CODES[pkd]["name"],
                        "category": PKD_CODES[pkd]["category"]
                    })
            results.append(CompanySearchResult(
                id=company["id"],
                name=company["name"],
                nip=company["nip"],
                address=company["address"],
                pkd_codes=company["pkd_codes"],
                pkd_descriptions=pkd_descriptions,
                status=company["status"]
            ))

    return {"results": results[:limit], "total": len(results)}


@router.get("/search/pkd", response_model=PKDSearchResponse)
async def search_by_pkd(
    code: str = Query(..., min_length=4, description="PKD code (e.g., 22.21.Z)"),
    current_user: User = Depends(get_current_user)
):
    """
    Search companies by PKD code.
    Returns all companies with the specified PKD code along with PKD description.
    """
    # Normalize PKD code
    pkd_code = code.upper().strip()

    # Get PKD description
    if pkd_code not in PKD_CODES:
        # Try partial match
        matching_codes = [k for k in PKD_CODES.keys() if k.startswith(pkd_code[:2])]
        if matching_codes:
            pkd_code = matching_codes[0]
        else:
            return PKDSearchResponse(
                pkd_code=code,
                pkd_description="Nieznany kod PKD",
                pkd_category="Nieznana",
                companies=[],
                total_count=0
            )

    pkd_info = PKD_CODES[pkd_code]

    # Find companies with this PKD code
    results = []
    for company in MOCK_COMPANIES:
        if pkd_code in company["pkd_codes"]:
            pkd_descriptions = []
            for pkd in company["pkd_codes"]:
                if pkd in PKD_CODES:
                    pkd_descriptions.append({
                        "code": pkd,
                        "name": PKD_CODES[pkd]["name"],
                        "category": PKD_CODES[pkd]["category"]
                    })
            results.append(CompanySearchResult(
                id=company["id"],
                name=company["name"],
                nip=company["nip"],
                address=company["address"],
                pkd_codes=company["pkd_codes"],
                pkd_descriptions=pkd_descriptions,
                status=company["status"]
            ))

    return PKDSearchResponse(
        pkd_code=pkd_code,
        pkd_description=pkd_info["name"],
        pkd_category=pkd_info["category"],
        companies=results,
        total_count=len(results)
    )


@router.get("/pkd-codes")
async def list_pkd_codes(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in PKD names")
):
    """List available PKD codes with optional filtering."""
    results = []
    for code, info in PKD_CODES.items():
        if category and info["category"].lower() != category.lower():
            continue
        if search and search.lower() not in info["name"].lower():
            continue
        results.append({
            "code": code,
            "name": info["name"],
            "category": info["category"]
        })
    return {"pkd_codes": results, "total": len(results)}


@router.get("/{identifier}")
async def get_company(identifier: str):
    """Get company profile by NIP, KRS, or internal ID."""
    # TODO: Implement company profile retrieval
    return {
        "id": identifier,
        "name": "Company Name",
        "nip": "1234567890",
        "krs": "0000123456",
        "address": "Warsaw, Poland",
        "pkd_codes": []
    }


@router.get("/{identifier}/financials")
async def get_company_financials(identifier: str):
    """Get company financial data."""
    # TODO: Implement financial data retrieval
    return {
        "company_id": identifier,
        "statements": [],
        "ratios": {}
    }


@router.get("/{identifier}/ownership")
async def get_company_ownership(identifier: str):
    """Get company ownership structure."""
    # TODO: Implement ownership mapping
    return {
        "company_id": identifier,
        "shareholders": [],
        "beneficial_owners": []
    }


@router.get("/{identifier}/people")
async def get_company_people(identifier: str):
    """Get company key people."""
    # TODO: Implement key people retrieval
    return {
        "company_id": identifier,
        "management_board": [],
        "supervisory_board": []
    }


@router.get("/{identifier}/competitors")
async def get_company_competitors(identifier: str):
    """Get company competitors."""
    # TODO: Implement competitor mapping
    return {
        "company_id": identifier,
        "competitors": []
    }


@router.get("/{identifier}/news")
async def get_company_news(identifier: str):
    """Get news about company."""
    # TODO: Implement news aggregation
    return {
        "company_id": identifier,
        "news": []
    }
