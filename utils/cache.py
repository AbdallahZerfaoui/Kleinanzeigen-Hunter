"""Lightweight Redis cache helper for scraper responses."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, Optional

from redis.asyncio import Redis
from redis.exceptions import RedisError

from config import CACHE_ENABLED, CACHE_TTL_SECONDS, REDIS_URL

logger = logging.getLogger(__name__)

_cache_state: Dict[str, Any] = {"client": None, "disabled": False}


def cache_available() -> bool:
    """Return True if caching is enabled via configuration."""

    return CACHE_ENABLED and bool(REDIS_URL) and not _cache_state["disabled"]


async def get_redis_client() -> Redis:
    """Lazily instantiate and return a Redis asyncio client."""

    client: Optional[Redis] = _cache_state["client"]
    if client is None:
        client = Redis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        _cache_state["client"] = client
    return client


def build_cache_key(namespace: str, **params: Any) -> str:
    """Build a deterministic cache key from provided parameters."""

    serialized = json.dumps(sorted(params.items()), default=str, separators=(",", ":"))
    digest = hashlib.sha1(serialized.encode("utf-8")).hexdigest()
    return f"{namespace}:{digest}"


async def get_cached_value(key: str) -> Optional[Any]:
    """Retrieve a cached JSON payload if caching is enabled."""

    if not cache_available():
        return None

    client = await get_redis_client()
    try:
        payload = await client.get(key)
    except (RedisError, OSError) as exc:  # pragma: no cover - network errors
        _disable_cache(exc)
        return None
    if payload is None:
        return None
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return payload


async def set_cached_value(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Store a JSON-serializable payload in Redis with a TTL."""

    if not cache_available():
        return False

    client = await get_redis_client()
    payload = json.dumps(value, default=str)
    try:
        await client.set(key, payload, ex=ttl or CACHE_TTL_SECONDS)
    except (RedisError, OSError) as exc:  # pragma: no cover - network errors
        _disable_cache(exc)
        return False
    return True


async def invalidate_cache(key: str) -> bool:
    """Remove a cached entry."""

    if not cache_available():
        return False

    client = await get_redis_client()
    try:
        removed = await client.delete(key)
    except (RedisError, OSError) as exc:  # pragma: no cover - network errors
        _disable_cache(exc)
        return False
    return bool(removed)


async def close_cache() -> None:
    """Close the Redis connection (useful for graceful shutdowns)."""

    client: Optional[Redis] = _cache_state["client"]
    if client is not None:
        await client.close()
        _cache_state["client"] = None


def _disable_cache(exc: Exception) -> None:
    """Disable caching after a Redis failure to avoid repeated errors."""

    if not _cache_state["disabled"]:
        logger.warning("Disabling Redis cache due to error: %s", exc)
        _cache_state["disabled"] = True
