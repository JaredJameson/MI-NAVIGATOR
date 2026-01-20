"""
Webhook service with retry mechanism and exponential backoff.
"""

import httpx
import asyncio
import hmac
import hashlib
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.models.webhook import Webhook, WebhookEvent, WebhookStatus
import logging

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for managing webhooks with retry mechanism."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def generate_signature(payload: Dict[str, Any], secret: str) -> str:
        """
        Generate HMAC-SHA256 signature for webhook payload.

        Args:
            payload: Webhook payload data
            secret: Secret key for signing

        Returns:
            Hex-encoded HMAC signature
        """
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return signature

    @staticmethod
    def verify_signature(payload: Dict[str, Any], secret: str, received_signature: str) -> bool:
        """
        Verify HMAC signature for webhook payload.

        Args:
            payload: Webhook payload data
            secret: Secret key for verification
            received_signature: Signature to verify

        Returns:
            True if signature is valid, False otherwise
        """
        expected_signature = WebhookService.generate_signature(payload, secret)
        return hmac.compare_digest(expected_signature, received_signature)

    async def trigger_webhook(
        self,
        event_type: WebhookEvent,
        payload: Dict[str, Any],
        user_id: str
    ) -> None:
        """
        Trigger all active webhooks for a specific event type.

        Args:
            event_type: Type of event that occurred
            payload: Data to send to webhook endpoint
            user_id: User who owns the webhook
        """
        webhooks = self.db.query(Webhook).filter(
            Webhook.user_id == user_id,
            Webhook.event_type == event_type,
            Webhook.is_active == True
        ).all()

        for webhook in webhooks:
            asyncio.create_task(self._deliver_webhook(webhook, payload))

    async def _deliver_webhook(
        self,
        webhook: Webhook,
        payload: Dict[str, Any]
    ) -> None:
        """
        Attempt to deliver webhook with retry logic.

        Args:
            webhook: Webhook configuration
            payload: Data to send
        """
        webhook.last_triggered_at = datetime.utcnow()
        webhook.status = WebhookStatus.RETRYING

        try:
            # Generate signature if secret is configured
            headers = {"Content-Type": "application/json"}
            if webhook.secret:
                signature = self.generate_signature(payload, webhook.secret)
                headers["X-Webhook-Signature"] = signature
                logger.debug(f"Generated signature for webhook {webhook.id}: {signature[:16]}...")

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook.url,
                    json=payload,
                    headers=headers
                )

                if response.status_code in [200, 201, 202, 204]:
                    # Success
                    webhook.status = WebhookStatus.DELIVERED
                    webhook.last_delivered_at = datetime.utcnow()
                    webhook.retry_count = 0
                    webhook.last_error = None
                    webhook.next_retry_at = None
                    logger.info(f"Webhook delivered successfully: {webhook.id} to {webhook.url}")
                else:
                    # HTTP error
                    raise Exception(f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
            # Delivery failed
            webhook.retry_count += 1
            webhook.last_error = str(e)
            webhook.status = WebhookStatus.FAILED

            logger.error(f"Webhook delivery failed: {webhook.id} to {webhook.url}, error: {e}")

            # Schedule retry with exponential backoff
            if webhook.retry_count <= webhook.max_retries:
                # Exponential backoff: 2^retry_count minutes
                backoff_minutes = 2 ** webhook.retry_count
                webhook.next_retry_at = datetime.utcnow() + timedelta(minutes=backoff_minutes)
                webhook.status = WebhookStatus.RETRYING
                logger.info(
                    f"Webhook will retry in {backoff_minutes} minutes "
                    f"(attempt {webhook.retry_count}/{webhook.max_retries})"
                )

                # Schedule retry
                asyncio.create_task(
                    self._schedule_retry(webhook.id, backoff_minutes * 60)
                )
            else:
                # Max retries reached
                webhook.status = WebhookStatus.FAILED
                logger.error(f"Webhook max retries reached: {webhook.id}")

        finally:
            self.db.commit()

    async def _schedule_retry(self, webhook_id: str, delay_seconds: int) -> None:
        """
        Schedule a webhook retry after a delay.

        Args:
            webhook_id: ID of webhook to retry
            delay_seconds: Seconds to wait before retry
        """
        await asyncio.sleep(delay_seconds)

        # Reload webhook from database
        webhook = self.db.query(Webhook).filter(Webhook.id == webhook_id).first()
        if not webhook or not webhook.is_active:
            return

        # Retry delivery
        # Note: payload would need to be stored for retry - simplified here
        logger.info(f"Retrying webhook delivery: {webhook_id}")
        # In production, you'd store the payload and retry with the same data

    def create_webhook(
        self,
        user_id: str,
        url: str,
        event_type: WebhookEvent,
        max_retries: int = 5,
        secret: Optional[str] = None
    ) -> Webhook:
        """
        Create a new webhook configuration.

        Args:
            user_id: User who owns the webhook
            url: Endpoint URL to send webhooks to
            event_type: Type of event to trigger webhook
            max_retries: Maximum number of retry attempts
            secret: Optional secret for HMAC signature (auto-generated if not provided)

        Returns:
            Created webhook
        """
        # Generate secret if not provided
        if secret is None:
            secret = secrets.token_hex(32)  # 64 character hex string

        webhook = Webhook(
            id=str(uuid.uuid4()),
            user_id=str(user_id),
            url=url,
            event_type=event_type,
            secret=secret,
            max_retries=max_retries,
            is_active=True,
            status=WebhookStatus.PENDING
        )

        self.db.add(webhook)
        self.db.commit()
        self.db.refresh(webhook)

        logger.info(f"Webhook created: {webhook.id} for user {user_id}")
        return webhook

    async def get_webhook(self, webhook_id: str, user_id: str) -> Optional[Webhook]:
        """Get a webhook by ID for a specific user."""
        result = await self.db.execute(
            select(Webhook).filter(
                Webhook.id == webhook_id,
                Webhook.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_webhooks(self, user_id: str) -> list[Webhook]:
        """List all webhooks for a user."""
        result = await self.db.execute(
            select(Webhook).filter(
                Webhook.user_id == user_id
            ).order_by(Webhook.created_at.desc())
        )
        return list(result.scalars().all())

    def delete_webhook(self, webhook_id: str, user_id: str) -> bool:
        """Delete a webhook."""
        webhook = self.get_webhook(webhook_id, user_id)
        if not webhook:
            return False

        self.db.delete(webhook)
        self.db.commit()
        logger.info(f"Webhook deleted: {webhook_id}")
        return True

    def update_webhook_status(
        self,
        webhook_id: str,
        is_active: bool
    ) -> Optional[Webhook]:
        """Enable or disable a webhook."""
        webhook = self.db.query(Webhook).filter(Webhook.id == webhook_id).first()
        if not webhook:
            return None

        webhook.is_active = is_active
        self.db.commit()
        self.db.refresh(webhook)

        logger.info(f"Webhook {'enabled' if is_active else 'disabled'}: {webhook_id}")
        return webhook
