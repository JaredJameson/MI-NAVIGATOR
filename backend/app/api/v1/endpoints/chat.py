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
from app.api.v1.endpoints.auth import get_current_user

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
async def list_conversations(current_user = Depends(get_current_user)):
    """List user's chat conversations."""
    user_id = str(current_user.id)
    user_convs = [c for c in conversations_store.values() if c.get("user_id") == user_id]
    return [ConversationResponse(**{k: v for k, v in c.items() if k != "user_id"}) for c in user_convs]


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(current_user = Depends(get_current_user)):
    """Create a new chat conversation."""
    conv_id = str(uuid.uuid4())
    now = datetime.utcnow()
    conversation = {
        "id": conv_id,
        "user_id": str(current_user.id),
        "title": None,
        "messages": [],
        "created_at": now,
        "updated_at": now
    }
    conversations_store[conv_id] = conversation
    return ConversationResponse(**{k: v for k, v in conversation.items() if k != "user_id"})


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str, current_user = Depends(get_current_user)):
    """Get conversation details with messages."""
    conv = conversations_store.get(conversation_id)
    if not conv or conv.get("user_id") != str(current_user.id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationResponse(**{k: v for k, v in conv.items() if k != "user_id"})


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    message: MessageCreate,
    current_user = Depends(get_current_user)
):
    """Send a message in conversation and get AI response."""
    conv = conversations_store.get(conversation_id)
    if not conv or conv.get("user_id") != str(current_user.id):
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


def generate_mock_response(user_message: str) -> str:
    """Generate a mock AI response based on user message."""
    import json
    import re
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

    # Company profile request
    elif ("profil" in user_lower or "profile" in user_lower) and ("firma" in user_lower or "company" in user_lower):
        return json.dumps({
            "type": "company_card",
            "data": {
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
        # Optional: Add token validation here if needed
        # For now, accept all connections for development

        while True:
            data = await websocket.receive_text()

            # Parse message (supports both plain text and JSON format)
            try:
                import json
                message_data = json.loads(data)
                content = message_data.get("content", "")
                file_ids = message_data.get("file_ids", [])
            except (json.JSONDecodeError, AttributeError):
                # Fallback to plain text
                content = data
                file_ids = []

            # Save user message to conversation store
            conv = conversations_store.get(conversation_id)
            if conv:
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

            # Generate mock response (mention files if present)
            if file_ids:
                response = f"Otrzymałem Twoją wiadomość z {len(file_ids)} załączonym plikiem/plikami.\n\n"
                response += generate_mock_response(content)
                response += f"\n\n[Uwaga: Przetwarzanie plików jest w trakcie implementacji. ID plików: {', '.join(file_ids[:3])}...]"
            else:
                response = generate_mock_response(content)

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
