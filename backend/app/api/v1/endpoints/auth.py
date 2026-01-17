"""
Authentication API Endpoints
"""

from datetime import datetime
from typing import Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse, Token, PasswordResetRequest, PasswordResetConfirm,
    TwoFactorSetupResponse, TwoFactorVerifyRequest, TwoFactorStatusResponse
)
from app.services.auth import AuthService
from app.services.two_factor import TwoFactorService

router = APIRouter()

# Security logger for failed login attempts
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# Add console handler if not already present
if not security_logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    console_handler.setFormatter(formatter)
    security_logger.addHandler(console_handler)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> "User":
    """Get current authenticated user from token."""
    from app.models.user import User

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = AuthService.decode_token(token)
    if not token_data or token_data.type != "access":
        raise credentials_exception

    if token_data.exp < datetime.utcnow():
        raise credentials_exception

    user = await AuthService.get_user_by_id(db, token_data.sub)
    if not user or not user.is_active:
        raise credentials_exception

    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.

    Password requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one digit
    """
    # Check if email already exists
    existing_user = await AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = await AuthService.create_user(db, user_data)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.

    Uses OAuth2 password flow:
    - username: user's email
    - password: user's password
    """
    # Get client IP address
    ip_address = request.client.host if request else "unknown"
    user_agent = request.headers.get("user-agent", "unknown") if request else "unknown"

    # First check if user exists and if account is locked
    existing_user = await AuthService.get_user_by_email(db, form_data.username)

    if existing_user and await AuthService.is_account_locked(existing_user):
        # Account is locked
        lockout_time = existing_user.account_locked_until
        security_logger.warning(
            f"Locked account login attempt | Email: {form_data.username} | "
            f"IP: {ip_address} | Locked until: {lockout_time.isoformat() if lockout_time else 'N/A'}"
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account temporarily locked due to multiple failed login attempts. Please try again later.",
        )

    # Try to authenticate
    user = await AuthService.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        # Commit failed attempt counter update before raising exception
        await db.commit()

        # Log failed login attempt
        security_logger.warning(
            f"Failed login attempt | Email: {form_data.username} | "
            f"IP: {ip_address} | User-Agent: {user_agent} | "
            f"Timestamp: {datetime.utcnow().isoformat()}"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Log successful login
    security_logger.info(
        f"Successful login | Email: {form_data.username} | "
        f"IP: {ip_address} | Timestamp: {datetime.utcnow().isoformat()}"
    )

    # Create tokens
    access_token = AuthService.create_access_token(str(user.id))
    refresh_token, refresh_expires = AuthService.create_refresh_token(str(user.id))

    # Store session
    await AuthService.create_session(
        db,
        user.id,
        refresh_token,
        refresh_expires,
        ip_address,
        user_agent
    )

    # Update last login
    await AuthService.update_last_login(db, user)
    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/logout")
async def logout(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout user and invalidate all sessions."""
    await AuthService.delete_all_user_sessions(db, current_user.id)
    await db.commit()

    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    # Decode and validate refresh token
    token_data = AuthService.decode_token(refresh_token)

    if not token_data or token_data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    if token_data.exp < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )

    # Get session
    session = await AuthService.get_session_by_refresh_token(db, refresh_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )

    # Get user
    user = await AuthService.get_user_by_id(db, token_data.sub)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    new_access_token = AuthService.create_access_token(str(user.id))
    new_refresh_token, refresh_expires = AuthService.create_refresh_token(str(user.id))

    # Delete old session and create new one
    await AuthService.delete_session(db, session)

    ip_address = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None

    await AuthService.create_session(
        db,
        user.id,
        new_refresh_token,
        refresh_expires,
        ip_address,
        user_agent
    )

    await db.commit()

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Get current user's profile information."""
    return current_user


@router.post("/forgot-password")
async def forgot_password(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate password reset flow.

    In development mode, the reset token is logged to console.
    Always returns success to prevent email enumeration.
    """
    user = await AuthService.get_user_by_email(db, data.email)

    # Always return success to prevent email enumeration
    if user:
        # Generate reset token
        reset_token = await AuthService.create_password_reset_token(db, user)
        await db.commit()

        # In development: log to console instead of sending email
        print(f"\n{'='*60}")
        print(f"PASSWORD RESET REQUEST for {data.email}")
        print(f"Reset link: http://localhost:3000/auth/reset-password?token={reset_token.token}")
        print(f"Token: {reset_token.token}")
        print(f"{'='*60}\n")

    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """Reset password with token."""
    # Validate token
    reset_token = await AuthService.get_valid_reset_token(db, data.token)

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Reset password
    try:
        await AuthService.reset_password(db, reset_token, data.password)
        await db.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return {"message": "Password reset successfully"}


@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_two_factor(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initialize 2FA setup for the current user.

    Returns a QR code and secret for the user to scan with an authenticator app.
    2FA is not enabled until the user verifies with a valid code.
    """
    secret, qr_code, manual_key = await TwoFactorService.setup_two_factor(db, current_user)
    await db.commit()

    return TwoFactorSetupResponse(
        secret=secret,
        qr_code=qr_code,
        manual_entry_key=manual_key
    )


@router.post("/2fa/verify", response_model=TwoFactorStatusResponse)
async def verify_and_enable_two_factor(
    data: TwoFactorVerifyRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify the 2FA setup code and enable 2FA for the user.

    The user must provide a valid 6-digit code from their authenticator app.
    """
    success = await TwoFactorService.enable_two_factor(db, current_user, data.code)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code. Please try again."
        )

    await db.commit()

    return TwoFactorStatusResponse(
        enabled=True,
        message="Two-factor authentication has been enabled successfully"
    )


@router.post("/2fa/disable", response_model=TwoFactorStatusResponse)
async def disable_two_factor(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disable 2FA for the current user.

    This will remove the TOTP secret and disable two-factor authentication.
    """
    await TwoFactorService.disable_two_factor(db, current_user)
    await db.commit()

    return TwoFactorStatusResponse(
        enabled=False,
        message="Two-factor authentication has been disabled"
    )


@router.get("/2fa/status", response_model=TwoFactorStatusResponse)
async def get_two_factor_status(
    current_user = Depends(get_current_user)
):
    """Get the current 2FA status for the user."""
    return TwoFactorStatusResponse(
        enabled=current_user.two_factor_enabled,
        message=f"Two-factor authentication is {'enabled' if current_user.two_factor_enabled else 'disabled'}"
    )


@router.get("/csrf-token")
async def get_csrf_token():
    """
    Get a CSRF token for form submissions.

    This token must be included in the X-CSRF-Token header
    for all unsafe HTTP methods (POST, PUT, DELETE, PATCH).
    """
    from app.core.csrf import generate_csrf_token

    token = generate_csrf_token()

    return {
        "csrf_token": token,
        "message": "Include this token in X-CSRF-Token header for POST/PUT/DELETE requests"
    }
