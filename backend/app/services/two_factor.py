"""
Two-Factor Authentication Service
"""

import pyotp
import qrcode
import io
import base64
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User


class TwoFactorService:
    """Service for two-factor authentication operations."""

    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret."""
        return pyotp.random_base32()

    @staticmethod
    def generate_qr_code(secret: str, user_email: str, issuer: str = "MI-Navigator") -> str:
        """
        Generate QR code for TOTP secret.

        Returns: Base64-encoded PNG image as data URL
        """
        # Create provisioning URI
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name=issuer
        )

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        # Convert to image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64 data URL
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def verify_totp_code(secret: str, code: str) -> bool:
        """
        Verify a TOTP code against a secret.

        Args:
            secret: Base32 encoded TOTP secret
            code: 6-digit TOTP code from user

        Returns: True if code is valid, False otherwise
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)  # Allow 1 time step tolerance

    @staticmethod
    async def setup_two_factor(db: AsyncSession, user: User) -> Tuple[str, str, str]:
        """
        Initialize 2FA setup for a user.

        Returns: (secret, qr_code_data_url, manual_entry_key)
        """
        # Generate new secret
        secret = TwoFactorService.generate_secret()

        # Store secret (but don't enable yet - user must verify first)
        user.totp_secret = secret
        await db.flush()

        # Generate QR code
        qr_code = TwoFactorService.generate_qr_code(secret, user.email)

        return (secret, qr_code, secret)

    @staticmethod
    async def enable_two_factor(db: AsyncSession, user: User, code: str) -> bool:
        """
        Enable 2FA after verifying the setup code.

        Returns: True if enabled successfully, False if code invalid
        """
        if not user.totp_secret:
            return False

        # Verify the code
        if not TwoFactorService.verify_totp_code(user.totp_secret, code):
            return False

        # Enable 2FA
        user.two_factor_enabled = True
        await db.flush()

        return True

    @staticmethod
    async def disable_two_factor(db: AsyncSession, user: User) -> None:
        """Disable 2FA for a user."""
        user.two_factor_enabled = False
        user.totp_secret = None
        await db.flush()

    @staticmethod
    async def verify_login_code(user: User, code: str) -> bool:
        """
        Verify 2FA code during login.

        Returns: True if code is valid, False otherwise
        """
        if not user.two_factor_enabled or not user.totp_secret:
            return False

        return TwoFactorService.verify_totp_code(user.totp_secret, code)
