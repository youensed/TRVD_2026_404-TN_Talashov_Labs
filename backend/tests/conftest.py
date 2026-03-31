from __future__ import annotations

import os

import fakeredis.aioredis
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

os.environ["APP_ENCRYPTION_KEY"] = "5kTuKj4SHDM2M_Z2mlk-wEYBLETymFcpnSUsctNk6BY="
os.environ["APP_SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./backend_test.sqlite3"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["FRONTEND_URL"] = "http://localhost:5173"
os.environ["APP_CORS_ORIGINS"] = "http://localhost:5173"
os.environ["APP_SECURE_COOKIES"] = "false"
os.environ["APP_SEED_DEMO_DATA"] = "false"

from app.core import redis as redis_module  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.main import app  # noqa: E402


test_engine = create_async_engine(os.environ["DATABASE_URL"])
TestSessionFactory = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def reset_state() -> None:
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
async def fake_redis():
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    redis_module._redis_client = client
    yield client
    await client.flushall()
    await client.aclose()
    redis_module._redis_client = None


@pytest.fixture
async def client(fake_redis):  # noqa: ANN001
    from app.db.session import get_db_session

    async def override_db_session():
        async with TestSessionFactory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as http_client:
        yield http_client
    app.dependency_overrides.clear()
