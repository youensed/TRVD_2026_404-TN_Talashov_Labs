from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import ClientContext, csrf_protected, get_client_context, get_current_user
from app.core.config import get_settings
from app.core.cookies import clear_auth_cookies, set_auth_cookies
from app.core.rate_limit import rate_limit
from app.db.session import get_db_session
from app.modules.auth.schemas import AuthSessionResponse, LoginRequest, LogoutResponse, RegisterRequest
from app.modules.auth.service import AuthService
from app.modules.users.model import User
from app.modules.users.schemas import CurrentUserResponse
from app.modules.users.service import build_current_user_response


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=AuthSessionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(limit=5, window_seconds=60, namespace="register"))],
)
async def register(
    payload: RegisterRequest,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
    client: ClientContext = Depends(get_client_context),
) -> AuthSessionResponse:
    user, tokens = await AuthService(session).register_patient(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        ip_address=client.ip_address,
        user_agent=client.user_agent,
    )
    set_auth_cookies(
        response,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        csrf_token=tokens.csrf_token,
    )
    return AuthSessionResponse(message="Реєстрацію завершено успішно.", user=build_current_user_response(user))


@router.post(
    "/login",
    response_model=AuthSessionResponse,
    dependencies=[Depends(rate_limit(limit=10, window_seconds=60, namespace="login"))],
)
async def login(
    payload: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
    client: ClientContext = Depends(get_client_context),
) -> AuthSessionResponse:
    user, tokens = await AuthService(session).login(
        email=payload.email,
        password=payload.password,
        ip_address=client.ip_address,
        user_agent=client.user_agent,
    )
    set_auth_cookies(
        response,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        csrf_token=tokens.csrf_token,
    )
    return AuthSessionResponse(message="Вхід виконано успішно.", user=build_current_user_response(user))


@router.post(
    "/refresh",
    response_model=AuthSessionResponse,
    dependencies=[Depends(rate_limit(limit=20, window_seconds=60, namespace="refresh"))],
)
async def refresh_session(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
    client: ClientContext = Depends(get_client_context),
) -> AuthSessionResponse:
    refresh_token = request.cookies.get(get_settings().refresh_cookie_name)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing.")
    user, tokens = await AuthService(session).refresh_session(
        refresh_token=refresh_token,
        ip_address=client.ip_address,
        user_agent=client.user_agent,
    )
    set_auth_cookies(
        response,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        csrf_token=tokens.csrf_token,
    )
    return AuthSessionResponse(message="Сесію оновлено.", user=build_current_user_response(user))


@router.post("/logout", response_model=LogoutResponse, dependencies=[Depends(csrf_protected)])
async def logout(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
    client: ClientContext = Depends(get_client_context),
) -> LogoutResponse:
    refresh_token = request.cookies.get(get_settings().refresh_cookie_name)
    await AuthService(session).logout(
        refresh_token=refresh_token,
        ip_address=client.ip_address,
        user_agent=client.user_agent,
    )
    clear_auth_cookies(response)
    return LogoutResponse(message="Сесію завершено.")


@router.get("/me", response_model=CurrentUserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)) -> CurrentUserResponse:
    return build_current_user_response(current_user)
