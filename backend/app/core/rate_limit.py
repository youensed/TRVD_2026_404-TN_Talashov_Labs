from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import HTTPException, Request, status

from app.core.redis import get_redis_client


def rate_limit(limit: int, window_seconds: int, namespace: str) -> Callable[[Request], Awaitable[None]]:
    async def dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        redis = get_redis_client()
        key = f"rate-limit:{namespace}:{client_ip}"
        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, window_seconds)
        if current > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
            )

    return dependency

