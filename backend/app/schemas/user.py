"""
User Schemas for Request/Response Validation
"""

import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str
    confirm_password: str
    name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_validation(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str
    remember_me: bool = False


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    industry: Optional[str] = None
    industry_segment: Optional[str] = None
    user_role: Optional[str] = None
    preferred_language: str
    preferred_depth: str
    preferred_format: str
    timezone: str = "Europe/Warsaw"
    report_branding: bool = True
    onboarding_completed: bool
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for user profile update."""
    name: Optional[str] = None
    industry: Optional[str] = None
    industry_segment: Optional[str] = None
    user_role: Optional[str] = None
    preferred_language: Optional[str] = None
    preferred_depth: Optional[str] = None
    preferred_format: Optional[str] = None
    timezone: Optional[str] = None
    report_branding: Optional[bool] = None


class Token(BaseModel):
    """JWT Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TwoFactorRequired(BaseModel):
    """Response when 2FA is required during login."""
    requires_2fa: bool = True
    temp_token: str
    message: str


class TokenPayload(BaseModel):
    """JWT Token payload."""
    sub: str  # user_id
    exp: datetime
    type: str  # "access" or "refresh"


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    password: str
    confirm_password: str

    @field_validator("password")
    @classmethod
    def password_validation(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v


class TwoFactorSetupResponse(BaseModel):
    """Schema for 2FA setup response."""
    secret: str
    qr_code: str  # Data URL for QR code image
    manual_entry_key: str  # Base32 secret for manual entry


class TwoFactorVerifyRequest(BaseModel):
    """Schema for 2FA code verification."""
    code: str  # 6-digit TOTP code

    @field_validator("code")
    @classmethod
    def code_validation(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("Code must be exactly 6 digits")
        return v


class TwoFactorStatusResponse(BaseModel):
    """Schema for 2FA status response."""
    enabled: bool
    message: str
