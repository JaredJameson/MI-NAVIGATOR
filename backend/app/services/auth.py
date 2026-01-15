"""
Authentication Service
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

import bcrypt
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User, Session, PasswordResetToken
from app.schemas.user import UserCreate, Token, TokenPayload


class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    @staticmethod
    def create_access_token(user_id: str) -> str:
        """Create a JWT access token."""
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "access"
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: str) -> Tuple[str, datetime]:
        """Create a JWT refresh token and return token with expiry."""
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh",
            "jti": str(uuid.uuid4())  # unique token id
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return token, expire

    @staticmethod
    def decode_token(token: str) -> Optional[TokenPayload]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return TokenPayload(
                sub=payload["sub"],
                exp=datetime.fromtimestamp(payload["exp"]),
                type=payload["type"]
            )
        except JWTError:
            return None

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user."""
        hashed_password = AuthService.hash_password(user_data.password)

        user = User(
            email=user_data.email,
            password_hash=hashed_password,
            name=user_data.name,
        )

        db.add(user)
        await db.flush()
        await db.refresh(user)

        return user

    @staticmethod
    async def create_session(
        db: AsyncSession,
        user_id: uuid.UUID,
        refresh_token: str,
        expires_at: datetime,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Session:
        """Create a new session with refresh token."""
        session = Session(
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )

        db.add(session)
        await db.flush()

        return session

    @staticmethod
    async def get_session_by_refresh_token(db: AsyncSession, refresh_token: str) -> Optional[Session]:
        """Get session by refresh token."""
        result = await db.execute(
            select(Session).where(Session.refresh_token == refresh_token)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_session(db: AsyncSession, session: Session) -> None:
        """Delete a session."""
        await db.delete(session)

    @staticmethod
    async def delete_all_user_sessions(db: AsyncSession, user_id: uuid.UUID) -> None:
        """Delete all sessions for a user."""
        result = await db.execute(select(Session).where(Session.user_id == user_id))
        sessions = result.scalars().all()
        for session in sessions:
            await db.delete(session)

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = await AuthService.get_user_by_email(db, email)

        if not user:
            return None

        if not AuthService.verify_password(password, user.password_hash):
            return None

        if not user.is_active:
            return None

        return user

    @staticmethod
    async def update_last_login(db: AsyncSession, user: User) -> None:
        """Update user's last login timestamp."""
        user.last_login_at = datetime.utcnow()
        await db.flush()

    @staticmethod
    def generate_reset_token() -> str:
        """Generate a random password reset token."""
        import secrets
        return secrets.token_urlsafe(32)

    @staticmethod
    async def create_password_reset_token(
        db: AsyncSession,
        user: User,
        expires_hours: int = 24
    ) -> PasswordResetToken:
        """Create a password reset token for a user."""
        # Invalidate any existing tokens for this user
        existing = await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used == False
            )
        )
        for token in existing.scalars().all():
            token.used = True

        # Create new token
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=AuthService.generate_reset_token(),
            expires_at=datetime.utcnow() + timedelta(hours=expires_hours)
        )
        db.add(reset_token)
        await db.flush()
        await db.refresh(reset_token)
        return reset_token

    @staticmethod
    async def get_valid_reset_token(
        db: AsyncSession,
        token: str
    ) -> Optional[PasswordResetToken]:
        """Get a valid (not expired, not used) password reset token."""
        result = await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token == token,
                PasswordResetToken.used == False,
                PasswordResetToken.expires_at > datetime.utcnow()
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def reset_password(
        db: AsyncSession,
        reset_token: PasswordResetToken,
        new_password: str
    ) -> User:
        """Reset user's password using a valid reset token."""
        # Get user
        user = await AuthService.get_user_by_id(db, str(reset_token.user_id))
        if not user:
            raise ValueError("User not found")

        # Update password
        user.password_hash = AuthService.hash_password(new_password)

        # Mark token as used
        reset_token.used = True

        # Invalidate all sessions (security measure)
        await AuthService.delete_all_user_sessions(db, user.id)

        await db.flush()
        return user
