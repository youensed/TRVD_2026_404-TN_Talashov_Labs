from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from uuid import uuid4

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError

from app.core.config import get_settings
from app.modules.common.enums import UserRole


password_hasher = PasswordHasher()


class TokenPayload(BaseModel):
    sub: str
    role: UserRole
    type: str
    jti: str
    sid: str | None = None
    exp: int


@dataclass(slots=True)
class AuthTokens:
    access_token: str
    refresh_token: str
    csrf_token: str
    session_id: str
    refresh_jti: str


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        return password_hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def _encode_token(payload: dict[str, str | int]) -> str:
    settings = get_settings()
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def create_access_token(user_id: str, role: UserRole) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_ttl_minutes)
    return _encode_token(
        {
            "sub": user_id,
            "role": role,
            "type": "access",
            "jti": str(uuid4()),
            "exp": int(expires_at.timestamp()),
        }
    )


def create_refresh_token(user_id: str, role: UserRole, session_id: str) -> tuple[str, str]:
    settings = get_settings()
    refresh_jti = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_ttl_days)
    token = _encode_token(
        {
            "sub": user_id,
            "role": role,
            "type": "refresh",
            "sid": session_id,
            "jti": refresh_jti,
            "exp": int(expires_at.timestamp()),
        }
    )
    return token, refresh_jti


def create_auth_tokens(user_id: str, role: UserRole) -> AuthTokens:
    session_id = str(uuid4())
    csrf_token = token_urlsafe(32)
    refresh_token, refresh_jti = create_refresh_token(user_id, role, session_id)
    return AuthTokens(
        access_token=create_access_token(user_id, role),
        refresh_token=refresh_token,
        csrf_token=csrf_token,
        session_id=session_id,
        refresh_jti=refresh_jti,
    )


def create_rotated_tokens(user_id: str, role: UserRole, session_id: str) -> AuthTokens:
    csrf_token = token_urlsafe(32)
    refresh_token, refresh_jti = create_refresh_token(user_id, role, session_id)
    return AuthTokens(
        access_token=create_access_token(user_id, role),
        refresh_token=refresh_token,
        csrf_token=csrf_token,
        session_id=session_id,
        refresh_jti=refresh_jti,
    )


def decode_token(token: str, expected_type: str) -> TokenPayload:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        token_payload = TokenPayload.model_validate(payload)
    except (JWTError, ValidationError) as exc:
        raise ValueError("Invalid token.") from exc

    if token_payload.type != expected_type:
        raise ValueError("Invalid token type.")
    return token_payload

