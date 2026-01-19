"""
API Response Caching System

Provides Redis-based caching for API responses with:
- Configurable TTL per endpoint
- Cache invalidation
- Cache headers (X-Cache-Hit)
- Hash-based cache keys
"""

import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
import time

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.core.config import settings


class CacheManager:
    """Manages Redis cache connections and operations"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connected = False

    async def connect(self):
        """Connect to Redis"""
        if not REDIS_AVAILABLE:
            print("⚠️  Redis not available, caching disabled")
            return

        try:
            # Fix Redis URL to use correct port
            redis_url = settings.REDIS_URL.replace(":6381", ":6379")
            self.redis_client = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis_client.ping()
            self._connected = True
            print(f"✅ Redis cache connected: {redis_url}")
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}")
            self._connected = False

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self._connected = False

    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._connected

    def generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        # Create a stable string representation of arguments
        key_data = {
            "prefix": prefix,
            "args": args,
            "kwargs": sorted(kwargs.items())  # Sort for consistency
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)

        # Hash for shorter keys
        key_hash = hashlib.md5(key_string.encode()).hexdigest()

        return f"cache:{prefix}:{key_hash}"

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._connected or not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL (seconds)"""
        if not self._connected or not self.redis_client:
            return False

        try:
            value_json = json.dumps(value, default=str)
            await self.redis_client.setex(key, ttl, value_json)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    async def delete(self, key: str):
        """Delete value from cache"""
        if not self._connected or not self.redis_client:
            return False

        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    async def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        if not self._connected or not self.redis_client:
            return False

        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Cache delete pattern error: {e}")
            return False


# Global cache manager instance
cache_manager = CacheManager()


def cached(ttl: int = 300, key_prefix: str = "default"):
    """
    Decorator to cache API endpoint responses

    Args:
        ttl: Time to live in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key (default: "default")

    Usage:
        @cached(ttl=600, key_prefix="companies")
        async def get_companies():
            # Expensive operation
            return data
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip cache if not connected
            if not cache_manager.is_connected():
                return await func(*args, **kwargs)

            # Generate cache key
            cache_key = cache_manager.generate_cache_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                **kwargs
            )

            # Try to get from cache
            start_time = time.time()
            cached_value = await cache_manager.get(cache_key)

            if cached_value is not None:
                # Cache hit
                cache_time = int((time.time() - start_time) * 1000)
                print(f"✅ Cache HIT: {cache_key[:50]}... ({cache_time}ms)")

                # Add cache metadata
                if isinstance(cached_value, dict):
                    cached_value["_cache_hit"] = True
                    cached_value["_cache_time_ms"] = cache_time

                return cached_value

            # Cache miss - execute function
            print(f"⚠️  Cache MISS: {cache_key[:50]}...")
            result = await func(*args, **kwargs)

            # Store in cache
            if result is not None:
                await cache_manager.set(cache_key, result, ttl)

            # Add cache metadata
            if isinstance(result, dict):
                result["_cache_hit"] = False

            return result

        return wrapper
    return decorator


async def invalidate_cache(pattern: str):
    """
    Invalidate cache entries matching pattern

    Usage:
        await invalidate_cache("cache:companies:*")
    """
    if cache_manager.is_connected():
        await cache_manager.delete_pattern(pattern)
        print(f"🗑️  Cache invalidated: {pattern}")
