import json
from typing import Any, Optional

import redis.asyncio as redis

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)
_client: Optional[redis.Redis] = None


async def get_redis() -> Optional[redis.Redis]:
    global _client
    settings = get_settings()
    if not settings.enable_redis_cache:
        return None
    if _client is None:
        try:
            _client = redis.from_url(settings.redis_url, decode_responses=True)
            await _client.ping()
        except Exception:
            logger.warning("Redis unavailable; continuing without cache")
            _client = None
    return _client


async def cache_get(key: str) -> Any:
    client = await get_redis()
    if client is None:
        return None
    value = await client.get(key)
    return json.loads(value) if value else None


async def cache_set(key: str, value: Any, ttl_seconds: int = 60) -> None:
    client = await get_redis()
    if client is not None:
        await client.setex(key, ttl_seconds, json.dumps(value, default=str))
