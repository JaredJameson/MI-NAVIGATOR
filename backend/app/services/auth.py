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
    def create_access_token(user_id: str, expires_minutes: int = None) -> str:
        """Create a JWT access token.

        Args:
            user_id: User ID to encode in token
            expires_minutes: Optional custom expiration time in minutes (default: from settings)
        """
        if expires_minutes is None:
            expires_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

        expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "access",
            "jti": str(uuid.uuid4())  # unique token id for session fixation prevention
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: str, expires_days: int = None) -> Tuple[str, datetime]:
        """Create a JWT refresh token and return token with expiry.

        Args:
            user_id: User ID to encode in token
            expires_days: Optional custom expiration time in days (default: from settings)
        """
        if expires_days is None:
            expires_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

        expire = datetime.utcnow() + timedelta(days=expires_days)
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
    async def delete_other_user_sessions(db: AsyncSession, user_id: uuid.UUID, current_refresh_token: str) -> int:
        """
        Delete all sessions for a user except the one with the given refresh token.
        Used when changing password to invalidate other devices while keeping current session active.

        Args:
            db: Database session
            user_id: User ID whose sessions to delete
            current_refresh_token: Refresh token of the current session to keep

        Returns:
            Number of sessions deleted
        """
        result = await db.execute(select(Session).where(Session.user_id == user_id))
        sessions = result.scalars().all()
        deleted_count = 0
        for session in sessions:
            if session.refresh_token != current_refresh_token:
                await db.delete(session)
                deleted_count += 1
        return deleted_count

    @staticmethod
    async def is_account_locked(user: User) -> bool:
        """Check if user account is locked."""
        if user.account_locked_until is None:
            return False

        # Check if lockout period has expired
        if datetime.utcnow() >= user.account_locked_until:
            # Lockout period expired, account is no longer locked
            return False

        return True

    @staticmethod
    async def reset_failed_attempts(db: AsyncSession, user: User) -> None:
        """Reset failed login attempts counter."""
        user.failed_login_attempts = 0
        user.account_locked_until = None
        await db.flush()

    @staticmethod
    async def increment_failed_attempts(db: AsyncSession, user: User) -> None:
        """Increment failed login attempts and lock account if threshold exceeded."""
        MAX_ATTEMPTS = 5
        LOCKOUT_DURATION_MINUTES = 15

        user.failed_login_attempts += 1

        # Lock account if threshold exceeded
        if user.failed_login_attempts >= MAX_ATTEMPTS:
            user.account_locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)

        await db.flush()

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user by email and password.
        Increments failed attempts on wrong password, resets on success.
        Returns None if authentication fails.
        """
        user = await AuthService.get_user_by_email(db, email)

        if not user:
            return None

        if not user.is_active:
            return None

        # Verify password
        if not AuthService.verify_password(password, user.password_hash):
            # Increment failed attempts
            await AuthService.increment_failed_attempts(db, user)
            return None

        # Successful login - reset failed attempts counter
        await AuthService.reset_failed_attempts(db, user)

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
