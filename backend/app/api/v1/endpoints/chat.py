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

    # Company profile request
    if ("profil" in user_lower or "profile" in user_lower) and ("firma" in user_lower or "company" in user_lower):
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

            await websocket.send_text(response)
    except WebSocketDisconnect:
        pass
