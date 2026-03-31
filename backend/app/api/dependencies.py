from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.csrf import enforce_csrf
from app.core.security import decode_token
from app.db.session import get_db_session
from app.modules.auth.service import AuthService
from app.modules.common.enums import UserRole
from app.modules.users.model import User
from app.modules.users.repository import UserRepository


@dataclass(slots=True)
class ClientContext:
    ip_address: str | None
    user_agent: str | None


def get_client_context(request: Request) -> ClientContext:
    return ClientContext(
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )


def csrf_protected(request: Request) -> None:
    enforce_csrf(request)


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> User:
    settings = get_settings()
    token = request.cookies.get(settings.access_cookie_name)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    try:
        token_payload = decode_token(token, expected_type="access")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token.") from exc

    user = await UserRepository(session).get_by_id(token_payload.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    await AuthService(session).enforce_admin_idle_timeout(user_id=str(user.id), role=user.role)
    return user


def require_roles(*roles: UserRole) -> Callable[[User], Awaitable[User]]:
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if roles and user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions.")
        return user

    return dependency

