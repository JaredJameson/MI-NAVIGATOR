"""
Test endpoints for verifying functionality
"""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from typing import Dict
import time

router = APIRouter()

# In-memory rate limit storage for testing
test_rate_limits: Dict[str, Dict] = {}

# Test rate limit configuration
TEST_RATE_LIMIT = 5  # Max 5 requests
TEST_WINDOW_SECONDS = 60  # Per 60 seconds (1 minute)


@router.get("/rate-limit")
async def test_rate_limit(request: Request):
    """
    Test endpoint for verifying rate limiting functionality.

    Rate limit: 5 requests per 60 seconds

    Returns:
    - 200 OK for requests within limit
    - 429 Too Many Requests when limit exceeded
    """

    # Get client identifier
    client_id = request.client.host if request.client else "unknown"

    # Get or initialize client data
    now = time.time()
    if client_id not in test_rate_limits:
        reset_time = now + TEST_WINDOW_SECONDS
        test_rate_limits[client_id] = {
            "count": 0,
            "reset": reset_time
        }

    client_data = test_rate_limits[client_id]

    # Check if window has expired
    if now >= client_data["reset"]:
        client_data["count"] = 0
        client_data["reset"] = now + TEST_WINDOW_SECONDS

    # Check if rate limit exceeded BEFORE incrementing
    if client_data["count"] >= TEST_RATE_LIMIT:
        # Return 429 Too Many Requests
        retry_after = int(client_data["reset"] - now)

        response = JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Please try again in {retry_after} seconds.",
                "retry_after": retry_after,
                "limit": TEST_RATE_LIMIT,
                "window": TEST_WINDOW_SECONDS
            }
        )

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(TEST_RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = "0"
        response.headers["X-RateLimit-Reset"] = str(int(client_data["reset"]))
        response.headers["Retry-After"] = str(retry_after)

        return response

    # Increment request count
    client_data["count"] += 1

    # Calculate remaining requests
    remaining = max(0, TEST_RATE_LIMIT - client_data["count"])

    # Create successful response
    response = JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Request successful",
            "request_count": client_data["count"],
            "remaining": remaining,
            "limit": TEST_RATE_LIMIT,
            "window": TEST_WINDOW_SECONDS,
            "reset_in": int(client_data["reset"] - now)
        }
    )

    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(TEST_RATE_LIMIT)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(client_data["reset"]))

    return response


@router.post("/rate-limit/reset")
async def reset_test_rate_limit(request: Request):
    """
    Reset rate limit for testing client.
    Useful for cleaning up between tests.
    """
    client_id = request.client.host if request.client else "unknown"

    if client_id in test_rate_limits:
        del test_rate_limits[client_id]

    return {
        "success": True,
        "message": f"Rate limit reset for client {client_id}"
    }
