from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.redis import close_redis_client, get_redis_client
from app.core.request_context import set_request_id
from app.db.session import engine
from app.db import imports as _imports  # noqa: F401


settings = get_settings()
configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await close_redis_client()
    await engine.dispose()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-CSRF-Token", settings.request_id_header],
)


@app.middleware("http")
async def request_context_middleware(request, call_next):  # type: ignore[no-untyped-def]
    request_id = request.headers.get(settings.request_id_header, str(uuid4()))
    set_request_id(request_id)
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers[settings.request_id_header] = request_id
    logger.info("%s %s %s %.2fms", request.method, request.url.path, response.status_code, duration_ms)
    return response

@app.get("/health/live", tags=["health"])
async def live_probe() -> dict[str, str]:
    return {"status": "live"}


@app.get("/health/ready", tags=["health"])
async def readiness_probe() -> dict[str, str]:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    await get_redis_client().ping()
    return {"status": "ready"}


app.include_router(api_router)
