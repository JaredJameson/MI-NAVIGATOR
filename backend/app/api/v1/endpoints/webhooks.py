"""
Webhook API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel, HttpUrl

from app.db.session import get_db
from app.models.user import User
from app.models.webhook import Webhook, WebhookEvent, WebhookStatus
from app.services.webhook_service import WebhookService
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


# Schemas
class WebhookCreate(BaseModel):
    """Schema for creating a webhook."""
    url: HttpUrl
    event_type: WebhookEvent
    max_retries: int = 5


class WebhookUpdate(BaseModel):
    """Schema for updating a webhook."""
    is_active: bool


class WebhookResponse(BaseModel):
    """Schema for webhook response."""
    id: str
    user_id: str
    url: str
    event_type: WebhookEvent
    secret: str | None = None  # HMAC secret for signature verification
    is_active: bool
    max_retries: int
    retry_count: int
    status: WebhookStatus
    last_triggered_at: str | None = None
    last_delivered_at: str | None = None
    last_error: str | None = None
    next_retry_at: str | None = None
    created_at: str

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        """Convert ORM object to Pydantic model with proper type conversions."""
        return cls(
            id=str(obj.id),
            user_id=str(obj.user_id),
            url=obj.url,
            event_type=obj.event_type,
            secret=obj.secret,
            is_active=obj.is_active,
            max_retries=obj.max_retries,
            retry_count=obj.retry_count or 0,
            status=obj.status,
            last_triggered_at=obj.last_triggered_at.isoformat() if obj.last_triggered_at else None,
            last_delivered_at=obj.last_delivered_at.isoformat() if obj.last_delivered_at else None,
            last_error=obj.last_error,
            next_retry_at=obj.next_retry_at.isoformat() if obj.next_retry_at else None,
            created_at=obj.created_at.isoformat() if obj.created_at else ""
        )


class WebhookTestPayload(BaseModel):
    """Schema for testing webhook."""
    payload: dict = {"test": "data", "event": "manual_trigger"}


@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    webhook_data: WebhookCreate,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new webhook."""
    service = WebhookService(db)
    webhook = service.create_webhook(
        user_id=str(current_user.id),
        url=str(webhook_data.url),
        event_type=webhook_data.event_type,
        max_retries=webhook_data.max_retries
    )
    return WebhookResponse.from_orm(webhook)


@router.get("/", response_model=List[WebhookResponse])
async def list_webhooks(
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all webhooks for current user."""
    service = WebhookService(db)
    webhooks = await service.list_webhooks(str(current_user.id))
    return [WebhookResponse.from_orm(w) for w in webhooks]


@router.get("/{webhook_id}", response_model=WebhookResponse)
async def get_webhook(
    webhook_id: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific webhook."""
    service = WebhookService(db)
    webhook = await service.get_webhook(webhook_id, str(current_user.id))
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    return WebhookResponse.from_orm(webhook)


@router.patch("/{webhook_id}", response_model=WebhookResponse)
async def update_webhook(
    webhook_id: str,
    webhook_data: WebhookUpdate,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update webhook status (enable/disable)."""
    service = WebhookService(db)

    # Verify ownership
    webhook = await service.get_webhook(webhook_id, str(current_user.id))
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )

    updated_webhook = service.update_webhook_status(
        webhook_id,
        webhook_data.is_active
    )
    return updated_webhook


@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: str,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a webhook."""
    service = WebhookService(db)
    success = service.delete_webhook(webhook_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )


@router.post("/{webhook_id}/test", response_model=dict)
async def test_webhook(
    webhook_id: str,
    test_data: WebhookTestPayload,
    db = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger a webhook for testing.

    This endpoint allows testing webhook delivery without waiting for actual events.
    """
    service = WebhookService(db)

    # Verify ownership
    webhook = await service.get_webhook(webhook_id, str(current_user.id))
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )

    # Trigger webhook with test payload
    await service._deliver_webhook(webhook, test_data.payload)

    return {
        "message": "Webhook test triggered",
        "webhook_id": webhook_id,
        "status": webhook.status.value,
        "retry_count": webhook.retry_count,
        "last_error": webhook.last_error
    }
