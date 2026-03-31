from __future__ import annotations

import asyncio
import os

import fakeredis.aioredis
import uvicorn


def configure_environment() -> None:
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./smoke.sqlite3"
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"
    os.environ["FRONTEND_URL"] = "http://127.0.0.1:5173"
    os.environ["APP_CORS_ORIGINS"] = "http://127.0.0.1:5173,http://localhost:5173"
    os.environ["APP_ENVIRONMENT"] = "development"
    os.environ["APP_SECURE_COOKIES"] = "false"
    os.environ["APP_SEED_DEMO_DATA"] = "true"
    os.environ.setdefault("APP_SECRET_KEY", "0ef53ef3f8df4d06a7f81d816657ab5a946f1d8bda946d24a3f5983d4d3459e9")
    os.environ.setdefault("APP_ENCRYPTION_KEY", "5kTuKj4SHDM2M_Z2mlk-wEYBLETymFcpnSUsctNk6BY=")


async def bootstrap() -> None:
    from app.core import redis as redis_module
    from app.db.base import Base
    from app.db.session import engine
    from app.db import imports as _imports  # noqa: F401
    from app.seed import seed

    redis_module._redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await seed()


def main() -> None:
    configure_environment()
    asyncio.run(bootstrap())
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
