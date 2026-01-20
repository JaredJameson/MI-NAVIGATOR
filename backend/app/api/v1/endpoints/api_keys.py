"""
API Keys Endpoints
Handles API key generation and management for programmatic access
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.models.api_key import APIKey
from app.db.session import get_db

router = APIRouter()


class APIKeyCreate(BaseModel):
    """Request model for creating an API key"""
    name: Optional[str] = Field(None, max_length=100, description="Optional name for the key")
    description: Optional[str] = Field(None, description="Optional description")
    expires_days: Optional[int] = Field(None, description="Optional expiration in days")


class APIKeyResponse(BaseModel):
    """Response model for API key (without exposing the actual key)"""
    id: str
    key_prefix: str
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, api_key: APIKey):
        """Convert APIKey to APIKeyResponse"""
        return cls(
            id=str(api_key.id),
            key_prefix=api_key.key_prefix,
            name=api_key.name,
            description=api_key.description,
            is_active=api_key.is_active,
            created_at=api_key.created_at,
            last_used_at=api_key.last_used_at,
            expires_at=api_key.expires_at
        )


class APIKeyCreateResponse(BaseModel):
    """Response model for newly created API key (includes the actual key ONCE)"""
    id: str
    key: str  # Full key - shown only once!
    key_prefix: str
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all API keys for the current user"""
    result = await db.execute(
        select(APIKey).where(
            APIKey.user_id == str(current_user.id)
        ).order_by(APIKey.created_at.desc())
    )
    api_keys = result.scalars().all()

    return [APIKeyResponse.from_orm(key) for key in api_keys]


@router.post("/", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a new API key for programmatic access.

    IMPORTANT: The full key is returned only once. Store it securely!
    """
    from datetime import timedelta

    # Generate the key
    key = APIKey.generate_key()
    key_hash = APIKey.hash_key(key)
    key_prefix = key[:12]  # First 12 chars as prefix (e.g., "mi_nav_ab12")

    # Calculate expiration if specified
    expires_at = None
    if data.expires_days:
        expires_at = datetime.utcnow() + timedelta(days=data.expires_days)

    # Create the API key record
    api_key = APIKey(
        user_id=str(current_user.id),
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=data.name,
        description=data.description,
        expires_at=expires_at
    )

    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    # Return the full key ONLY this once
    return APIKeyCreateResponse(
        id=str(api_key.id),
        key=key,  # Full key shown only once!
        key_prefix=key_prefix,
        name=api_key.name,
        description=api_key.description,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an API key"""
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == str(current_user.id)
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    await db.delete(api_key)
    await db.commit()

    return None


@router.patch("/{key_id}/deactivate", response_model=APIKeyResponse)
async def deactivate_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate an API key (soft delete)"""
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == key_id,
            APIKey.user_id == str(current_user.id)
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    api_key.is_active = False
    await db.commit()
    await db.refresh(api_key)

    return APIKeyResponse.from_orm(api_key)
