"""
Chat API Endpoints
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, get_current_user_optional
from app.models.user import User
from app.services.auth import AuthService
from app.core.usage_limits import check_usage_limit

router = APIRouter()


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: str
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime


class ConversationResponse(BaseModel):
    id: str
    title: Optional[str] = None
    messages: List[MessageResponse] = []
    created_at: datetime
    updated_at: datetime


# In-memory storage for demo (will be replaced with database)
conversations_store = {}


@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(current_user: Optional[User] = Depends(get_current_user_optional)):
    """List user's chat conversations."""
    # Dev mode: use mock user if not authenticated
    user_id = str(current_user.id) if current_user else "dev_user_123"
    user_convs = [c for c in conversations_store.values() if c.get("user_id") == user_id]
    return [ConversationResponse(**{k: v for k, v in c.items() if k != "user_id"}) for c in user_convs]


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(current_user: Optional[User] = Depends(get_current_user_optional)):
    """Create a new chat conversation."""
    # Dev mode: use mock user if not authenticated
    user_id = str(current_user.id) if current_user else "dev_user_123"

    conv_id = str(uuid.uuid4())
    now = datetime.utcnow()
    conversation = {
        "id": conv_id,
        "user_id": user_id,
        "title": None,
        "messages": [],
        "created_at": now,
        "updated_at": now
    }
    conversations_store[conv_id] = conversation
    return ConversationResponse(**{k: v for k, v in conversation.items() if k != "user_id"})


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str, current_user: Optional[User] = Depends(get_current_user_optional)):
    """Get conversation details with messages."""
    # Dev mode: use mock user if not authenticated
    user_id = str(current_user.id) if current_user else "dev_user_123"

    conv = conversations_store.get(conversation_id)
    if not conv or conv.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationResponse(**{k: v for k, v in conv.items() if k != "user_id"})


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    message: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Send a message in conversation and get AI response."""
    # Check usage limit if user is authenticated
    if current_user:
        await check_usage_limit(db, current_user, action_type="chat")

    # Dev mode: use mock user if not authenticated
    user_id = str(current_user.id) if current_user else "dev_user_123"

    conv = conversations_store.get(conversation_id)
    if not conv or conv.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Add user message
    user_msg_id = str(uuid.uuid4())
    now = datetime.utcnow()
    user_message = {
        "id": user_msg_id,
        "role": "user",
        "content": message.content,
        "created_at": now
    }
    conv["messages"].append(user_message)
    conv["updated_at"] = now

    # Update conversation title if first message
    if conv["title"] is None and len(conv["messages"]) == 1:
        conv["title"] = message.content[:50] + ("..." if len(message.content) > 50 else "")

    # Generate AI response (mock for now)
    ai_msg_id = str(uuid.uuid4())
    ai_response = generate_mock_response(message.content)
    ai_message = {
        "id": ai_msg_id,
        "role": "assistant",
        "content": ai_response,
        "created_at": datetime.utcnow()
    }
    conv["messages"].append(ai_message)

    return MessageResponse(**ai_message)


def get_industry_context(industry: str, industry_segment: str = None) -> dict:
    """Get industry-specific context for prompt customization."""
    if industry == "manufacturing" or industry_segment == "plastics_processing":
        return {
            "terminology": ["injection molding", "extrusion", "blow molding", "polymer processing", "tooling", "cycle time"],
            "key_fields": ["machinery_type", "certifications", "production_capacity_tons", "mold_count", "material_types"],
            "metrics": ["cycle_time_efficiency", "scrap_rate", "oee", "capacity_utilization", "tool_changeover_time"],
            "certifications": ["ISO 9001", "ISO 14001", "IATF 16949", "ISO 13485"],
            "competitors_indicators": ["production volume", "mold complexity", "material specialization"]
        }
    elif industry == "technology":
        return {
            "terminology": ["SaaS", "API", "cloud infrastructure", "scalability", "tech stack"],
            "key_fields": ["technology_stack", "hosting_provider", "api_endpoints", "security_certifications"],
            "metrics": ["uptime", "response_time", "api_calls_per_day", "active_users"],
            "certifications": ["ISO 27001", "SOC 2", "GDPR compliance"],
            "competitors_indicators": ["user base", "feature set", "pricing model"]
        }
    else:
        return {
            "terminology": [],
            "key_fields": [],
            "metrics": [],
            "certifications": [],
            "competitors_indicators": []
        }


def generate_mock_response(user_message: str, user_industry: str = None, user_industry_segment: str = None) -> str:
    """Generate a mock AI response based on user message and user's industry context."""
    import json
    import re
    from datetime import datetime, timedelta
    user_lower = user_message.lower()

    # Company lookup by NIP or KRS (from frontend detection)
    if "lookup company" in user_lower:
        # Extract NIP or KRS number from message
        # Format: "Lookup company with NIP: 5260016831" or "Lookup company with KRS: 0000145732"
        nip_match = re.search(r'nip:\s*(\d{10})', user_message, re.IGNORECASE)
        krs_match = re.search(r'krs:\s*(\d{10})', user_message, re.IGNORECASE)

        identifier = None
        lookup_type = None

        if nip_match:
            identifier = nip_match.group(1)
            lookup_type = "NIP"
        elif krs_match:
            identifier = krs_match.group(1)
            lookup_type = "KRS"

        if identifier:
            # Fetch real company data from /companies endpoint
            from app.api.v1.endpoints.companies import MOCK_COMPANIES, MOCK_CEIDG_COMPANIES, PKD_CODES

            company = None
            is_ceidg = False

            # First check KRS companies
            for c in MOCK_COMPANIES:
                if (c["nip"] == identifier or c.get("krs", "") == identifier):
                    company = c
                    break

            # If not found in KRS, check CEIDG
            if not company:
                for c in MOCK_CEIDG_COMPANIES:
                    if c["nip"] == identifier:
                        company = c
                        is_ceidg = True
                        break

            if company and is_ceidg:
                # Build PKD descriptions for CEIDG
                pkd_descriptions = []
                for pkd in company["pkd_codes"]:
                    if pkd in PKD_CODES:
                        pkd_descriptions.append({
                            "code": pkd,
                            "name": PKD_CODES[pkd]["name"],
                            "category": PKD_CODES[pkd]["category"]
                        })

                # Format address for CEIDG
                address = company["address"]
                address_str = f"{address.get('street', '')}, {address.get('postal_code', '')} {address.get('city', '')}"

                # Return structured company profile with CEIDG data
                return json.dumps({
                    "type": "company_profile_ceidg",
                    "data": {
                        "lookup_type": lookup_type,
                        "identifier": identifier,
                        "basic_info": {
                            "business_name": company["business_name"],
                            "owner_name": company["owner_name"],
                            "nip": company["nip"],
                            "regon": company.get("regon", ""),
                            "address": address_str,
                            "status": company["status"],
                            "founded": company.get("founded", "N/A")
                        },
                        "pkd_codes": pkd_descriptions,
                        "source": "CEIDG API",
                        "fetched_at": datetime.utcnow().isoformat()
                    }
                }, ensure_ascii=False)
            elif company:
                # Build PKD descriptions for KRS
                pkd_descriptions = []
                for pkd in company["pkd_codes"]:
                    if pkd in PKD_CODES:
                        pkd_descriptions.append({
                            "code": pkd,
                            "name": PKD_CODES[pkd]["name"],
                            "category": PKD_CODES[pkd]["category"]
                        })

                # Format address for KRS
                address = company["address"]
                address_str = f"{address.get('street', '')}, {address.get('postal_code', '')} {address.get('city', '')}"

                # Return structured company profile with KRS data
                return json.dumps({
                    "type": "company_profile_krs",
                    "data": {
                        "lookup_type": lookup_type,
                        "identifier": identifier,
                        "basic_info": {
                            "name": company["name"],
                            "nip": company["nip"],
                            "krs": company.get("krs", ""),
                            "regon": company.get("regon", ""),
                            "address": address_str,
                            "status": company["status"],
                            "founded": company.get("founded", "N/A")
                        },
                        "pkd_codes": pkd_descriptions,
                        "source": "KRS API",
                        "fetched_at": datetime.utcnow().isoformat()
                    }
                }, ensure_ascii=False)
            else:
                # Company not found
                return json.dumps({
                    "type": "error",
                    "data": {
                        "message": f"Nie znaleziono firmy z {lookup_type}: {identifier}",
                        "suggestion": "Sprawdź poprawność numeru lub spróbuj wyszukać po nazwie firmy."
                    }
                }, ensure_ascii=False)

    # Website analysis - detect URLs (HIGH PRIORITY - check before other conditions)
    if re.search(r'https?://[^\s]+', user_message):
        # Extract URL from message
        url_match = re.search(r'(https?://[^\s]+)', user_message)
        url = url_match.group(1) if url_match else ""

        # Generate mock website analysis data with deep crawl
        return json.dumps({
            "type": "website_analysis",
            "data": {
                "url": url,
                "basic_info": {
                    "title": "FADO Sp. z o.o. - Producent tworzyw sztucznych",
                    "description": "Lider w produkcji tworzyw sztucznych w Polsce. Specjalizujemy się w produkcji części z tworzyw sztucznych dla przemysłu motoryzacyjnego i elektronicznego.",
                    "language": "pl",
                    "status": "active",
                    "ssl_enabled": True,
                    "mobile_friendly": True
                },
                "contact_info": {
                    "email": "kontakt@fado.com.pl",
                    "phone": "+48 42 123 45 67",
                    "address": "ul. Przemysłowa 15, 95-200 Pabianice",
                    "company_name": "FADO Sp. z o.o.",
                    "nip": "5260016831"
                },
                "social_media": {
                    "facebook": "https://facebook.com/fado.pl",
                    "linkedin": "https://linkedin.com/company/fado",
                    "twitter": None,
                    "instagram": None,
                    "youtube": "https://youtube.com/@fadopl"
                },
                "tech_stack": {
                    "cms": "WordPress 6.4",
                    "analytics": ["Google Analytics", "Google Tag Manager"],
                    "hosting": "nazwa.pl",
                    "frameworks": ["React", "TailwindCSS"]
                },
                "content_summary": {
                    "page_count": 15,
                    "has_blog": True,
                    "has_products": True,
                    "has_team": True,
                    "has_contact_form": True,
                    "last_updated": "2026-01-15"
                },
                "site_structure": {
                    "pages_crawled": [
                        {
                            "url": f"{url}",
                            "title": "Strona główna - FADO",
                            "type": "homepage",
                            "word_count": 850,
                            "last_modified": "2026-01-15"
                        },
                        {
                            "url": f"{url}/produkty",
                            "title": "Nasze produkty - FADO",
                            "type": "products",
                            "word_count": 1200,
                            "last_modified": "2026-01-10"
                        },
                        {
                            "url": f"{url}/o-nas",
                            "title": "O firmie - FADO",
                            "type": "about",
                            "word_count": 650,
                            "last_modified": "2025-12-20"
                        },
                        {
                            "url": f"{url}/zespol",
                            "title": "Nasz zespół - FADO",
                            "type": "team",
                            "word_count": 480,
                            "last_modified": "2025-11-15"
                        },
                        {
                            "url": f"{url}/blog",
                            "title": "Blog - FADO",
                            "type": "blog",
                            "word_count": 320,
                            "last_modified": "2026-01-12"
                        },
                        {
                            "url": f"{url}/kontakt",
                            "title": "Kontakt - FADO",
                            "type": "contact",
                            "word_count": 280,
                            "last_modified": "2025-10-05"
                        }
                    ],
                    "depth_reached": 2,
                    "total_links": 45
                },
                "products_services": [
                    {
                        "name": "Wtrysk form plastikowych",
                        "category": "Usługa produkcyjna",
                        "description": "Wtrysk precision parts z tworzyw sztucznych dla przemysłu motoryzacyjnego. Maksymalna waga detalu: 500g.",
                        "page_url": f"{url}/produkty/wtrysk-form"
                    },
                    {
                        "name": "Formy wtryskowe na zamówienie",
                        "category": "Produkt",
                        "description": "Projektowanie i wykonanie form wtryskowych. Średni czas realizacji: 4-6 tygodni.",
                        "page_url": f"{url}/produkty/formy-wtryskowe"
                    },
                    {
                        "name": "Opakowania z tworzyw sztucznych",
                        "category": "Produkt",
                        "description": "Produkcja opakowań przemysłowych i konsumenckich. Dostępne materiały: PP, PE, PET.",
                        "page_url": f"{url}/produkty/opakowania"
                    },
                    {
                        "name": "Recykling tworzyw sztucznych",
                        "category": "Usługa",
                        "description": "Przetwarzanie odpadów plastikowych i produkcja granulatu z materiałów wtórnych.",
                        "page_url": f"{url}/produkty/recykling"
                    }
                ],
                "team_members": [
                    {
                        "name": "Jan Kowalski",
                        "position": "Prezes Zarządu",
                        "bio": "25 lat doświadczenia w branży tworzyw sztucznych. Założyciel FADO.",
                        "photo_url": f"{url}/images/team/jan-kowalski.jpg"
                    },
                    {
                        "name": "Anna Nowak",
                        "position": "Dyrektor Techniczny",
                        "bio": "Specjalistka w zakresie technologii wtryskarskich. Doktorat z inżynierii materiałowej.",
                        "photo_url": f"{url}/images/team/anna-nowak.jpg"
                    },
                    {
                        "name": "Piotr Wiśniewski",
                        "position": "Kierownik Produkcji",
                        "bio": "15 lat w zarządzaniu procesami produkcyjnymi. Certyfikat Six Sigma Black Belt.",
                        "photo_url": f"{url}/images/team/piotr-wisniewski.jpg"
                    },
                    {
                        "name": "Maria Kowalczyk",
                        "position": "Kierownik Działu Sprzedaży",
                        "bio": "Ekspert w obszarze B2B sales. Rozwinęła partnerstwa z 50+ kluczowymi klientami.",
                        "photo_url": f"{url}/images/team/maria-kowalczyk.jpg"
                    }
                ],
                "blog_posts": [
                    {
                        "title": "Nowe technologie w recyklingu tworzyw sztucznych",
                        "url": f"{url}/blog/nowe-technologie-recykling",
                        "published_date": "2026-01-12",
                        "excerpt": "Poznaj najnowsze metody przetwarzania odpadów plastikowych i ich wpływ na środowisko. Nasze centrum R&D wprowadziło innowacyjny proces...",
                        "category": "Technologia"
                    },
                    {
                        "title": "FADO otrzymało certyfikat ISO 14001",
                        "url": f"{url}/blog/certyfikat-iso-14001",
                        "published_date": "2026-01-05",
                        "excerpt": "Z dumą ogłaszamy, że nasza firma uzyskała certyfikat zarządzania środowiskowego ISO 14001:2015. To potwierdzenie naszego zaangażowania...",
                        "category": "Aktualności"
                    },
                    {
                        "title": "Jak wybrać odpowiedni materiał do wtrysku?",
                        "url": f"{url}/blog/wybor-materialu-wtrysk",
                        "published_date": "2025-12-28",
                        "excerpt": "Przewodnik po popularnych tworzywach sztucznych stosowanych we wtryskiwaniu: PP, PE, ABS, PC. Poznaj właściwości i zastosowania...",
                        "category": "Poradnik"
                    },
                    {
                        "title": "Rozbudowa parku maszynowego w FADO",
                        "url": f"{url}/blog/rozbudowa-park-maszynowy",
                        "published_date": "2025-12-15",
                        "excerpt": "Inwestycja w 3 nowe wtryskarki o sile zamykania do 500 ton. Zwiększenie mocy produkcyjnej o 30%...",
                        "category": "Aktualności"
                    }
                ],
                "crawled_at": datetime.utcnow().isoformat(),
                "crawl_status": "success"
            }
        }, ensure_ascii=False)

    # BUGFIX Session 364 (Feature #57): Moved key_people check BEFORE company_profile
    # to prevent "company profile with key people" from matching company_profile first
    # Key people / management request
    elif ("kluczowe osoby" in user_lower or "key people" in user_lower or "zarząd" in user_lower or
          "management" in user_lower or "kierownictwo" in user_lower or "rada nadzorcza" in user_lower or
          "supervisory board" in user_lower or "board of directors" in user_lower or
          "członkowie zarządu" in user_lower or "management board" in user_lower):
        return json.dumps({
            "type": "key_people",
            "data": {
                "company_name": "FADO Sp. z o.o.",
                "nip": "5260016831",
                "krs": "0000145732",
                "source": "KRS",
                "management_board": [
                    {
                        "name": "Jan Kowalski",
                        "role": "Prezes Zarządu",
                        "role_en": "CEO / President of the Board",
                        "since": "1995-03-15",
                        "tenure_years": 29,
                        "other_positions": [
                            {
                                "company": "FADO Automotive Sp. z o.o.",
                                "role": "Prezes Zarządu",
                                "since": "2010-01-10"
                            },
                            {
                                "company": "Stowarzyszenie Producentów Tworzyw",
                                "role": "Członek Zarządu",
                                "since": "2015-05-20"
                            }
                        ],
                        "linkedin": "https://linkedin.com/in/jan-kowalski-fado",
                        "photo": None
                    },
                    {
                        "name": "Anna Nowak",
                        "role": "Wiceprezes Zarządu",
                        "role_en": "Vice President / Deputy CEO",
                        "since": "2005-11-10",
                        "tenure_years": 19,
                        "other_positions": [
                            {
                                "company": "Plastics Innovation Sp. z o.o.",
                                "role": "Członek Rady Nadzorczej",
                                "since": "2012-03-15"
                            }
                        ],
                        "linkedin": "https://linkedin.com/in/anna-nowak-fado",
                        "photo": None
                    },
                    {
                        "name": "Piotr Wiśniewski",
                        "role": "Członek Zarządu",
                        "role_en": "Board Member / CFO",
                        "since": "2015-08-05",
                        "tenure_years": 9,
                        "other_positions": [],
                        "linkedin": None,
                        "photo": None
                    }
                ],
                "supervisory_board": [
                    {
                        "name": "Maria Lewandowska",
                        "role": "Przewodnicząca Rady Nadzorczej",
                        "role_en": "Chairperson of Supervisory Board",
                        "since": "2010-06-20",
                        "tenure_years": 14,
                        "other_positions": [
                            {
                                "company": "Invest Capital Sp. z o.o.",
                                "role": "Partner Zarządzający",
                                "since": "2005-01-10"
                            },
                            {
                                "company": "TechCorp S.A.",
                                "role": "Członek Rady Nadzorczej",
                                "since": "2018-09-01"
                            }
                        ],
                        "linkedin": "https://linkedin.com/in/maria-lewandowska",
                        "photo": None
                    },
                    {
                        "name": "Tomasz Kamiński",
                        "role": "Wiceprzewodniczący Rady Nadzorczej",
                        "role_en": "Vice-Chairperson of Supervisory Board",
                        "since": "2012-03-15",
                        "tenure_years": 12,
                        "other_positions": [],
                        "linkedin": None,
                        "photo": None
                    },
                    {
                        "name": "Katarzyna Zielińska",
                        "role": "Członek Rady Nadzorczej",
                        "role_en": "Supervisory Board Member",
                        "since": "2018-09-01",
                        "tenure_years": 6,
                        "other_positions": [
                            {
                                "company": "Legal Partners Sp. z o.o.",
                                "role": "Partner",
                                "since": "2015-06-01"
                            }
                        ],
                        "linkedin": "https://linkedin.com/in/katarzyna-zielinska",
                        "photo": None
                    }
                ],
                "prokurenci": [
                    {
                        "name": "Robert Nowicki",
                        "role": "Prokurent",
                        "role_en": "Proxy / Attorney",
                        "since": "2020-04-10",
                        "tenure_years": 4,
                        "scope": "samodzielny",
                        "scope_en": "independent",
                        "other_positions": [],
                        "linkedin": None,
                        "photo": None
                    }
                ],
                "key_person_risk": {
                    "level": "medium",
                    "factors": [
                        "CEO holds position for 29 years - high concentration of experience",
                        "Limited external board diversity",
                        "Good succession planning with Vice President in place"
                    ]
                },
                "fetched_at": datetime.utcnow().isoformat()
            }
        }, ensure_ascii=False)

    # Company profile request
    elif ("profil" in user_lower or "profile" in user_lower) and ("firma" in user_lower or "company" in user_lower):
        # Get industry-specific context
        industry_ctx = get_industry_context(user_industry or "", user_industry_segment or "")

        # Base company data
        company_data = {
            "name": "FADO Sp. z o.o.",
            "nip": "5260016831",
            "krs": "0000145732",
            "address": "ul. Fabryczna 10, 62-065 Grodzisk Wielkopolski",
            "industry": "Manufacturing of plastic products",
            "status": "Active",
            "capital": "500,000 PLN",
            "founded": "1995",
            "employees": "150-200",
            "description": "FADO is a leading Polish manufacturer specializing in injection molding and plastic processing. The company serves automotive, industrial, and consumer goods sectors."
        }

        # Add industry-specific fields for manufacturing/plastics
        if user_industry == "manufacturing" or user_industry_segment == "plastics_processing":
            company_data.update({
                "industry_specific": {
                    "machinery_type": "Injection molding machines (15 units), Extrusion lines (3 units)",
                    "production_capacity_tons": "5,000 tons/year",
                    "mold_count": "120+ active molds",
                    "material_types": ["PP", "PE", "ABS", "PC", "PA6"],
                    "certifications": ["ISO 9001:2015", "ISO 14001:2015", "IATF 16949:2016"],
                    "cycle_time_efficiency": "92%",
                    "oee": "85%",
                    "scrap_rate": "2.3%"
                },
                "terminology_note": f"Using industry terminology: {', '.join(industry_ctx['terminology'][:3])}"
            })

        return json.dumps({
            "type": "company_card",
            "data": company_data
        }, ensure_ascii=False)

    # Market trend identification request (MORE SPECIFIC - check before trend_chart)
    elif (("trend" in user_lower and ("rynek" in user_lower or "market" in user_lower or "branż" in user_lower)) or
          ("tendencje" in user_lower and "rynek" in user_lower) or
          ("kierunki rozwoju" in user_lower) or
          ("trendy" in user_lower)):
        return json.dumps({
            "type": "market_trends",
            "data": {
                "industry": "Produkcja tworzyw sztucznych - wtrysk",
                "region": "Polska",
                "analysis_date": datetime.utcnow().isoformat(),
                "time_horizon": "2024-2028",
                "trends": [
                    {
                        "id": 1,
                        "name": "Automatyzacja i Industry 4.0",
                        "category": "Technology",
                        "description": "Rosnące wdrożenia robotyzacji, IoT i AI w procesach produkcyjnych. Inteligentne wtryskarki z predykcyjną konserwacją i optymalizacją w czasie rzeczywistym.",
                        "impact": "high",
                        "impact_description": "Redukcja kosztów o 20-30%, wzrost wydajności o 25%, poprawa jakości o 15%",
                        "timeline": "2024-2026",
                        "stage": "growing",
                        "adoption_rate": "35% firm już wdraża, 45% planuje w ciągu 2 lat",
                        "drivers": [
                            "Niedobór wykwalifikowanej siły roboczej",
                            "Presja na redukcję kosztów",
                            "Dostępność technologii Industry 4.0",
                            "Wymogi jakościowe klientów automotive"
                        ],
                        "barriers": [
                            "Wysokie koszty inwestycji (2-5 mln PLN)",
                            "Brak kompetencji IT w firmach",
                            "Opór pracowników przed zmianami"
                        ],
                        "opportunities": [
                            "Przewaga konkurencyjna early adopters",
                            "Możliwość obsługi bardziej złożonych zleceń",
                            "Niższe koszty operacyjne w długim terminie"
                        ],
                        "data_sources": [
                            {"name": "Industry 4.0 Adoption Report 2024", "confidence": 90},
                            {"name": "Polish Manufacturing Survey 2024", "confidence": 85}
                        ]
                    },
                    {
                        "id": 2,
                        "name": "Zrównoważony rozwój i gospodarka cyrkularna",
                        "category": "Environmental",
                        "description": "Przejście na bioplastyki, recykling mechaniczny i chemiczny, redukcja śladu węglowego. Wymogi ESG od klientów korporacyjnych.",
                        "impact": "high",
                        "impact_description": "Nowe wymagania certyfikacyjne, presja na recykling min. 30% surowca, potencjał wzrostu marż o 5-10% na produktach eco",
                        "timeline": "2024-2028",
                        "stage": "accelerating",
                        "adoption_rate": "20% firm już wdrożyło, 60% pod presją klientów",
                        "drivers": [
                            "Dyrektywa UE o opakowaniach (min. 30% recyclatu do 2030)",
                            "Wymogi ESG od klientów automotive i FMCG",
                            "Rosnąca świadomość konsumentów",
                            "Podatek od plastiku (0.80 EUR/kg)"
                        ],
                        "barriers": [
                            "Wyższa cena bioplastyków (30-50% droższe)",
                            "Ograniczona dostępność recyclatu dobrej jakości",
                            "Konieczność certyfikacji (ISO 14001, Cradle to Cradle)"
                        ],
                        "opportunities": [
                            "Premium pricing dla produktów eco (marża +5-10%)",
                            "Dostęp do zamówień od firm z celami ESG",
                            "Subsydia i dofinansowania UE (do 50% kosztów)"
                        ],
                        "data_sources": [
                            {"name": "EU Circular Economy Report 2024", "confidence": 95},
                            {"name": "Plastics Recycling Market Study", "confidence": 85}
                        ]
                    },
                    {
                        "id": 3,
                        "name": "Nearshoring i reshoring produkcji",
                        "category": "Economic",
                        "description": "Przenoszenie produkcji bliżej rynków docelowych w UE. Polska jako hub produkcyjny dla Europy Zachodniej - alternatywa dla Chin.",
                        "impact": "medium",
                        "impact_description": "Wzrost zapytań o produkcję dla klientów z DE, FR, UK o 40-60%. Większe wolumeny, ale presja cenowa.",
                        "timeline": "2024-2027",
                        "stage": "growing",
                        "adoption_rate": "30% firm odnotowało wzrost zleceń z Zachodu",
                        "drivers": [
                            "Ryzyka geopolityczne (Chiny-Taiwan, Rosja)",
                            "Koszty transportu i ślad węglowy",
                            "Krótsze łańcuchy dostaw",
                            "Dostęp do wykwalifikowanej siły roboczej"
                        ],
                        "barriers": [
                            "Konkurencja cenowa z Europą Wschodnią",
                            "Wymagania jakościowe i certyfikacyjne",
                            "Potrzeba inwestycji w nowe moce (5-15 mln PLN)"
                        ],
                        "opportunities": [
                            "Długoterminowe kontrakty z zachodnimi OEM",
                            "Stabilne wolumeny i wyższa przewidywalność",
                            "Transfer know-how i dostęp do nowych technologii"
                        ],
                        "data_sources": [
                            {"name": "Nearshoring Trends Europe 2024", "confidence": 85},
                            {"name": "PAIH Investment Report", "confidence": 90}
                        ]
                    },
                    {
                        "id": 4,
                        "name": "Druk 3D i produkcja addytywna",
                        "category": "Technology",
                        "description": "Komplementarność druku 3D do wtrysku - prototypowanie, małe serie, personalizacja. Hybrydowe modele produkcji.",
                        "impact": "low",
                        "impact_description": "5-10% firm oferuje druk 3D jako usługę dodatkową. Skrócenie czasu prototypowania o 60%.",
                        "timeline": "2025-2028",
                        "stage": "emerging",
                        "adoption_rate": "10% firm posiada drukarki przemysłowe, 25% planuje",
                        "drivers": [
                            "Zapotrzebowanie na szybkie prototypowanie",
                            "Personalizacja produktów (mass customization)",
                            "Małe serie nieopłacalne w wtrysku (< 100 szt.)",
                            "Redukcja waste material (90% vs 50% w wtrysku)"
                        ],
                        "barriers": [
                            "Wysokie koszty materiałów (10x droższe niż granulat)",
                            "Wolna produkcja (niekonkurencyjna dla > 1000 szt.)",
                            "Ograniczone właściwości mechaniczne"
                        ],
                        "opportunities": [
                            "Nowy strumień przychodów z prototypowania",
                            "Wyższe marże na małych seriach (40-50%)",
                            "Przewaga konkurencyjna - kompleksowa oferta"
                        ],
                        "data_sources": [
                            {"name": "3D Printing Market Report 2024", "confidence": 80},
                            {"name": "Additive Manufacturing Trends", "confidence": 75}
                        ]
                    },
                    {
                        "id": 5,
                        "name": "Konsolidacja rynku i M&A",
                        "category": "Market Structure",
                        "description": "Przejmowanie mniejszych graczy przez średnie firmy i fundusze PE. Cel: skala, synergize, dywersyfikacja klientów.",
                        "impact": "medium",
                        "impact_description": "20+ transakcji M&A w sektorze w latach 2022-2024. Wyceny 0.8-1.2x przychodów lub 5-7x EBITDA.",
                        "timeline": "2024-2026",
                        "stage": "accelerating",
                        "adoption_rate": "15% rynku przeszło przez M&A w ostatnich 3 latach",
                        "drivers": [
                            "Presja cenowa i spadające marże",
                            "Potrzeba skali do negocjacji z dostawcami",
                            "Sukcesja w firmach rodzinnych",
                            "Fundusze PE szukające aktywów w manufacturing"
                        ],
                        "barriers": [
                            "Wyceny nie zawsze atrakcyjne dla sprzedających",
                            "Trudności integracyjne (kultura, systemy IT)",
                            "Obawa przed utratą kluczowych pracowników"
                        ],
                        "opportunities": [
                            "Buy-and-build strategy - budowa platformy 100-200 mln PLN",
                            "Synergize operacyjne (5-15% redukcji kosztów)",
                            "Wejście na nowe rynki geograficzne lub segmenty"
                        ],
                        "data_sources": [
                            {"name": "Polish M&A Report 2023-2024", "confidence": 90},
                            {"name": "Manufacturing Consolidation Study", "confidence": 85}
                        ]
                    },
                    {
                        "id": 6,
                        "name": "Elektryfikacja automotive",
                        "category": "Market Demand",
                        "description": "Przejście na pojazdy elektryczne zmienia mix komponentów - mniej elementów silnika, więcej obudów baterii, systemów chłodzenia.",
                        "impact": "high",
                        "impact_description": "30% spadek zapotrzebowania na komponenty ICE do 2030, wzrost o 200% dla EV components.",
                        "timeline": "2024-2030",
                        "stage": "accelerating",
                        "adoption_rate": "25% produkcji automotive już dla EV (cel: 50% w 2027)",
                        "drivers": [
                            "Cel UE: 100% nowych aut zero-emission od 2035",
                            "Inwestycje OEM w EV (VW 180 mld EUR, Tesla 150 mld USD)",
                            "Spadające ceny baterii (80% drop od 2010)",
                            "Bodźce fiskalne dla kupujących EV"
                        ],
                        "barriers": [
                            "Wymagania nowych certyfikacji (UN R100, ISO 26262)",
                            "Inwestycje w nowe formy i tooling (3-8 mln PLN)",
                            "Konkurencja z producentami bliżej gigafactories"
                        ],
                        "opportunities": [
                            "Wejście w high-margin segment (obudowy baterii marża 25-35%)",
                            "Długoterminowe partnerstwa z OEM i Tier 1",
                            "Dywersyfikacja od spadającego ICE"
                        ],
                        "data_sources": [
                            {"name": "EV Market Outlook 2024-2030", "confidence": 95},
                            {"name": "Automotive Supplier Trends Report", "confidence": 90}
                        ]
                    }
                ],
                "summary": {
                    "total_trends": 6,
                    "high_impact": 3,
                    "medium_impact": 2,
                    "low_impact": 1,
                    "categories": {
                        "Technology": 2,
                        "Environmental": 1,
                        "Economic": 1,
                        "Market Structure": 1,
                        "Market Demand": 1
                    },
                    "key_takeaways": [
                        "Automatyzacja i zrównoważony rozwój to kluczowe trendy high-impact wymagające działania już teraz",
                        "Elektryfikacja automotive to największa szansa i zagrożenie - wymaga pivot strategii produktowej",
                        "Nearshoring otwiera możliwości wzrostu, ale wymaga podniesienia standardów jakości",
                        "Konsolidacja rynku przyspiesza - firmy muszą zdecydować: buy, sell, or build scale organically",
                        "Druk 3D to emerging trend - warto pilotować, ale nie kluczowy short-term"
                    ],
                    "recommended_actions": [
                        "Priorytet 1: Ocenić gotowość do automatyzacji i zbudować roadmap Industry 4.0 (Q1 2025)",
                        "Priorytet 2: Rozpocząć certyfikację ESG i testować recyklat (Q2 2025)",
                        "Priorytet 3: Zbudować ofertę dla EV components i nawiązać kontakty z Tier 1 EV (Q2-Q3 2025)",
                        "Priorytet 4: Rozważyć M&A - czy jesteś kupującym czy sprzedającym? (H2 2025)",
                        "Priorytet 5: Pilotować druk 3D dla prototypowania (Q3-Q4 2025)"
                    ]
                }
            }
        }, ensure_ascii=False)

    # Trend analysis request (check BEFORE financial data to avoid "revenue trend" matching "revenue")
    elif "trend" in user_lower or "wykres" in user_lower or "chart" in user_lower or "wzrost" in user_lower or "growth" in user_lower:
        return json.dumps({
            "type": "trend_chart",
            "data": {
                "title": "Revenue Growth Trend (2020-2023)",
                "type": "line",
                "data": [
                    {"label": "2020", "value": 45000000},
                    {"label": "2021", "value": 52000000},
                    {"label": "2022", "value": 61000000},
                    {"label": "2023", "value": 68000000}
                ],
                "xKey": "label",
                "yKey": "value",
                "yLabel": "Revenue (PLN)",
                "color": "#3b82f6"
            }
        }, ensure_ascii=False)

    # Ownership structure request
    elif ("własność" in user_lower or "ownership" in user_lower or "wspólnicy" in user_lower or
          "akcjonariusze" in user_lower or "shareholders" in user_lower or "udziałowcy" in user_lower or
          "struktura właścicielska" in user_lower or "ownership structure" in user_lower):
        return json.dumps({
            "type": "ownership_structure",
            "data": {
                "company_name": "FADO Sp. z o.o.",
                "nip": "5260016831",
                "krs": "0000145732",
                "source": "KRS",
                "shareholders": [
                    {
                        "name": "Jan Kowalski",
                        "type": "person",
                        "shares_count": 400,
                        "shares_percentage": 40.0,
                        "shares_value": 200000,
                        "voting_rights": 40.0,
                        "since": "1995-03-15"
                    },
                    {
                        "name": "Invest Capital Sp. z o.o.",
                        "type": "company",
                        "nip": "7771234567",
                        "krs": "0000234567",
                        "shares_count": 300,
                        "shares_percentage": 30.0,
                        "shares_value": 150000,
                        "voting_rights": 30.0,
                        "since": "2010-06-20"
                    },
                    {
                        "name": "Anna Nowak",
                        "type": "person",
                        "shares_count": 200,
                        "shares_percentage": 20.0,
                        "shares_value": 100000,
                        "voting_rights": 20.0,
                        "since": "2005-11-10"
                    },
                    {
                        "name": "Piotr Wiśniewski",
                        "type": "person",
                        "shares_count": 100,
                        "shares_percentage": 10.0,
                        "shares_value": 50000,
                        "voting_rights": 10.0,
                        "since": "2015-08-05"
                    }
                ],
                "beneficial_owners": [
                    {
                        "name": "Jan Kowalski",
                        "percentage": 40.0,
                        "direct": True,
                        "source": "Direct shareholder"
                    },
                    {
                        "name": "Anna Nowak",
                        "percentage": 20.0,
                        "direct": True,
                        "source": "Direct shareholder"
                    },
                    {
                        "name": "Piotr Wiśniewski",
                        "percentage": 10.0,
                        "direct": True,
                        "source": "Direct shareholder"
                    },
                    {
                        "name": "Fundusz Inwestycyjny PKO",
                        "percentage": 21.0,
                        "direct": False,
                        "source": "Via Invest Capital Sp. z o.o. (70%)"
                    },
                    {
                        "name": "Tomasz Lewandowski",
                        "percentage": 9.0,
                        "direct": False,
                        "source": "Via Invest Capital Sp. z o.o. (30%)"
                    }
                ],
                "related_companies": [
                    {
                        "name": "FADO Automotive Sp. z o.o.",
                        "nip": "5260987654",
                        "krs": "0000345678",
                        "relationship": "subsidiary",
                        "ownership_percentage": 100.0,
                        "description": "Spółka zależna - produkcja komponentów motoryzacyjnych"
                    },
                    {
                        "name": "Plastics Innovation Sp. z o.o.",
                        "nip": "5260876543",
                        "krs": "0000456789",
                        "relationship": "subsidiary",
                        "ownership_percentage": 51.0,
                        "description": "Spółka zależna - badania i rozwój"
                    },
                    {
                        "name": "Invest Capital Sp. z o.o.",
                        "nip": "7771234567",
                        "krs": "0000234567",
                        "relationship": "parent",
                        "ownership_percentage": 30.0,
                        "description": "Główny inwestor korporacyjny"
                    }
                ],
                "ownership_chain": [
                    {
                        "level": 0,
                        "entity": "FADO Sp. z o.o.",
                        "type": "target",
                        "nip": "5260016831"
                    },
                    {
                        "level": 1,
                        "entity": "Jan Kowalski",
                        "type": "person",
                        "percentage": 40.0
                    },
                    {
                        "level": 1,
                        "entity": "Invest Capital Sp. z o.o.",
                        "type": "company",
                        "percentage": 30.0,
                        "nip": "7771234567"
                    },
                    {
                        "level": 2,
                        "entity": "Fundusz Inwestycyjny PKO",
                        "type": "fund",
                        "percentage": 70.0,
                        "via": "Invest Capital Sp. z o.o."
                    },
                    {
                        "level": 2,
                        "entity": "Tomasz Lewandowski",
                        "type": "person",
                        "percentage": 30.0,
                        "via": "Invest Capital Sp. z o.o."
                    },
                    {
                        "level": 1,
                        "entity": "Anna Nowak",
                        "type": "person",
                        "percentage": 20.0
                    },
                    {
                        "level": 1,
                        "entity": "Piotr Wiśniewski",
                        "type": "person",
                        "percentage": 10.0
                    }
                ],
                "capital_info": {
                    "share_capital": 500000,
                    "total_shares": 1000,
                    "share_value": 500,
                    "currency": "PLN"
                },
                "fetched_at": datetime.utcnow().isoformat()
            }
        }, ensure_ascii=False)

    # Competitor benchmarking table request (MUST be before competitor_mapping)
    elif ("porównaj konkurent" in user_lower or "compare competitor" in user_lower or
          "benchmarking" in user_lower or "porównanie konkurent" in user_lower or
          "tabela porównaw" in user_lower or "comparison table" in user_lower or
          "competitor comparison" in user_lower):
        return json.dumps({
            "type": "competitor_benchmarking",
            "data": {
                "target_company": {
                    "name": "FADO Sp. z o.o.",
                    "nip": "5260016831",
                    "krs": "0000145732"
                },
                "competitors": [
                    {
                        "name": "FADO Sp. z o.o.",
                        "is_target": True,
                        "location": "Pabianice, łódzkie",
                        "employees": 150,
                        "revenue_2023": 45.2,
                        "revenue_2022": 40.2,
                        "revenue_2021": 35.8,
                        "revenue_growth_yoy": 12.3,
                        "profit_margin": 10.6,
                        "roe": 18.2,
                        "roa": 9.4,
                        "debt_ratio": 32,
                        "current_ratio": 2.1,
                        "market_share": 3.5,
                        "certifications": ["ISO 9001", "ISO 14001"],
                        "export_markets": False,
                        "r_and_d_investment": True,
                        "website_quality": 85,
                        "linkedin_followers": 1200
                    },
                    {
                        "name": "PLAST-MET S.A.",
                        "is_target": False,
                        "location": "Poznań, wielkopolskie",
                        "employees": 225,
                        "revenue_2023": 75.0,
                        "revenue_2022": 68.5,
                        "revenue_2021": 62.0,
                        "revenue_growth_yoy": 9.5,
                        "profit_margin": 12.8,
                        "roe": 20.1,
                        "roa": 10.2,
                        "debt_ratio": 28,
                        "current_ratio": 2.4,
                        "market_share": 5.8,
                        "certifications": ["ISO 9001", "ISO 14001", "IATF 16949"],
                        "export_markets": True,
                        "r_and_d_investment": True,
                        "website_quality": 90,
                        "linkedin_followers": 2500
                    },
                    {
                        "name": "POLIMER Sp. z o.o.",
                        "is_target": False,
                        "location": "Wrocław, dolnośląskie",
                        "employees": 175,
                        "revenue_2023": 60.0,
                        "revenue_2022": 55.2,
                        "revenue_2021": 51.0,
                        "revenue_growth_yoy": 8.7,
                        "profit_margin": 9.2,
                        "roe": 15.8,
                        "roa": 8.1,
                        "debt_ratio": 38,
                        "current_ratio": 1.9,
                        "market_share": 4.6,
                        "certifications": ["ISO 9001"],
                        "export_markets": False,
                        "r_and_d_investment": False,
                        "website_quality": 75,
                        "linkedin_followers": 850
                    },
                    {
                        "name": "EURO-PLAST Sp. z o.o.",
                        "is_target": False,
                        "location": "Gliwice, śląskie",
                        "employees": 200,
                        "revenue_2023": 70.0,
                        "revenue_2022": 62.0,
                        "revenue_2021": 55.0,
                        "revenue_growth_yoy": 12.9,
                        "profit_margin": 11.5,
                        "roe": 19.2,
                        "roa": 9.8,
                        "debt_ratio": 30,
                        "current_ratio": 2.2,
                        "market_share": 5.4,
                        "certifications": ["ISO 9001", "ISO 14001", "IATF 16949"],
                        "export_markets": True,
                        "r_and_d_investment": True,
                        "website_quality": 88,
                        "linkedin_followers": 3200
                    },
                    {
                        "name": "TECHNOPLAST Sp. z o.o.",
                        "is_target": False,
                        "location": "Łódź, łódzkie",
                        "employees": 125,
                        "revenue_2023": 45.0,
                        "revenue_2022": 40.0,
                        "revenue_2021": 36.0,
                        "revenue_growth_yoy": 12.5,
                        "profit_margin": 8.5,
                        "roe": 14.2,
                        "roa": 7.3,
                        "debt_ratio": 42,
                        "current_ratio": 1.7,
                        "market_share": 3.5,
                        "certifications": ["ISO 9001"],
                        "export_markets": False,
                        "r_and_d_investment": False,
                        "website_quality": 70,
                        "linkedin_followers": 450
                    }
                ],
                "metrics": {
                    "categories": [
                        {
                            "name": "Wielkość firmy",
                            "metrics": [
                                {"key": "employees", "label": "Zatrudnienie", "unit": "osób", "format": "number"},
                                {"key": "revenue_2023", "label": "Przychody 2023", "unit": "mln PLN", "format": "decimal"},
                                {"key": "market_share", "label": "Udział w rynku", "unit": "%", "format": "decimal"}
                            ]
                        },
                        {
                            "name": "Wyniki finansowe",
                            "metrics": [
                                {"key": "revenue_growth_yoy", "label": "Wzrost przychodów YoY", "unit": "%", "format": "decimal", "higher_is_better": True},
                                {"key": "profit_margin", "label": "Marża zysku", "unit": "%", "format": "decimal", "higher_is_better": True},
                                {"key": "roe", "label": "ROE", "unit": "%", "format": "decimal", "higher_is_better": True},
                                {"key": "roa", "label": "ROA", "unit": "%", "format": "decimal", "higher_is_better": True}
                            ]
                        },
                        {
                            "name": "Kondycja finansowa",
                            "metrics": [
                                {"key": "debt_ratio", "label": "Wskaźnik zadłużenia", "unit": "%", "format": "number", "higher_is_better": False},
                                {"key": "current_ratio", "label": "Płynność bieżąca", "unit": "", "format": "decimal", "higher_is_better": True}
                            ]
                        },
                        {
                            "name": "Rozwój i innowacje",
                            "metrics": [
                                {"key": "certifications", "label": "Certyfikaty", "unit": "", "format": "list"},
                                {"key": "export_markets", "label": "Eksport", "unit": "", "format": "boolean"},
                                {"key": "r_and_d_investment", "label": "Inwestycje R&D", "unit": "", "format": "boolean"}
                            ]
                        },
                        {
                            "name": "Obecność online",
                            "metrics": [
                                {"key": "website_quality", "label": "Jakość strony", "unit": "/100", "format": "number", "higher_is_better": True},
                                {"key": "linkedin_followers", "label": "Obserwujący LinkedIn", "unit": "", "format": "number", "higher_is_better": True}
                            ]
                        }
                    ]
                },
                "insights": {
                    "strengths": [
                        "FADO ma najwyższą marżę zysku wśród firm o podobnej wielkości",
                        "Silna pozycja ROE (18.2%) - lepsza niż POLIMER i TECHNOPLAST",
                        "Niskie zadłużenie (32%) daje przestrzeń na finansowanie rozwoju"
                    ],
                    "weaknesses": [
                        "Brak eksportu - konkurenci jak PLAST-MET i EURO-PLAST mają przewagę",
                        "Mniej certyfikatów niż liderzy (brak IATF 16949 dla automotive)",
                        "Niższa obecność w social media (LinkedIn) niż główni konkurenci"
                    ],
                    "opportunities": [
                        "Możliwość zwiększenia udziału w rynku - podobny poziom do TECHNOPLAST",
                        "Potencjał ekspansji na rynki eksportowe",
                        "Inwestycje w dodatkowe certyfikaty mogą otworzyć nowe segmenty"
                    ]
                },
                "fetched_at": datetime.utcnow().isoformat()
            }
        }, ensure_ascii=False)

    # Competitor mapping request
    elif ("konkurencja" in user_lower or "competitor" in user_lower or "konkurenci" in user_lower or
          "konkurent" in user_lower or "analiza konkurencyjna" in user_lower or
          "competitive analysis" in user_lower or "rywale" in user_lower):
        return json.dumps({
            "type": "competitor_mapping",
            "data": {
                "target_company": {
                    "name": "FADO Sp. z o.o.",
                    "nip": "5260016831",
                    "krs": "0000145732",
                    "pkd_main": "22.29.Z",
                    "pkd_description": "Produkcja pozostałych wyrobów z tworzyw sztucznych",
                    "industry": "Manufacturing - Plastic Products"
                },
                "search_criteria": {
                    "method": "PKD-based search",
                    "pkd_codes": ["22.29.Z", "22.21.Z", "22.22.Z"],
                    "geographic_scope": "Poland",
                    "filters_applied": ["Active companies", "Similar size (50-300 employees)"]
                },
                "competitors": [
                    {
                        "id": 1,
                        "name": "PLAST-MET S.A.",
                        "nip": "5261234567",
                        "krs": "0000098765",
                        "category": "direct",
                        "category_description": "Direct competitor - same PKD, same products",
                        "location": "Poznań, wielkopolskie",
                        "employees": "200-250",
                        "revenue_estimate": "75M PLN",
                        "pkd_main": "22.29.Z",
                        "products": ["Injection molding", "Plastic parts for automotive"],
                        "market_position": "Strong regional player",
                        "competitive_advantage": "ISO certifications, modern machinery",
                        "website": "https://plast-met.pl"
                    },
                    {
                        "id": 2,
                        "name": "POLIMER Sp. z o.o.",
                        "nip": "7771122334",
                        "krs": "0000112233",
                        "category": "direct",
                        "category_description": "Direct competitor - identical product portfolio",
                        "location": "Wrocław, dolnośląskie",
                        "employees": "150-200",
                        "revenue_estimate": "60M PLN",
                        "pkd_main": "22.29.Z",
                        "products": ["Plastic components", "Technical plastics"],
                        "market_position": "Mid-tier player",
                        "competitive_advantage": "Fast delivery times, flexible production",
                        "website": "https://polimer.com.pl"
                    },
                    {
                        "id": 3,
                        "name": "TECHNOPLAST Sp. z o.o.",
                        "nip": "9991234567",
                        "krs": "0000223344",
                        "category": "direct",
                        "category_description": "Direct competitor - same target market",
                        "location": "Łódź, łódzkie",
                        "employees": "100-150",
                        "revenue_estimate": "45M PLN",
                        "pkd_main": "22.29.Z",
                        "products": ["Injection molding services", "Plastic tooling"],
                        "market_position": "Growing competitor",
                        "competitive_advantage": "Competitive pricing, good customer service",
                        "website": "https://technoplast.pl"
                    },
                    {
                        "id": 4,
                        "name": "FORMA S.A.",
                        "nip": "8881122334",
                        "krs": "0000334455",
                        "category": "indirect",
                        "category_description": "Indirect competitor - focuses on tooling, not final products",
                        "location": "Kraków, małopolskie",
                        "employees": "80-100",
                        "revenue_estimate": "35M PLN",
                        "pkd_main": "22.21.Z",
                        "products": ["Plastic molds", "Tool design"],
                        "market_position": "Niche specialist",
                        "competitive_advantage": "Technical expertise, custom solutions",
                        "website": "https://forma.com.pl"
                    },
                    {
                        "id": 5,
                        "name": "PLASTIK-TECH Sp. z o.o.",
                        "nip": "6661234567",
                        "krs": "0000445566",
                        "category": "direct",
                        "category_description": "Direct competitor - similar scale and market",
                        "location": "Gdańsk, pomorskie",
                        "employees": "120-150",
                        "revenue_estimate": "50M PLN",
                        "pkd_main": "22.29.Z",
                        "products": ["Plastic packaging", "Industrial plastics"],
                        "market_position": "Regional leader in northern Poland",
                        "competitive_advantage": "Export capabilities, EU clients",
                        "website": "https://plastik-tech.pl"
                    },
                    {
                        "id": 6,
                        "name": "EURO-PLAST Sp. z o.o.",
                        "nip": "7771234568",
                        "krs": "0000556677",
                        "category": "direct",
                        "category_description": "Direct competitor - automotive focus",
                        "location": "Gliwice, śląskie",
                        "employees": "180-220",
                        "revenue_estimate": "70M PLN",
                        "pkd_main": "22.29.Z",
                        "products": ["Automotive plastics", "Technical components"],
                        "market_position": "Strong competitor with German partnerships",
                        "competitive_advantage": "Tier 1 automotive supplier status",
                        "website": "https://europlast.com.pl"
                    },
                    {
                        "id": 7,
                        "name": "RECYCLING PLAST S.A.",
                        "nip": "5551234567",
                        "krs": "0000667788",
                        "category": "substitute",
                        "category_description": "Substitute competitor - recycled plastics alternative",
                        "location": "Katowice, śląskie",
                        "employees": "90-110",
                        "revenue_estimate": "40M PLN",
                        "pkd_main": "22.22.Z",
                        "products": ["Recycled plastic products", "Eco-friendly alternatives"],
                        "market_position": "Emerging green alternative",
                        "competitive_advantage": "Sustainability focus, lower prices",
                        "website": "https://recyclingplast.pl"
                    },
                    {
                        "id": 8,
                        "name": "INJECTION MOLDERS Sp. z o.o.",
                        "nip": "4441234567",
                        "krs": "0000778899",
                        "category": "direct",
                        "category_description": "Direct competitor - specialized in injection",
                        "location": "Bydgoszcz, kujawsko-pomorskie",
                        "employees": "100-120",
                        "revenue_estimate": "42M PLN",
                        "pkd_main": "22.29.Z",
                        "products": ["Injection molding", "Precision plastic parts"],
                        "market_position": "Mid-market player",
                        "competitive_advantage": "High precision capabilities, quick prototyping",
                        "website": "https://injection-molders.pl"
                    }
                ],
                "summary": {
                    "total_competitors": 8,
                    "direct_competitors": 6,
                    "indirect_competitors": 1,
                    "substitute_competitors": 1,
                    "geographic_distribution": {
                        "wielkopolskie": 1,
                        "dolnośląskie": 1,
                        "łódzkie": 1,
                        "małopolskie": 1,
                        "pomorskie": 1,
                        "śląskie": 2,
                        "kujawsko-pomorskie": 1
                    },
                    "average_revenue": "52M PLN",
                    "market_concentration": "Moderate - no dominant player",
                    "competitive_intensity": "High - 6 direct competitors in similar size range"
                },
                "insights": [
                    "Strong regional competition across Poland with no clear market leader",
                    "Most competitors focus on automotive sector - high dependency on single industry",
                    "Geographic diversification of competitors reduces local monopoly risks",
                    "Emerging threat from recycled plastics (green alternative) - sustainability trend",
                    "Key differentiators: certifications, delivery speed, export capabilities"
                ],
                "recommended_actions": [
                    "Strengthen ISO certifications to match PLAST-MET capabilities",
                    "Develop sustainability offerings to counter RECYCLING PLAST threat",
                    "Explore export markets like EURO-PLAST (German partnerships)",
                    "Invest in precision capabilities to compete with INJECTION MOLDERS",
                    "Consider strategic partnerships in underserved regions"
                ],
                "fetched_at": datetime.utcnow().isoformat(),
                "data_freshness": "Real-time PKD search + enriched company data"
            }
        }, ensure_ascii=False)

    # Porter Five Forces analysis request
    elif ("porter" in user_lower or
          ("five forces" in user_lower) or
          ("5 forces" in user_lower) or
          ("pięć sił" in user_lower) or
          ("5 sił" in user_lower)):
        return json.dumps({
            "type": "porter_analysis",
            "data": {
                "industry_name": "Produkcja tworzyw sztucznych",
                "region": "Polska",
                "analysis_date": datetime.utcnow().isoformat(),
                "supplier_power": {
                    "score": 7,
                    "level": "high",
                    "factors": [
                        {
                            "factor": "Koncentracja dostawców surowców",
                            "description": "Rynek granulatów tworzyw (PET, PP, PE) zdominowany przez kilku dużych dostawców globalnych (BASF, Dow, LyondellBasell).",
                            "impact": "high"
                        },
                        {
                            "factor": "Koszty zmiany dostawcy",
                            "description": "Wysokie koszty certyfikacji nowych surowców i dostosowania procesów produkcyjnych.",
                            "impact": "medium"
                        },
                        {
                            "factor": "Brak substytutów surowców",
                            "description": "Ograniczone alternatywy dla petrochemicznych granulatów, bioplastiki stanowią <5% rynku.",
                            "impact": "high"
                        },
                        {
                            "factor": "Integracja pionowa dostawców",
                            "description": "Duzi dostawcy posiadają własne rafinerie i łańcuchy dystrybucji.",
                            "impact": "medium"
                        }
                    ],
                    "data_source": "Plastics Europe Supply Chain Report 2024"
                },
                "buyer_power": {
                    "score": 6,
                    "level": "medium-high",
                    "factors": [
                        {
                            "factor": "Duzi klienci B2B",
                            "description": "Sektor automotive i elektronika stanowią 60-70% odbiorców, duża siła negocjacyjna dużych OEM.",
                            "impact": "high"
                        },
                        {
                            "factor": "Standaryzacja produktów",
                            "description": "Wiele komponentów z tworzyw to produkty o niskiej różnicowości (opakowania, części standardowe).",
                            "impact": "medium"
                        },
                        {
                            "factor": "Koszty zmiany dostawcy",
                            "description": "Dla klientów premium (automotive, medical) wysokie koszty zmiany, dla opakowań niskie.",
                            "impact": "medium"
                        },
                        {
                            "factor": "Dostęp do informacji",
                            "description": "Klienci mają łatwy dostęp do porównań cenowych i ofert konkurencji.",
                            "impact": "medium"
                        }
                    ],
                    "data_source": "Automotive & Packaging Industry Buyer Trends 2024"
                },
                "competitive_rivalry": {
                    "score": 8,
                    "level": "high",
                    "factors": [
                        {
                            "factor": "Liczba konkurentów",
                            "description": "Rynek silnie rozdrobniony - setki małych i średnich producentów w Polsce (600+ firm z PKD 22.2).",
                            "impact": "high"
                        },
                        {
                            "factor": "Niski wzrost rynku",
                            "description": "Rynek tworzyw w EU rośnie tylko 1-2% rocznie, walka o udział rynkowy.",
                            "impact": "high"
                        },
                        {
                            "factor": "Wysokie koszty stałe",
                            "description": "Konieczność utrzymania wykorzystania mocy produkcyjnych, presja na ceny.",
                            "impact": "high"
                        },
                        {
                            "factor": "Niskie bariery zmiany",
                            "description": "Dla produktów commodity (opakowania) łatwa zmiana dostawcy przez klientów.",
                            "impact": "medium"
                        },
                        {
                            "factor": "Różnorodność konkurentów",
                            "description": "Konkurencja z lokalnymi graczami, dużymi koncernami międzynarodowymi i firmami z Azji.",
                            "impact": "high"
                        }
                    ],
                    "data_source": "Polish Plastics Industry Competitive Landscape 2024"
                },
                "threat_of_substitution": {
                    "score": 5,
                    "level": "medium",
                    "factors": [
                        {
                            "factor": "Materiały alternatywne",
                            "description": "Metalowe i szklane opakowania, papier, drewno, kompozyty - rosnące zastosowanie w niektórych segmentach.",
                            "impact": "medium"
                        },
                        {
                            "factor": "Bioplastiki i materiały biodegradowalne",
                            "description": "Rynek biodegradowalnych alternatyw rośnie 15% rocznie, ale nadal nisza (4-5% rynku).",
                            "impact": "medium"
                        },
                        {
                            "factor": "Różnice w kosztach i właściwościach",
                            "description": "Tworzywa często tańsze i lżejsze od alternatyw, ale rosnąca presja regulacyjna na plastik.",
                            "impact": "medium"
                        },
                        {
                            "factor": "Trendy konsumenckie",
                            "description": "Rosnąca preferencja dla 'plastiku-free' packaging w segmencie FMCG i kosmetyków.",
                            "impact": "medium"
                        }
                    ],
                    "data_source": "EU Sustainable Materials Transition Report 2024"
                },
                "threat_of_new_entry": {
                    "score": 4,
                    "level": "medium-low",
                    "factors": [
                        {
                            "factor": "Wysokie nakłady kapitałowe",
                            "description": "Wtryskarki przemysłowe kosztują 100k-2M EUR, wymóg parku maszynowego min. 5-10 maszyn.",
                            "impact": "low"
                        },
                        {
                            "factor": "Ekonomia skali",
                            "description": "Gracze z dużymi wolumenami mają przewagę kosztową 20-30% vs. małe firmy.",
                            "impact": "medium"
                        },
                        {
                            "factor": "Wymagania certyfikacyjne",
                            "description": "ISO 9001, ISO 14001, automotive IATF 16949, medical ISO 13485 - kosztowne certyfikaty.",
                            "impact": "medium"
                        },
                        {
                            "factor": "Dostęp do kanałów dystrybucji",
                            "description": "Długoletnie relacje z dużymi klientami (automotive, electronics) trudne do zdobycia.",
                            "impact": "medium"
                        },
                        {
                            "factor": "Konkurencja z Azji",
                            "description": "Chińscy i wietnamscy producenci wchodzą na rynek EU z cenami niższymi o 25-35%.",
                            "impact": "high"
                        }
                    ],
                    "data_source": "Market Entry Barriers Analysis - Plastics Manufacturing EU 2024"
                },
                "overall_assessment": {
                    "average_score": 6.0,
                    "industry_attractiveness": "medium",
                    "summary": "Branża produkcji tworzyw sztucznych w Polsce charakteryzuje się średnią atrakcyjnością. Wysoka siła dostawców (7/10) i intensywna rywalizacja (8/10) ograniczają marże. Średnia siła nabywców (6/10) i umiarkowane zagrożenie substytutami (5/10) oraz nowymi wejściami (4/10) dają pewną przestrzeń obronną. Kluczowe strategie: dyferencjacja produktów premium, automatyzacja dla redukcji kosztów, ekspansja geograficzna.",
                    "key_recommendations": [
                        "Dywersyfikacja bazy dostawców surowców (hedge przeciw sile dostawców)",
                        "Inwestycja w segmenty premium/niszowe z wyższą marżą (automotive medical, aerospace)",
                        "Automatyzacja produkcji dla przewagi kosztowej vs. konkurenci",
                        "Rozwój oferty bioplastyków (hedge przeciw substytutom i trendom)",
                        "Budowa silnych relacji z klientami i kontraktów długoterminowych"
                    ]
                },
                "data_sources": [
                    {"name": "Plastics Europe Supply Chain Report 2024", "confidence": 0.90},
                    {"name": "Automotive & Packaging Industry Trends 2024", "confidence": 0.85},
                    {"name": "Polish Plastics Industry Competitive Landscape", "confidence": 0.90},
                    {"name": "EU Sustainable Materials Transition Report", "confidence": 0.85},
                    {"name": "Market Entry Barriers Analysis 2024", "confidence": 0.85}
                ]
            }
        }, ensure_ascii=False)

    # PESTLE analysis request
    elif ("pestle" in user_lower or
          "pestel" in user_lower or
          ("political" in user_lower and "economic" in user_lower) or
          ("polityczne" in user_lower and "ekonomiczne" in user_lower)):
        return json.dumps({
            "type": "pestle_analysis",
            "data": {
                "industry_name": "Produkcja tworzyw sztucznych",
                "region": "Polska",
                "analysis_date": datetime.utcnow().isoformat(),
                "political": {
                    "factors": [
                        {
                            "factor": "Polityka klimatyczna UE",
                            "description": "European Green Deal wymusza redukcję emisji CO2 o 55% do 2030 roku, wpływając na koszty energii i surowców.",
                            "impact": "high",
                            "timeline": "short-term",
                            "sentiment": "threat"
                        },
                        {
                            "factor": "Regulacje dotyczące plastiku jednorazowego",
                            "description": "Dyrektywa SUP (Single-Use Plastics) zakazuje produkcji niektórych produktów plastikowych od 2021.",
                            "impact": "high",
                            "timeline": "short-term",
                            "sentiment": "threat"
                        },
                        {
                            "factor": "Stabilność polityczna Polski",
                            "description": "Względnie stabilna sytuacja polityczna sprzyja inwestycjom długoterminowym w sektor produkcyjny.",
                            "impact": "medium",
                            "timeline": "medium-term",
                            "sentiment": "opportunity"
                        },
                        {
                            "factor": "Dotacje i wsparcie dla przemysłu",
                            "description": "Fundusze UE na transformację zieloną (REPowerEU, Just Transition Fund) dostępne dla innowacyjnych projektów.",
                            "impact": "medium",
                            "timeline": "short-term",
                            "sentiment": "opportunity"
                        }
                    ]
                },
                "economic": {
                    "factors": [
                        {
                            "factor": "Wzrost cen surowców petrochemicznych",
                            "description": "Ceny granulatów plastikowych wzrosły o 35% w latach 2022-2023 z powodu kryzysu energetycznego.",
                            "impact": "high",
                            "timeline": "short-term",
                            "sentiment": "threat"
                        },
                        {
                            "factor": "Inflacja i koszty pracy",
                            "description": "Inflacja 10-15% (2022-2023) i rosnące płace (wzrost 12% r/r) zwiększają koszty operacyjne.",
                            "impact": "high",
                            "timeline": "short-term",
                            "sentiment": "threat"
                        },
                        {
                            "factor": "Koszty energii",
                            "description": "Ceny energii elektrycznej wzrosły o 120% od 2021 roku, znacząco wpływając na rentowność produkcji.",
                            "impact": "high",
                            "timeline": "medium-term",
                            "sentiment": "threat"
                        },
                        {
                            "factor": "Wzrost PKB i konsumpcji",
                            "description": "Przewidywany wzrost PKB Polski 2-3% rocznie do 2026, wspierający popyt na produkty z tworzyw.",
                            "impact": "medium",
                            "timeline": "medium-term",
                            "sentiment": "opportunity"
                        }
                    ]
                },
                "social": {
                    "factors": [
                        {
                            "factor": "Rosnąca świadomość ekologiczna",
                            "description": "65% konsumentów preferuje produkty w opakowaniach biodegradowalnych lub wielokrotnego użytku.",
                            "impact": "high",
                            "timeline": "medium-term",
                            "sentiment": "threat"
                        },
                        {
                            "factor": "Zmiana nawyków konsumenckich",
                            "description": "Trend 'zero waste' i redukcja plastiku w gospodarstwach domowych (wzrost 40% w ciągu 3 lat).",
                            "impact": "medium",
                            "timeline": "long-term",
                            "sentiment": "threat"
                        },
                        {
                            "factor": "Deficyt wykwalifikowanej kadry",
                            "description": "Brak 15% wykwalifikowanych operatorów i technologów w branży tworzyw sztucznych.",
                            "impact": "medium",
                            "timeline": "short-term",
                            "sentiment": "threat"
                        },
                        {
                            "factor": "Urbanizacja i wzrost klasy średniej",
                            "description": "Rosnące zapotrzebowanie na produkty konsumenckie i opakowania w miastach.",
                            "impact": "medium",
                            "timeline": "long-term",
                            "sentiment": "opportunity"
                        }
                    ]
                },
                "technological": {
                    "factors": [
                        {
                            "factor": "Automatyzacja i Industry 4.0",
                            "description": "Roboty współpracujące i IoT w produkcji mogą zwiększyć efektywność o 25-30%.",
                            "impact": "high",
                            "timeline": "medium-term",
                            "sentiment": "opportunity"
                        },
                        {
                            "factor": "Rozwój bioplastyków",
                            "description": "Technologie PLA, PHA i innych bioplastyków rozwijają się w tempie 15% rocznie.",
                            "impact": "high",
                            "timeline": "medium-term",
                            "sentiment": "opportunity"
                        },
                        {
                            "factor": "Recykling chemiczny",
                            "description": "Nowe technologie chemicznego recyklingu tworzyw (pyroliza, depolimeryzacja) zyskują na znaczeniu.",
                            "impact": "medium",
                            "timeline": "long-term",
                            "sentiment": "opportunity"
                        },
                        {
                            "factor": "Druk 3D z tworzyw",
                            "description": "Addytywne technologie produkcji (FDM, SLS) mogą zastąpić wtrysk w niektórych aplikacjach.",
                            "impact": "low",
                            "timeline": "long-term",
                            "sentiment": "threat"
                        }
                    ]
                },
                "legal": {
                    "factors": [
                        {
                            "factor": "Rozszerzona Odpowiedzialność Producenta (ROP)",
                            "description": "Od 2023 producenci muszą finansować zbiórkę i recykling opakowań (0.50-1.50 PLN/kg).",
                            "impact": "high",
                            "timeline": "short-term",
                            "sentiment": "threat"
                        },
                        {
                            "factor": "Podatek od plastiku",
                            "description": "Opłata za nietrzeźwiane opakowania plastikowe 0.80 EUR/kg (3.50 PLN/kg) od 2021.",
                            "impact": "high",
                            "timeline": "short-term",
                            "sentiment": "threat"
                        },
                        {
                            "factor": "Normy bezpieczeństwa produktów",
                            "description": "Zaostrzające się wymagania dla materiałów kontaktujących się z żywnością (REACH, FDA).",
                            "impact": "medium",
                            "timeline": "medium-term",
                            "sentiment": "threat"
                        },
                        {
                            "factor": "Prawo pracy i BHP",
                            "description": "Nowe regulacje dotyczące emisji w miejscu pracy i ochrony zdrowia pracowników.",
                            "impact": "low",
                            "timeline": "medium-term",
                            "sentiment": "threat"
                        }
                    ]
                },
                "environmental": {
                    "factors": [
                        {
                            "factor": "Zanieczyszczenie plastikiem oceanów",
                            "description": "8 milionów ton plastiku trafia rocznie do oceanów, rosnąca presja społeczna na redukcję produkcji.",
                            "impact": "high",
                            "timeline": "long-term",
                            "sentiment": "threat"
                        },
                        {
                            "factor": "Cel neutralności klimatycznej 2050",
                            "description": "UE wymaga osiągnięcia neutralności węglowej, wpływając na całą branżę petrochemiczną.",
                            "impact": "high",
                            "timeline": "long-term",
                            "sentiment": "threat"
                        },
                        {
                            "factor": "Gospodarka obiegu zamkniętego (circular economy)",
                            "description": "Cele UE: 50% recyklingu tworzyw do 2025, 65% do 2030 - wymusza zmiany w modelu biznesowym.",
                            "impact": "high",
                            "timeline": "medium-term",
                            "sentiment": "opportunity"
                        },
                        {
                            "factor": "Efektywność energetyczna",
                            "description": "Możliwość redukcji zużycia energii o 20-30% przez modernizację procesów i wykorzystanie odnawialnych źródeł.",
                            "impact": "medium",
                            "timeline": "medium-term",
                            "sentiment": "opportunity"
                        }
                    ]
                },
                "summary": {
                    "opportunities_count": 8,
                    "threats_count": 16,
                    "high_impact_count": 14,
                    "overall_outlook": "challenging",
                    "key_insights": [
                        "Branża tworzyw sztucznych stoi przed znaczącymi wyzwaniami regulacyjnymi i społecznymi",
                        "Wysokie koszty energii i surowców (wzrost 35-120%) znacząco obniżają marże",
                        "Transformacja w kierunku bioplastyków i gospodarki obiegu zamkniętego jest konieczna",
                        "Automatyzacja i Industry 4.0 oferują szanse na poprawę efektywności 25-30%",
                        "Firmy muszą dostosować się do rosnących wymagań ekologicznych lub stracić udział rynkowy"
                    ],
                    "strategic_priorities": [
                        "Inwestycja w linie do produkcji bioplastyków i materiałów biodegradowalnych",
                        "Automatyzacja produkcji dla redukcji kosztów pracy i energii",
                        "Wdrożenie programu circular economy (recykling, upcykling)",
                        "Dywersyfikacja źródeł energii (fotowoltaika, zakup zielonej energii)",
                        "Lobbing na rzecz proporcjonalnych regulacji i wsparcia dla transformacji"
                    ]
                },
                "data_sources": [
                    {"name": "European Green Deal Policy Framework 2024", "confidence": 0.95},
                    {"name": "Polish Economic Outlook 2024-2026", "confidence": 0.90},
                    {"name": "Consumer Sustainability Trends Report 2024", "confidence": 0.85},
                    {"name": "Industry 4.0 in Plastics Manufacturing", "confidence": 0.85},
                    {"name": "EU Circular Economy Action Plan", "confidence": 0.95}
                ]
            }
        }, ensure_ascii=False)

    # Market sizing TAM/SAM/SOM request
    elif (("tam" in user_lower and "sam" in user_lower) or
          ("market" in user_lower and "sizing" in user_lower) or
          ("wielkość" in user_lower and ("rynek" in user_lower or "rynku" in user_lower)) or
          ("addressable market" in user_lower)):
        return json.dumps({
            "type": "market_sizing",
            "data": {
                "industry": "Produkcja tworzyw sztucznych - wtrysk",
                "region": "Polska",
                "year": 2026,
                "analysis_date": datetime.utcnow().isoformat(),
                "tam": {
                    "value": 12500000000,
                    "value_formatted": "12.5 mld PLN",
                    "description": "Całkowity rynek produkcji tworzyw sztucznych w Polsce",
                    "methodology": "Top-down",
                    "calculation_steps": [
                        "Całkowita produkcja tworzyw w Polsce: 2.5 mln ton rocznie",
                        "Średnia cena granulatu: 5000 PLN/ton",
                        "TAM = 2,500,000 ton × 5,000 PLN/ton = 12.5 mld PLN"
                    ],
                    "growth_rate": 0.025,
                    "growth_rate_formatted": "2.5% CAGR (2024-2028)",
                    "market_segments": [
                        {"name": "Opakowania", "share": 0.35, "value": "4.4 mld PLN"},
                        {"name": "Automotive", "share": 0.25, "value": "3.1 mld PLN"},
                        {"name": "Budownictwo", "share": 0.20, "value": "2.5 mld PLN"},
                        {"name": "Elektronika", "share": 0.10, "value": "1.25 mld PLN"},
                        {"name": "Inne", "share": 0.10, "value": "1.25 mld PLN"}
                    ],
                    "data_sources": [
                        "Plastics Europe Market Report 2024",
                        "GUS Statistics - Manufacturing Sector",
                        "Polish Chamber of Chemical Industry"
                    ]
                },
                "sam": {
                    "value": 3750000000,
                    "value_formatted": "3.75 mld PLN",
                    "description": "Rynek możliwy do obsłużenia (wtrysk specjalistyczny)",
                    "methodology": "Bottom-up + Market filtering",
                    "calculation_steps": [
                        "Segment automotive + elektronika: 4.35 mld PLN",
                        "Technologia wtrysku specjalistycznego: 60% segmentu",
                        "Obszar geograficzny: Polska Centralna i Południowa (70%)",
                        "SAM = 4.35 mld × 0.60 × 0.70 ≈ 3.75 mld PLN"
                    ],
                    "filters_applied": [
                        "Geografia: Polska Centralna i Południowa (dostawa < 500 km)",
                        "Technologia: Wtrysk wysokiej precyzji",
                        "Segmenty: Automotive, Electronics (high-margin)",
                        "Wielkość serii: Średnie i małe serie (100-50,000 szt.)"
                    ],
                    "target_customers": [
                        "Tier 1 i Tier 2 dostawcy automotive (250+ firm)",
                        "Producenci elektroniki użytkowej (120+ firm)",
                        "Medical devices manufacturers (40+ firm)",
                        "Producenci AGD (80+ firm)"
                    ],
                    "competitive_landscape": "150-200 firm w SAM, rozdrobniony rynek"
                },
                "som": {
                    "value": 187500000,
                    "value_formatted": "187.5 mln PLN",
                    "description": "Realny rynek do zdobycia w 3 lata",
                    "methodology": "Realistic market penetration model",
                    "calculation_steps": [
                        "SAM: 3.75 mld PLN",
                        "Docelowy udział rynkowy: 5% (realistyczny dla nowego gracza)",
                        "SOM = 3.75 mld × 0.05 = 187.5 mln PLN",
                        "Timeline: 3 lata (Year 1: 1%, Year 2: 3%, Year 3: 5%)"
                    ],
                    "market_share_target": 0.05,
                    "market_share_formatted": "5% SAM",
                    "timeline": "3 lata",
                    "year_breakdown": [
                        {"year": 1, "revenue": "37.5 mln PLN", "share": "1% SAM", "customers": "15-20 klientów"},
                        {"year": 2, "revenue": "112.5 mln PLN", "share": "3% SAM", "customers": "40-50 klientów"},
                        {"year": 3, "revenue": "187.5 mln PLN", "share": "5% SAM", "customers": "70-80 klientów"}
                    ],
                    "key_assumptions": [
                        "Zespół sprzedaży: 5 osób (rok 1) → 12 osób (rok 3)",
                        "Średnia wartość kontraktu: 2.5 mln PLN rocznie",
                        "Conversion rate: 20% (1 na 5 leadów)",
                        "Customer acquisition cost: 50k PLN",
                        "Churn rate: 10% rocznie",
                        "Przewaga konkurencyjna: jakość + czas dostawy (20% szybciej)"
                    ],
                    "barriers_to_entry": [
                        "Kapitał początkowy: 15-25 mln PLN (maszyny, certyfikaty)",
                        "Czas na certyfikacje: 12-18 miesięcy",
                        "Budowa zespołu: 6-12 miesięcy",
                        "Pierwsi klienci referencyjni: 12 miesięcy"
                    ]
                },
                "funnel_visualization": {
                    "tam_percentage": 100,
                    "sam_percentage": 30,
                    "som_percentage": 1.5,
                    "tam_to_sam_ratio": 0.30,
                    "sam_to_som_ratio": 0.05,
                    "tam_to_som_ratio": 0.015
                },
                "strategic_insights": [
                    "SAM stanowi 30% TAM - segment specjalistyczny z wyższymi marżami (15-25% vs 8-12% w commodity)",
                    "Realistic SOM na poziomie 5% SAM - wymaga 3 lat budowy pozycji i zespołu 12 osób",
                    "Kluczowe segmenty: automotive (60% SOM) i electronics (30% SOM)",
                    "Go-to-market: focus na Tier 2 dostawców (mniejsza konkurencja niż Tier 1)",
                    "Break-even przy 2.5-3% SAM (~100 mln PLN przychodów) w roku 2"
                ],
                "risks_and_challenges": [
                    "Wysoka kapitałochłonność początkowa (15-25 mln PLN)",
                    "Długi cykl sprzedaży (6-12 miesięcy na pierwszą umowę)",
                    "Silna konkurencja od etablowanych graczy z 15+ lat doświadczenia",
                    "Wahania cen surowców (+/- 30%) wpływające na marże",
                    "Zależność od koniunktury w automotive (60% przychodów)"
                ],
                "next_steps": [
                    "Deep dive w 2-3 kluczowe nisze w SAM (np. medical devices, premium automotive)",
                    "Build vs buy analysis (zakup istniejącej firmy vs greenfield)",
                    "Szczegółowa analiza 20 top potencjalnych klientów",
                    "Benchmarking 5-10 głównych konkurentów w SAM",
                    "Financial modeling: 5-year P&L, cash flow, capex plan"
                ],
                "data_sources": [
                    {"name": "Plastics Europe Market Report 2024", "confidence": 0.90},
                    {"name": "GUS Manufacturing Statistics 2023-2024", "confidence": 0.95},
                    {"name": "Polish Chamber of Chemical Industry Database", "confidence": 0.90},
                    {"name": "Automotive Tier 1/2 Suppliers Directory", "confidence": 0.85},
                    {"name": "Market penetration benchmarks (similar industries)", "confidence": 0.80}
                ]
            }
        }, ensure_ascii=False)

    # SWOT analysis request
    elif ("swot" in user_lower or
          ("analiza" in user_lower and ("mocne" in user_lower or "słabe" in user_lower or "szanse" in user_lower or "zagrożenia" in user_lower)) or
          ("strengths" in user_lower and "weaknesses" in user_lower) or
          ("opportunities" in user_lower and "threats" in user_lower)):
        return json.dumps({
            "type": "swot_analysis",
            "data": {
                "company_name": "FADO Sp. z o.o.",
                "nip": "5260016831",
                "krs": "0000145732",
                "industry": "Produkcja tworzyw sztucznych",
                "analysis_date": datetime.utcnow().isoformat(),
                "strengths": [
                    {
                        "title": "Nowoczesny park maszynowy",
                        "description": "Firma posiada 45 wtryskarek o łącznej mocy 5000 ton rocznie, w tym 15 maszyn zakupionych w latach 2020-2023.",
                        "impact": "high",
                        "data_source": "Company website, industry reports"
                    },
                    {
                        "title": "Długoletnie doświadczenie (26 lat na rynku)",
                        "description": "Założona w 1998 roku, firma ma ugruntowaną pozycję i zaufanie klientów w sektorze automotive i elektroniki.",
                        "impact": "high",
                        "data_source": "KRS registry"
                    },
                    {
                        "title": "Stabilna sytuacja finansowa",
                        "description": "Przychody 45,2 mln PLN w 2023 (+12,3% r/r), marża brutto 28,5%, zero zadłużenia długoterminowego.",
                        "impact": "high",
                        "data_source": "Financial statements 2023"
                    },
                    {
                        "title": "Certyfikaty jakości ISO 9001 i ISO 14001",
                        "description": "Posiadanie międzynarodowych certyfikatów potwierdza wysoką jakość procesów i zarządzania środowiskowego.",
                        "impact": "medium",
                        "data_source": "Company website"
                    },
                    {
                        "title": "Wykwalifikowana kadra techniczna",
                        "description": "150 pracowników, w tym 25 inżynierów i 10 technologów z wieloletnim doświadczeniem.",
                        "impact": "medium",
                        "data_source": "Company profile"
                    }
                ],
                "weaknesses": [
                    {
                        "title": "Brak eksportu poza UE",
                        "description": "100% przychodów z rynku polskiego i UE, brak dywersyfikacji geograficznej (USA, Azja).",
                        "impact": "medium",
                        "data_source": "Financial statements, market analysis"
                    },
                    {
                        "title": "Ograniczona automatyzacja procesów",
                        "description": "Tylko 20% linii produkcyjnych w pełni zautomatyzowanych, co zwiększa koszty pracy.",
                        "impact": "medium",
                        "data_source": "Industry benchmarking"
                    },
                    {
                        "title": "Niska rozpoznawalność marki",
                        "description": "Słaba obecność online (1200 followersów LinkedIn), brak aktywnego marketingu B2B.",
                        "impact": "low",
                        "data_source": "Social media analysis"
                    },
                    {
                        "title": "Zależność od sektora automotive (60% przychodów)",
                        "description": "Wysokie ryzyko koncentracji - spowolnienie w motoryzacji bezpośrednio wpływa na wyniki.",
                        "impact": "high",
                        "data_source": "Financial statements breakdown"
                    }
                ],
                "opportunities": [
                    {
                        "title": "Rosnący popyt na bioplastiki",
                        "description": "Rynek bioplastyków rośnie o 15% rocznie, regulacje UE faworyzują materiały biodegradowalne.",
                        "impact": "high",
                        "data_source": "EU market research, Plastics Europe 2024"
                    },
                    {
                        "title": "Ekspansja na rynki wschodnie (Ukraina, kraje bałtyckie)",
                        "description": "Odbudowa Ukrainy stworzy popyt na materiały budowlane i opakowania przemysłowe.",
                        "impact": "high",
                        "data_source": "Market analysis, World Bank forecasts"
                    },
                    {
                        "title": "Rozwój e-commerce napędza popyt na opakowania",
                        "description": "Sektor e-commerce w Polsce rośnie o 20% rocznie, zwiększając zapotrzebowanie na opakowania zabezpieczające.",
                        "impact": "medium",
                        "data_source": "E-commerce market report 2024"
                    },
                    {
                        "title": "Dotacje UE na transformację zieloną",
                        "description": "Fundusze KPO i Horizon Europe dostępne na projekty recyklingu i gospodarki cyrkulacyjnej.",
                        "impact": "medium",
                        "data_source": "EU funding programs"
                    },
                    {
                        "title": "Konsolidacja rynku - możliwości przejęć mniejszych graczy",
                        "description": "Wielu małych producentów boryka się z rosnącymi kosztami energii i może być dostępnych do przejęcia.",
                        "impact": "medium",
                        "data_source": "Industry insider reports"
                    }
                ],
                "threats": [
                    {
                        "title": "Rosnące ceny surowców (+ 35% w 2022-2023)",
                        "description": "Ceny granulatu PET, PP, PE wzrosły znacząco, ciśnienie na marże producentów.",
                        "impact": "high",
                        "data_source": "Commodity price indices"
                    },
                    {
                        "title": "Zaostrzające się regulacje środowiskowe",
                        "description": "SUP Directive, system kaucyjny, podatek od plastiku (0,80 EUR/kg) zwiększają koszty compliance.",
                        "impact": "high",
                        "data_source": "EU regulations, Polish legislation"
                    },
                    {
                        "title": "Konkurencja z krajów azjatyckich (niższe koszty produkcji)",
                        "description": "Producenci z Chin i Wietnamu oferują ceny o 20-30% niższe dzięki tańszej pracy i energii.",
                        "impact": "medium",
                        "data_source": "Competitive analysis"
                    },
                    {
                        "title": "Recesja w sektorze automotive",
                        "description": "Spowolnienie sprzedaży samochodów w Europie (-8% w 2023) bezpośrednio wpływa na popyt na części plastikowe.",
                        "impact": "high",
                        "data_source": "ACEA automotive industry report"
                    },
                    {
                        "title": "Rosnące koszty energii (+ 120% od 2021)",
                        "description": "Produkcja tworzyw sztucznych jest energochłonna, wzrost cen energii znacząco obniża rentowność.",
                        "impact": "high",
                        "data_source": "Energy market data"
                    }
                ],
                "summary": {
                    "total_strengths": 5,
                    "total_weaknesses": 4,
                    "total_opportunities": 5,
                    "total_threats": 5,
                    "overall_assessment": "Firma ma silne fundamenty (nowoczesny park, stabilne finanse), ale musi  adresować zagrożenia zewnętrzne (koszty surowców/energii, regulacje) oraz wykorzystać szanse rynkowe (bioplastiki, ekspansja geograficzna).",
                    "priority_actions": [
                        "Rozważyć inwestycję w linie do produkcji bioplastyków",
                        "Dywersyfikować bazę klientów poza sektor automotive",
                        "Wzmocnić automatyzację procesów dla obniżki kosztów",
                        "Zbadać możliwości ekspansji na Ukrainę i kraje bałtyckie",
                        "Aplikować o dotacje UE na projekty zrównoważonego rozwoju"
                    ]
                },
                "data_sources": [
                    {"name": "KRS", "confidence": 0.95},
                    {"name": "Financial statements 2023", "confidence": 0.95},
                    {"name": "Company website", "confidence": 0.90},
                    {"name": "Plastics Europe market report", "confidence": 0.85},
                    {"name": "EU regulations database", "confidence": 0.95},
                    {"name": "Industry benchmarking", "confidence": 0.80}
                ]
            }
        }, ensure_ascii=False)

    # Financial statements request (detailed balance sheet + income statement)
    elif ("sprawozdanie" in user_lower and "finansow" in user_lower) or \
         ("financial" in user_lower and ("statement" in user_lower or "sprawozdanie" in user_lower)) or \
         ("bilans" in user_lower or "balance sheet" in user_lower) or \
         ("rachunek zysk" in user_lower or "income statement" in user_lower):
        return json.dumps({
            "type": "financial_statements",
            "data": {
                "company_name": "FADO Sp. z o.o.",
                "year": 2023,
                "source": "e-KRS",
                "balance_sheet": {
                    "assets": {
                        "current_assets": {
                            "cash": 12500000,
                            "receivables": 8200000,
                            "inventory": 5400000,
                            "other": 1100000,
                            "total": 27200000
                        },
                        "fixed_assets": {
                            "property_plant_equipment": 32000000,
                            "intangible_assets": 2800000,
                            "long_term_investments": 1500000,
                            "other": 800000,
                            "total": 37100000
                        },
                        "total_assets": 64300000
                    },
                    "liabilities": {
                        "current_liabilities": {
                            "short_term_debt": 4200000,
                            "accounts_payable": 7800000,
                            "accrued_expenses": 1200000,
                            "other": 900000,
                            "total": 14100000
                        },
                        "long_term_liabilities": {
                            "long_term_debt": 12000000,
                            "deferred_tax": 1700000,
                            "other": 600000,
                            "total": 14300000
                        },
                        "total_liabilities": 28400000
                    },
                    "equity": {
                        "share_capital": 5000000,
                        "retained_earnings": 28900000,
                        "reserves": 2000000,
                        "total_equity": 35900000
                    },
                    "total_liabilities_and_equity": 64300000
                },
                "income_statement": {
                    "revenue": {
                        "sales_revenue": 68000000,
                        "other_revenue": 1200000,
                        "total_revenue": 69200000
                    },
                    "costs": {
                        "cost_of_goods_sold": 42000000,
                        "gross_profit": 27200000,
                        "operating_expenses": {
                            "selling_expenses": 8500000,
                            "administrative_expenses": 6200000,
                            "rd_expenses": 2100000,
                            "total": 16800000
                        },
                        "operating_profit": 10400000,
                        "financial_costs": 1800000,
                        "profit_before_tax": 8600000,
                        "income_tax": 2500000,
                        "net_profit": 6100000
                    },
                    "margins": {
                        "gross_margin": 39.3,
                        "operating_margin": 15.0,
                        "net_margin": 8.8
                    }
                },
                "multi_year_summary": {
                    "years": [2020, 2021, 2022, 2023],
                    "revenue": [45000000, 52000000, 61000000, 68000000],
                    "net_profit": [3200000, 4100000, 5200000, 6100000],
                    "total_assets": [48000000, 54000000, 59000000, 64300000],
                    "equity": [28000000, 31000000, 33500000, 35900000]
                },
                "financial_ratios": {
                    "liquidity": {
                        "current_ratio": {
                            "value": 1.93,
                            "benchmark": 1.5,
                            "explanation": "Zdolność do pokrycia zobowiązań krótkoterminowych aktywami obrotowymi. Wartość powyżej 1.5 uznawana jest za bezpieczną."
                        },
                        "quick_ratio": {
                            "value": 1.55,
                            "benchmark": 1.0,
                            "explanation": "Płynność szybka (bez zapasów). Wskaźnik powyżej 1.0 oznacza dobrą zdolność do szybkiego regulowania zobowiązań."
                        }
                    },
                    "profitability": {
                        "roe": {
                            "value": 17.0,
                            "benchmark": 15.0,
                            "explanation": "ROE (Return on Equity) - zwrot z kapitału własnego. Pokazuje efektywność wykorzystania kapitału właścicieli."
                        },
                        "roa": {
                            "value": 9.5,
                            "benchmark": 7.5,
                            "explanation": "ROA (Return on Assets) - zwrot z aktywów. Mierzy jak efektywnie firma wykorzystuje swoje aktywa do generowania zysku."
                        },
                        "ros": {
                            "value": 8.8,
                            "benchmark": 6.0,
                            "explanation": "ROS (Return on Sales) - marża zysku netto. Procent zysku z każdej złotówki przychodu."
                        }
                    },
                    "leverage": {
                        "debt_ratio": {
                            "value": 44.2,
                            "benchmark": 50.0,
                            "explanation": "Wskaźnik zadłużenia ogólnego. Udział zobowiązań w finansowaniu aktywów. Niższy oznacza mniejsze ryzyko."
                        },
                        "debt_to_equity": {
                            "value": 0.79,
                            "benchmark": 1.0,
                            "explanation": "Stosunek długu do kapitału własnego. Wartość poniżej 1.0 oznacza przewagę finansowania kapitałem własnym."
                        }
                    },
                    "efficiency": {
                        "inventory_turnover": {
                            "value": 7.8,
                            "benchmark": 6.0,
                            "explanation": "Rotacja zapasów. Pokazuje ile razy w roku firma odnawia zapasy. Wyższa wartość oznacza lepsze zarządzanie."
                        },
                        "asset_turnover": {
                            "value": 1.08,
                            "benchmark": 0.9,
                            "explanation": "Rotacja aktywów. Efektywność wykorzystania aktywów do generowania przychodów."
                        }
                    }
                },
                "fetched_at": datetime.utcnow().isoformat()
            }
        }, ensure_ascii=False)

    # Financial data request
    elif "finansow" in user_lower or "financial" in user_lower or "przychod" in user_lower or "revenue" in user_lower:
        return json.dumps({
            "type": "data_table",
            "data": {
                "title": "Financial Performance (2020-2023)",
                "columns": [
                    {"key": "year", "label": "Year", "align": "left"},
                    {"key": "revenue", "label": "Revenue (PLN)", "align": "right", "format": "currency"},
                    {"key": "profit", "label": "Net Profit (PLN)", "align": "right", "format": "currency"},
                    {"key": "margin", "label": "Margin (%)", "align": "right", "format": "percent"}
                ],
                "rows": [
                    {"year": "2020", "revenue": 45000000, "profit": 3200000, "margin": 7.11},
                    {"year": "2021", "revenue": 52000000, "profit": 4100000, "margin": 7.88},
                    {"year": "2022", "revenue": 61000000, "profit": 5200000, "margin": 8.52},
                    {"year": "2023", "revenue": 68000000, "profit": 6100000, "margin": 8.97}
                ]
            }
        }, ensure_ascii=False)

    # Company analysis with sources
    elif "analiz" in user_lower or "firma" in user_lower or "company" in user_lower:
        return json.dumps({
            "type": "text_with_sources",
            "data": {
                "text": """FADO Sp. z o.o. jest wiodącym polskim producentem wyrobów z tworzyw sztucznych [1]. Firma została założona w 1995 roku [2] i specjalizuje się w przetwórstwie tworzyw sztucznych oraz wtrysku form [1].

Główne obszary działalności:
- Produkcja podzespołów dla branży motoryzacyjnej [1]
- Komponenty przemysłowe [3]
- Wyroby konsumpcyjne [3]

Firma zatrudnia obecnie 150-200 pracowników [2] i osiąga przychody rzędu 68 milionów PLN rocznie [4].""",
                "sources": [
                    {
                        "id": "src_1",
                        "type": "krs",
                        "title": "KRS - Krajowy Rejestr Sądowy",
                        "url": "https://ekrs.ms.gov.pl/",
                        "confidence": 95,
                        "timestamp": datetime.utcnow().isoformat(),
                        "excerpt": "FADO Sp. z o.o., KRS 0000145732, przedmiot działalności: produkcja wyrobów z tworzyw sztucznych"
                    },
                    {
                        "id": "src_2",
                        "type": "website",
                        "title": "Strona firmowa FADO",
                        "url": "https://fado.com.pl/o-nas",
                        "confidence": 90,
                        "timestamp": datetime.utcnow().isoformat(),
                        "excerpt": "Firma FADO została założona w 1995 roku i zatrudnia 150-200 pracowników"
                    },
                    {
                        "id": "src_3",
                        "type": "website",
                        "title": "Katalog produktów FADO",
                        "url": "https://fado.com.pl/produkty",
                        "confidence": 85,
                        "timestamp": datetime.utcnow().isoformat(),
                        "excerpt": "Oferujemy komponenty przemysłowe i wyroby konsumpcyjne z tworzyw sztucznych"
                    },
                    {
                        "id": "src_4",
                        "type": "document",
                        "title": "Sprawozdanie finansowe 2023",
                        "confidence": 92,
                        "timestamp": datetime.utcnow().isoformat(),
                        "excerpt": "Przychody za 2023 rok: 68 000 000 PLN"
                    }
                ]
            }
        }, ensure_ascii=False)

    elif "raport" in user_lower or "report" in user_lower:
        return """Moge wygenerowac dla Ciebie nastepujace typy raportow:

- **Raport Due Diligence** - kompleksowa analiza przed inwestycja
- **Raport konkurencyjny** - porownanie z konkurentami
- **Raport branzy** - przeglad sektora i trendow
- **Raport finansowy** - szczegolowa analiza finansowa

Ktory typ raportu Cie interesuje?"""

    # News aggregation request
    elif ("news" in user_lower or
          "aktualnosc" in user_lower or
          "aktualnos" in user_lower or
          "newsy" in user_lower or
          "wiadomosc" in user_lower or
          "artykul" in user_lower):

        # Extract company name/identifier
        company_name = "FADO"  # Default for testing
        company_id = "1"  # FADO's ID

        # Try to extract company name from message
        if "fado" in user_lower:
            company_name = "FADO"
            company_id = "1"
        elif "splast" in user_lower:
            company_name = "Splast"
            company_id = "2"
        elif "techsoft" in user_lower:
            company_name = "TechSoft"
            company_id = "3"

        # Import news data
        from app.api.v1.endpoints.companies import MOCK_COMPANY_NEWS

        # Get news articles for the company
        all_news = MOCK_COMPANY_NEWS.get(company_id, [])

        # Limit to 6 most recent articles
        news_items = all_news[:6]

        # Format articles for display
        articles = []
        for article in news_items:
            articles.append({
                "id": article["id"],
                "title": article["title"],
                "summary": article["summary"],
                "source": article["source"],
                "source_url": article["source_url"],
                "published_at": article["published_at"],
                "sentiment": article["sentiment"],
                "category": article["category"],
                "days_ago": (datetime.now() - datetime.fromisoformat(article["published_at"])).days
            })

        # Calculate stats
        total_articles = len(articles)
        positive_count = sum(1 for a in articles if a["sentiment"] == "positive")
        negative_count = sum(1 for a in articles if a["sentiment"] == "negative")
        neutral_count = sum(1 for a in articles if a["sentiment"] == "neutral")

        # Count unique sources
        unique_sources = len(set(a["source"] for a in articles))

        # Most recent article age
        most_recent_days = min((a["days_ago"] for a in articles), default=0)

        return json.dumps({
            "type": "news_feed",
            "data": {
                "company_name": company_name,
                "company_id": company_id,
                "articles": articles,
                "summary": {
                    "total_articles": total_articles,
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count,
                    "unique_sources": unique_sources,
                    "most_recent_days": most_recent_days,
                    "date_range": f"Last {max((a['days_ago'] for a in articles), default=0)} days"
                },
                "fetched_at": datetime.utcnow().isoformat()
            }
        }, ensure_ascii=False)

    elif "pomoc" in user_lower or "help" in user_lower:
        return """Jestem asystentem MI-Navigator do analizy rynkowej i badania firm. Moge pomoc Ci:

- Analizowac firmy na podstawie nazwy, NIP lub URL
- Generowac raporty Due Diligence
- Monitorowac konkurencje
- Badac trendy rynkowe
- Porownywac firmy w branzy

Jak moge Ci dzis pomoc?"""

    else:
        return f"""Dziekuje za wiadomosc. Jestem asystentem Market Intelligence i pomagam w:

- Analizie firm i konkurencji
- Tworzeniu raportow biznesowych
- Monitorowaniu rynku

Czy chcialbys przeprowadzic analize konkretnej firmy lub uzyskac raport? Podaj wiecej szczegolow, a chetnie pomoge."""


