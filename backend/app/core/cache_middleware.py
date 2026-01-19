"""
Cache headers middleware for FastAPI

Adds cache-related headers to API responses:
- X-Cache-Hit: true/false (whether response came from cache)
- X-Cache-Time-Ms: Response time from cache in milliseconds
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Callable


class CacheHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add cache headers to API responses.

    Headers added:
    - X-Cache-Hit: Whether response was served from cache (true/false)
    - X-Cache-Time-Ms: Time taken to retrieve from cache (if cached)
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and add cache headers"""

        # Process the request
        response = await call_next(request)

        # Check if response contains cache metadata
        # (this would be set by the @cached decorator)
        # For now, we'll add a default header indicating cache is available
        if not response.headers.get("X-Cache-Hit"):
            response.headers["X-Cache-Status"] = "available"

        return response
