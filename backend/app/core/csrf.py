"""
CSRF Protection Middleware for FastAPI
"""

import secrets
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import MutableHeaders

# Store active CSRF tokens (in production, use Redis or database)
_csrf_tokens: dict[str, bool] = {}

# Safe methods that don't require CSRF protection
SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}


def generate_csrf_token() -> str:
    """Generate a new CSRF token."""
    token = secrets.token_urlsafe(32)
    _csrf_tokens[token] = True
    return token


def validate_csrf_token(token: Optional[str]) -> bool:
    """Validate a CSRF token."""
    if not token:
        return False
    return token in _csrf_tokens


def get_csrf_token_from_request(request: Request) -> Optional[str]:
    """Extract CSRF token from request headers or form data."""
    # Check X-CSRF-Token header first
    token = request.headers.get("X-CSRF-Token")
    if token:
        return token

    # Check cookies (alternative method)
    token = request.cookies.get("csrf_token")
    return token


class CSRFMiddleware(BaseHTTPMiddleware):
    """Middleware to add CSRF protection."""

    def __init__(self, app, exempt_paths: list[str] = None):
        super().__init__(app)
        # Paths that don't require CSRF protection
        self.exempt_paths = exempt_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/csrf-token",  # Endpoint to get CSRF token
            "/api/v1/users/onboarding",  # Onboarding endpoint (authenticated)
        ]

    async def dispatch(self, request: Request, call_next):
        """Process request and validate CSRF token for unsafe methods."""

        # Skip CSRF check for WebSocket connections
        if request.url.path.startswith("/api/v1/chat/ws") or request.url.path.startswith("/chat/ws"):
            print(f"[CSRF] Skipping CSRF check for WebSocket: {request.url.path}")
            response = await call_next(request)
            return response

        # Skip CSRF check for safe methods
        if request.method in SAFE_METHODS:
            response = await call_next(request)
            return response

        # Skip CSRF check for exempt paths
        path = request.url.path
        if any(path.startswith(exempt_path) for exempt_path in self.exempt_paths):
            response = await call_next(request)
            return response

        # Validate CSRF token for unsafe methods (POST, PUT, DELETE, PATCH)
        csrf_token = get_csrf_token_from_request(request)

        if not validate_csrf_token(csrf_token):
            print(f"[CSRF] Blocking request to {request.url.path} - invalid/missing CSRF token")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "CSRF token missing or invalid"}
            )

        # Token is valid, proceed with request
        response = await call_next(request)
        return response