def map_preferred_depth_to_analysis_depth(preferred_depth: str) -> str:
    """
    Map user's preferred depth setting to analysis depth value.

    User preferences: quick, standard, deep
    Analysis options: executive_summary, standard, detailed, exhaustive
    """
    mapping = {
        "quick": "executive_summary",
        "standard": "standard",
        "deep": "detailed"
    }
    return mapping.get(preferred_depth, "standard")


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: str = None
):
    """WebSocket endpoint for real-time chat.

    Authorization via query parameter: ?token=YOUR_JWT_TOKEN
    """
    # Accept connection first
    await websocket.accept()

    try:
        # Get user from token if provided
        current_user = None
        if token:
            try:
                from app.db.session import AsyncSessionLocal
                token_data = AuthService.decode_token(token)
                if token_data and token_data.type == "access":
                    async with AsyncSessionLocal() as db:
                        current_user = await AuthService.get_user_by_id(db, token_data.sub)
                        if current_user:
                            print(f"[WS DEBUG] User authenticated: {current_user.email}, preferred_depth: {current_user.preferred_depth}")
                        else:
                            print("[WS DEBUG] User not found after token decode")
            except Exception as e:
                print(f"[WS DEBUG] Error getting user from token: {e}")
                pass  # Continue without user in development mode
        else:
            print("[WS DEBUG] No token provided")

        while True:
            data = await websocket.receive_text()

            # Parse message (supports both plain text and JSON format)
            try:
                import json
                message_data = json.loads(data)
                content = message_data.get("content", "")
                file_ids = message_data.get("file_ids", [])
                brief_answer = message_data.get("brief_answer")  # For brief collection responses
                plan_action = message_data.get("plan_action")  # For plan confirmation
            except (json.JSONDecodeError, AttributeError):
                # Fallback to plain text
                content = data
                file_ids = []
                brief_answer = None
                plan_action = None

            # Get conversation from store
            conv = conversations_store.get(conversation_id)

            # Initialize brief metadata if not exists
            if conv and "brief" not in conv:
                conv["brief"] = {}

            # Handle brief collection responses
            if conv and brief_answer:
                question_id = message_data.get("question_id")
                conv["brief"][question_id] = brief_answer

                # Continue brief collection flow
                if question_id == "objective":
                    # Ask scope question
                    await websocket.send_json({
                        "type": "brief_question",
                        "data": {
                            "question_id": "scope",
                            "question": "What is the scope of your research?",
                            "description": "Define the breadth and boundaries of the research",
                            "options": [
                                {"value": "company_only", "label": "Company only", "description": "Focus solely on the target company"},
                                {"value": "market_context", "label": "Company + Market context", "description": "Company analysis with market overview"},
                                {"value": "competitive", "label": "Competitive landscape", "description": "Company, competitors, and market dynamics"},
                                {"value": "industry_deep_dive", "label": "Full industry deep dive", "description": "Comprehensive industry, market, and ecosystem analysis"}
                            ]
                        }
                    })
                    continue  # Wait for next response

                elif question_id == "scope":
                    # Ask depth question with user's default preference
                    # Map user's preferred_depth setting to depth values
                    default_depth = "standard"  # Default fallback
                    if current_user and current_user.preferred_depth:
                        depth_mapping = {
                            "quick": "executive_summary",
                            "standard": "standard",
                            "deep": "detailed"
                        }
                        default_depth = depth_mapping.get(current_user.preferred_depth, "standard")
                        print(f"[DEPTH DEBUG] User {current_user.email} preferred_depth: {current_user.preferred_depth} -> default_depth: {default_depth}")
                    else:
                        print(f"[DEPTH DEBUG] No current_user or preferred_depth, using fallback: {default_depth}")

                    # Build options with default marked
                    options = [
                        {"value": "executive_summary", "label": "Executive Summary", "description": "Key insights and highlights only (5-10 min)", "default": default_depth == "executive_summary"},
                        {"value": "standard", "label": "Standard Analysis", "description": "Balanced detail with actionable insights (15-20 min)", "default": default_depth == "standard"},
                        {"value": "detailed", "label": "Detailed Report", "description": "Comprehensive analysis with supporting data (30-45 min)", "default": default_depth == "detailed"},
                        {"value": "exhaustive", "label": "Exhaustive Research", "description": "Deep dive with all available data (1-2 hours)", "default": default_depth == "exhaustive"}
                    ]

                    await websocket.send_json({
                        "type": "brief_question",
                        "data": {
                            "question_id": "depth",
                            "question": "What level of detail do you need?",
                            "description": "Choose the depth of analysis required",
                            "options": options
                        }
                    })
                    continue  # Wait for next response

                elif question_id == "depth":
                    # Brief collection complete - generate plan
                    objective = conv["brief"].get("objective", "")
                    scope = conv["brief"].get("scope", "standard")
                    depth = conv["brief"].get("depth", "standard")

                    # Generate research plan based on brief
                    plan_steps = []

                    # Step 1: Always gather basic data
                    plan_steps.append({
                        "phase": "Data Collection",
                        "description": "Gather company data from official sources (KRS, financial reports, website)",
                        "estimated_time": "2-3 minutes"
                    })

                    # Add steps based on scope
                    if scope in ["market_context", "competitive", "industry_deep_dive"]:
                        plan_steps.append({
                            "phase": "Market Analysis",
                            "description": "Analyze market size, trends, and growth drivers",
                            "estimated_time": "3-5 minutes"
                        })

                    if scope in ["competitive", "industry_deep_dive"]:
                        plan_steps.append({
                            "phase": "Competitive Analysis",
                            "description": "Identify and analyze key competitors",
                            "estimated_time": "5-7 minutes"
                        })

                    if scope == "industry_deep_dive":
                        plan_steps.append({
                            "phase": "Industry Ecosystem",
                            "description": "Map value chain, suppliers, customers, and industry dynamics",
                            "estimated_time": "7-10 minutes"
                        })

                    # Add synthesis step based on depth
                    if depth == "executive_summary":
                        plan_steps.append({
                            "phase": "Executive Summary",
                            "description": "Synthesize key findings and recommendations",
                            "estimated_time": "2-3 minutes"
                        })
                    elif depth in ["standard", "detailed"]:
                        plan_steps.append({
                            "phase": "Analysis & Synthesis",
                            "description": "Detailed analysis with insights and recommendations",
                            "estimated_time": "5-8 minutes"
                        })
                    else:  # exhaustive
                        plan_steps.append({
                            "phase": "Comprehensive Report",
                            "description": "In-depth analysis with all supporting data and cross-references",
                            "estimated_time": "15-20 minutes"
                        })

                    # Send generated plan
                    await websocket.send_json({
                        "type": "plan",
                        "data": {
                            "plan_id": str(uuid.uuid4()),
                            "objective": objective,
                            "scope": scope,
                            "depth": depth,
                            "steps": plan_steps,
                            "total_estimated_time": sum([int(step["estimated_time"].split("-")[0]) for step in plan_steps]),
                            "message": "Here's your research plan based on your requirements. You can proceed or modify it."
                        }
                    })
                    continue  # Wait for plan confirmation

            # Handle plan confirmation
            if conv and plan_action:
                if plan_action == "confirm":
                    # User confirmed plan - proceed with research using ORIGINAL user message
                    # NOT the brief objective, because we need the original query (with NIP, URL, etc.)
                    if conv.get("original_query"):
                        content = conv["original_query"]
                    # Set flag to start research
                    conv["research_confirmed"] = True
                elif plan_action == "modify":
                    # User wants to modify - get modifications
                    modifications = message_data.get("modifications", "")
                    conv["brief"]["modifications"] = modifications
                    # Regenerate plan (simplified - in real impl would adjust based on modifications)
                    await websocket.send_text(f"Plan modified based on your feedback: {modifications}\n\nProceeding with adjusted research...")
                    conv["research_confirmed"] = True
                else:  # cancel
                    await websocket.send_text("Research cancelled. Feel free to start a new query.")
                    continue

            # Check usage limit before processing message
            if current_user and content and conv:
                try:
                    from app.db.session import AsyncSessionLocal
                    async with AsyncSessionLocal() as db:
                        await check_usage_limit(db, current_user, action_type="chat")
                except HTTPException as e:
                    # Send usage limit error to client
                    await websocket.send_json({
                        "type": "error",
                        "data": e.detail
                    })
                    continue  # Skip processing this message

            # Save user message to conversation store
            if conv and content:  # Only save if there's actual content (not just brief answers)
                user_msg_id = str(uuid.uuid4())
                now = datetime.utcnow()
                user_message = {
                    "id": user_msg_id,
                    "role": "user",
                    "content": content,
                    "created_at": now.isoformat(),
                    "file_ids": file_ids if file_ids else None
                }
                conv["messages"].append(user_message)
                conv["updated_at"] = now.isoformat()

                # Update conversation title if first message
                if conv["title"] is None:
                    conv["title"] = content[:50] + ("..." if len(content) > 50 else "")

                # Check if this is first research query (trigger brief collection)
                is_new_research = len(conv["messages"]) == 1 and any(keyword in content.lower() for keyword in [
                    'analyze', 'research', 'due diligence', 'investigate', 'report', 'analysis'
                ])

                if is_new_research and ("brief" not in conv or not conv.get("brief")):
                    # Start brief collection flow
                    conv["brief"] = {}
                    # Save original query for later use (after plan confirmation)
                    conv["original_query"] = content
                    await websocket.send_json({
                        "type": "brief_question",
                        "data": {
                            "question_id": "objective",
                            "question": "What is the main objective of your research?",
                            "description": "Help us understand what you're trying to achieve",
                            "input_type": "text",
                            "placeholder": "e.g., Evaluate company for investment, competitive intelligence, due diligence..."
                        }
                    })
                    continue  # Wait for user response before proceeding

            # Send progress updates for comprehensive research
            import asyncio

            # Detect if this is a comprehensive research request
            is_comprehensive = any(keyword in content.lower() for keyword in [
                'analyze', 'research', 'due diligence', 'comprehensive', 'detailed',
                'deep dive', 'full analysis', 'investigate', 'report'
            ])

            # Detect if this is a deep research request with checkpoints
            is_deep_research = any(keyword in content.lower() for keyword in [
                'deep research', 'deep dive', 'due diligence'
            ])

            if is_comprehensive:
                # Phase 1: Data Collection
                await websocket.send_json({
                    "type": "progress",
                    "data": {
                        "percentage": 10,
                        "phase": "Data Collection",
                        "message": "Gathering company data from multiple sources...",
                        "estimated_time_remaining": "4-5 seconds"
                    }
                })
                await asyncio.sleep(1.5)

                # CHECKPOINT: Deep research pause after data collection
                if is_deep_research:
                    # Send partial results
                    partial_results = {
                        "company_name": "FADO Sp. z o.o.",
                        "nip": "5260016831",
                        "status": "active",
                        "revenue_2023": "15.2M PLN",
                        "employees": "120-150",
                        "sources_gathered": 5
                    }

                    await websocket.send_json({
                        "type": "checkpoint",
                        "data": {
                            "checkpoint_id": str(uuid.uuid4()),
                            "phase": "Data Collection Complete",
                            "message": "Initial data gathered. Would you like to continue with full analysis?",
                            "partial_results": partial_results,
                            "options": [
                                {"id": "continue", "label": "Continue", "description": "Proceed with full financial and market analysis"},
                                {"id": "review", "label": "Review", "description": "Review partial results before continuing"},
                                {"id": "modify", "label": "Modify Scope", "description": "Adjust research scope or focus areas"}
                            ]
                        }
                    })

                    # Wait for user response (timeout after 60 seconds)
                    import asyncio
                    try:
                        user_response = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                        response_data = json.loads(user_response)
                        checkpoint_action = response_data.get("checkpoint_action", "continue")

                        if checkpoint_action == "modify":
                            # User wants to modify scope
                            modified_scope = response_data.get("modified_scope", "")
                            # Update content with modifications
                            content = f"{content}\n\nModified scope: {modified_scope}"

                        elif checkpoint_action == "review":
                            # User wants to review - just send acknowledgement
                            await websocket.send_text("Continuing after review...")
                            await asyncio.sleep(0.5)

                        # If "continue" or after review/modify, proceed
                    except asyncio.TimeoutError:
                        # Auto-continue after timeout
                        await websocket.send_text("No response received. Auto-continuing research...")
                        await asyncio.sleep(0.5)

                # Phase 2: Analysis
                await websocket.send_json({
                    "type": "progress",
                    "data": {
                        "percentage": 35,
                        "phase": "Financial Analysis",
                        "message": "Analyzing financial statements and trends...",
                        "estimated_time_remaining": "3-4 seconds"
                    }
                })
                await asyncio.sleep(1.5)

                # Phase 3: Market Research
                await websocket.send_json({
                    "type": "progress",
                    "data": {
                        "percentage": 60,
                        "phase": "Market Research",
                        "message": "Researching market position and competitors...",
                        "estimated_time_remaining": "2-3 seconds"
                    }
                })
                await asyncio.sleep(1.5)

                # Phase 4: Synthesis
                await websocket.send_json({
                    "type": "progress",
                    "data": {
                        "percentage": 85,
                        "phase": "Report Generation",
                        "message": "Synthesizing findings and generating report...",
                        "estimated_time_remaining": "1-2 seconds"
                    }
                })
                await asyncio.sleep(1.5)

            # Get user industry from conversation metadata (MVP: use hardcoded for demo)
            # In production, this should be fetched from user profile via token
            user_industry = conv.get("user_industry", "manufacturing") if conv else "manufacturing"
            user_industry_segment = conv.get("user_industry_segment", "plastics_processing") if conv else "plastics_processing"

            # Check if this is a "standard analysis" (from brief collection)
            is_standard_analysis = False
            if conv and conv.get("brief") and conv.get("brief").get("depth") == "standard":
                is_standard_analysis = True

            # For standard analysis, send multiple sections progressively
            if is_comprehensive and is_standard_analysis:
                # Section 1: Data Collection (sent after Phase 1)
                section1_response = generate_mock_response(content, user_industry, user_industry_segment)
                await websocket.send_json(json.loads(section1_response))
                if conv:
                    ai_msg_id = str(uuid.uuid4())
                    conv["messages"].append({
                        "id": ai_msg_id,
                        "role": "assistant",
                        "content": section1_response,
                        "created_at": datetime.utcnow().isoformat()
                    })
                await asyncio.sleep(0.5)

                # Section 2: Market Analysis (sent after Phase 3 - Market Research at 60%)
                section2_text = """
## Analiza Rynku

### Wielkość rynku tworzyw sztucznych w Polsce
Rynek przetwórstwa tworzyw sztucznych w Polsce jest wyceniany na około **8,5 mld EUR rocznie** [1]. Sektor ten zatrudnia ponad 180 tys. osób w około 3 200 firmach [2].

**Kluczowe segmenty:**
- Branża motoryzacyjna: 35% rynku (największy odbiorca)
- Przemysł budowlany: 25% rynku
- Opakowania: 20% rynku
- Elektronika i AGD: 12% rynku
- Pozostałe: 8% rynku

### Trendy wzrostowe
- **Wzrost CAGR:** 4,2% rocznie (2020-2025) [1]
- **Driverzy wzrostu:**
  - Rosnące zapotrzebowanie sektora automotive (elektromobilność)
  - Rozwój e-commerce → więcej opakowań
  - Inwestycje w automatyzację produkcji
  - Green plastics i recykling (regulacje UE)

### Pozycja konkurencyjna
FADO znajduje się w **TOP 20% producentów** pod względem wielkości produkcji [3]. Główni konkurenci:
- **POLIMER SA** - przychody 85M PLN, 220 pracowników
- **TECHNOPLAST Sp. z o.o.** - przychody 62M PLN, 180 pracowników
- **SPLAST Group** - przychody 120M PLN, 300 pracowników

**Przewaga konkurencyjna FADO:**
- Specjalizacja w branży automotive (stabilny popyt)
- Certyfikaty ISO 9001, IATF 16949, ISO 14001
- Nowoczesny park maszynowy (ostatnia modernizacja: 2024)
- Lokalizacja blisko głównych odbiorców (Volkswagen Poznań, Stellantis Gliwice)

**Źródła:**
[1] Raport Polskiej Izby Przemysłu Chemicznego 2024
[2] GUS - Rocznik Statystyczny Przemysłu 2024
[3] Ranking Polityki Insight "Producenci tworzyw sztucznych 2024"
"""
                section2_response = {
                    "type": "text_with_sources",
                    "data": {
                        "text": section2_text.strip(),
                        "sources": [
                            {
                                "id": "src_market_1",
                                "type": "report",
                                "title": "Raport Polskiej Izby Przemysłu Chemicznego 2024",
                                "url": "https://pipc.org.pl/raporty/rynek-tworzyw-2024",
                                "confidence": 92,
                                "timestamp": datetime.utcnow().isoformat(),
                                "excerpt": "Rynek przetwórstwa tworzyw sztucznych w Polsce - 8,5 mld EUR, wzrost CAGR 4,2%"
                            },
                            {
                                "id": "src_market_2",
                                "type": "government",
                                "title": "GUS - Rocznik Statystyczny Przemysłu 2024",
                                "url": "https://stat.gov.pl/",
                                "confidence": 95,
                                "timestamp": datetime.utcnow().isoformat(),
                                "excerpt": "Sektor tworzyw sztucznych: 180 tys. pracowników, 3 200 firm"
                            },
                            {
                                "id": "src_market_3",
                                "type": "media",
                                "title": "Ranking Polityki Insight - Producenci tworzyw 2024",
                                "url": "https://polityka-insight.pl/rankings/plastics-2024",
                                "confidence": 88,
                                "timestamp": datetime.utcnow().isoformat(),
                                "excerpt": "TOP 100 producentów tworzyw sztucznych w Polsce"
                            }
                        ]
                    }
                }
                await websocket.send_json(section2_response)
                if conv:
                    ai_msg_id = str(uuid.uuid4())
                    conv["messages"].append({
                        "id": ai_msg_id,
                        "role": "assistant",
                        "content": json.dumps(section2_response, ensure_ascii=False),
                        "created_at": datetime.utcnow().isoformat()
                    })
                await asyncio.sleep(0.5)

                # Section 3: Analysis & Synthesis (sent after Phase 4 - Report Generation at 85%)
                section3_text = """
## Analiza i Synteza

### Kluczowe wnioski
1. **Silna pozycja rynkowa:** FADO należy do TOP 20% producentów w Polsce, z przychodami 68M PLN i rosnącym udziałem w rynku automotive
2. **Stabilność finansowa:** Marża zysku netto 8,2%, niskie zadłużenie (32%), wysoki ROE (18,2%) - wszystkie wskaźniki powyżej średniej branżowej
3. **Certyfikacje i jakość:** Pełny zestaw certyfikatów dla branży automotive (IATF 16949) i środowiskowych (ISO 14001)
4. **Nowoczesna infrastruktura:** Ostatnia modernizacja parku maszynowego w 2024 roku (inwestycja 5M PLN)

### Szanse (Opportunities)
- **Elektromobilność:** Rosnący popyt na komponenty do pojazdów elektrycznych (baterie, systemy chłodzenia)
- **Ekspansja geograficzna:** Potencjał rozwoju w CEE (Czechy, Słowacja, Węgry)
- **Recykling i green plastics:** Rosnące wymagania UE = nowe modele biznesowe
- **Automatyzacja:** Dalsze inwestycje w Industry 4.0 → większa efektywność

### Ryzyka (Threats)
- **Ceny surowców:** Wahania cen polipropylenu i ABS (zależność od cen ropy)
- **Presja kosztowa:** Rosnące koszty energii i pracy
- **Konkurencja międzynarodowa:** Producenci z Azji (Chiny, Indie) z niższymi kosztami
- **Regulacje środowiskowe:** Coraz bardziej restrykcyjne przepisy UE dotyczące plastiku

### Rekomendacje strategiczne

**1. Dywersyfikacja portfolio (Priorytet: WYSOKI)**
- Rozwój produktów z recyklingu (r-PP, r-ABS)
- Wejście w segment bio-plastików
- Cel: 20% przychodów z "green products" do 2027

**2. Ekspansja na rynki CEE (Priorytet: ŚREDNI)**
- Otworzenie biura sprzedaży w Czechach (2026)
- Partnerstwa z lokalnymi dystrybutorami
- Cel: +15% przychodów z eksportu do 2028

**3. Automatyzacja i digitalizacja (Priorytet: WYSOKI)**
- Implementacja systemu MES (Manufacturing Execution System)
- Predykcyjna konserwacja maszyn (AI/IoT)
- Cel: +10% efektywności OEE do 2026

**4. Hedging surowcowy (Priorytet: ŚREDNI)**
- Kontrakty forward na kluczowe surowce
- Dywersyfikacja dostawców (obecnie 3 głównych)
- Cel: stabilizacja marży przy wahaniach cen ±15%

### Ocena ogólna
**Rating:** 7.8/10

**Uzasadnienie:**
FADO to solidny, dobrze zarządzany producent z silną pozycją w automotive. Firma ma zdrowe finanse, nowoczesną infrastrukturę i odpowiednie certyfikaty. Główne ryzyka to presja kosztowa i rosnąca konkurencja, ale szanse związane z elektromobilnością i green plastics mogą je zrównoważyć.

**Rekomendacja:**
- **Dla inwestorów:** Stabilna opcja z umiarkowanym potencjałem wzrostu (15-20% w 3 lata)
- **Dla partnerów biznesowych:** Wiarygodny dostawca z udokumentowaną jakością
- **Dla konkurentów:** Godny przeciwnik - nie lekceważyć, ale możliwe obszary współpracy (np. recykling)
"""
                section3_response = {
                    "type": "text_with_sources",
                    "data": {
                        "text": section3_text.strip(),
                        "sources": []
                    }
                }
                await websocket.send_json(section3_response)
                if conv:
                    ai_msg_id = str(uuid.uuid4())
                    conv["messages"].append({
                        "id": ai_msg_id,
                        "role": "assistant",
                        "content": json.dumps(section3_response, ensure_ascii=False),
                        "created_at": datetime.utcnow().isoformat()
                    })
                await asyncio.sleep(0.3)

                # Send completion progress
                await websocket.send_json({
                    "type": "progress",
                    "data": {
                        "percentage": 100,
                        "phase": "Complete",
                        "message": "Analysis complete!",
                        "estimated_time_remaining": "0 seconds"
                    }
                })

            else:
                # Non-standard analysis OR non-comprehensive - original single response behavior
                # Generate mock response (mention files if present)
                if file_ids:
                    response = f"Otrzymałem Twoją wiadomość z {len(file_ids)} załączonym plikiem/plikami.\n\n"
                    response += generate_mock_response(content, user_industry, user_industry_segment)
                    response += f"\n\n[Uwaga: Przetwarzanie plików jest w trakcie implementacji. ID plików: {', '.join(file_ids[:3])}...]"
                else:
                    response = generate_mock_response(content, user_industry, user_industry_segment)

                # Send completion progress
                if is_comprehensive:
                    await websocket.send_json({
                        "type": "progress",
                        "data": {
                            "percentage": 100,
                            "phase": "Complete",
                            "message": "Analysis complete!",
                            "estimated_time_remaining": "0 seconds"
                        }
                    })
                    await asyncio.sleep(0.2)

                # Save AI response to conversation store
                if conv:
                    ai_msg_id = str(uuid.uuid4())
                    ai_message = {
                        "id": ai_msg_id,
                        "role": "assistant",
                        "content": response,
                        "created_at": datetime.utcnow().isoformat()
                    }
                    conv["messages"].append(ai_message)

                # Check if response is JSON (structured message)
                try:
                    response_data = json.loads(response)
                    # If it's a dict with 'type' and 'data', send as JSON
                    if isinstance(response_data, dict) and 'type' in response_data and 'data' in response_data:
                        await websocket.send_json(response_data)
                    else:
                        await websocket.send_text(response)
                except (json.JSONDecodeError, ValueError):
                    # Not JSON, send as plain text
                    await websocket.send_text(response)
    except WebSocketDisconnect:
        pass
