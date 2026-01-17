"""
Rate limiting middleware for FastAPI
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable, Dict
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add rate limit headers to all API responses.

    Headers added:
    - X-RateLimit-Limit: Maximum requests allowed per window
    - X-RateLimit-Remaining: Requests remaining in current window
    - X-RateLimit-Reset: Unix timestamp when the limit resets
    """

    def __init__(
        self,
        app: ASGIApp,
        limit: int = 10000,  # Max requests per month
        window_seconds: int = 2592000  # 30 days in seconds
    ):
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds

        # Simple in-memory storage (would use Redis in production)
        self.requests: Dict[str, Dict] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and add rate limit headers"""

        # Get client identifier (IP or user ID from token)
        client_id = request.client.host if request.client else "unknown"

        # Get or initialize client data
        now = time.time()
        if client_id not in self.requests:
            reset_time = now + self.window_seconds
            self.requests[client_id] = {
                "count": 0,
                "reset": reset_time
            }

        client_data = self.requests[client_id]

        # Check if window has expired
        if now >= client_data["reset"]:
            client_data["count"] = 0
            client_data["reset"] = now + self.window_seconds

        # Increment request count
        client_data["count"] += 1

        # Calculate remaining requests
        remaining = max(0, self.limit - client_data["count"])

        # Process the request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(client_data["reset"]))

        return response
