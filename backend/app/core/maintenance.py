"""
Maintenance Mode Middleware
Blocks access to the application when maintenance mode is enabled.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings


class MaintenanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check if the application is in maintenance mode.

    If MAINTENANCE_MODE is enabled:
    - Returns 503 Service Unavailable for all requests
    - Exception: Admin users can still access (checked via Authorization header)
    - Exception: Health check endpoint always accessible
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Always allow health check
        if request.url.path == "/health":
            return await call_next(request)

        # Always allow maintenance status endpoint
        if request.url.path == "/api/v1/system/maintenance":
            return await call_next(request)

        # Check if maintenance mode is enabled
        if settings.MAINTENANCE_MODE:
            # Check if user is admin (has valid token with admin role)
            authorization = request.headers.get("Authorization")

            is_admin = False
            if authorization and authorization.startswith("Bearer "):
                # Try to decode JWT token and check for admin role
                try:
                    from app.services.auth import AuthService
                    token = authorization.replace("Bearer ", "")
                    token_data = AuthService.decode_token(token)

                    if token_data and token_data.type == "access":
                        # Check if token contains admin role
                        # For simplicity, we'll check if role is in token payload
                        # In production, you might want to query database
                        if hasattr(token_data, 'role') and token_data.role == 'admin':
                            is_admin = True
                except Exception:
                    # Token decode failed, not admin
                    pass

            if not is_admin:
                # Return maintenance response
                return JSONResponse(
                    status_code=503,
                    content={
                        "maintenance": True,
                        "message": settings.MAINTENANCE_MESSAGE,
                        "eta": settings.MAINTENANCE_ETA if settings.MAINTENANCE_ETA else None
                    },
                    headers={
                        "Retry-After": "3600"  # Suggest retry after 1 hour
                    }
                )

        return await call_next(request)
