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
    user_lower = user_message.lower()

    if "analiz" in user_lower or "firma" in user_lower or "company" in user_lower:
        return """Rozumiem, ze chcesz przeprowadzic analize firmy. Moge pomoc Ci w nastepujacych obszarach:

1. **Analiza finansowa** - przychody, rentownosc, zadluzenie
2. **Analiza rynkowa** - pozycja konkurencyjna, udzial w rynku
3. **Due diligence** - kompleksowa ocena przed transakcja
4. **Monitoring konkurencji** - sledzenie dzialan konkurentow

Podaj nazwe firmy lub jej NIP, a rozpoczne analize."""

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
