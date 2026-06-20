import time

from fastapi import HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.cache import get_redis
from app.core.config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        settings = get_settings()
        if request.url.path in {"/", "/docs", "/openapi.json"}:
            return await call_next(request)
        client_host = request.client.host if request.client else "unknown"
        window = int(time.time() // settings.rate_limit_window_seconds)
        key = f"rate:{client_host}:{window}"
        redis = await get_redis()
        if redis is not None:
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, settings.rate_limit_window_seconds)
            if count > settings.rate_limit_requests:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
        return await call_next(request)
