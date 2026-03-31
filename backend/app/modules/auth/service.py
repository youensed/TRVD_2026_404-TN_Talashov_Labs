from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.redis import get_redis_client
from app.core.security import AuthTokens, create_auth_tokens, create_rotated_tokens, decode_token, hash_password, verify_password
from app.modules.audit.service import AuditService
from app.modules.common.enums import AuditEventType, UserRole
from app.modules.users.model import User
from app.modules.users.repository import UserRepository


@dataclass(slots=True)
class AuthService:
    session: AsyncSession

    async def register_patient(
        self,
        *,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone: str | None,
        ip_address: str | None,
        user_agent: str | None,
    ) -> tuple[User, AuthTokens]:
        repository = UserRepository(self.session)
        if await repository.get_by_email(email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists.")

        user = User(
            email=email,
            password_hash=hash_password(password),
            role=UserRole.PATIENT,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            is_verified=True,
        )
        created = await repository.create(user)
        tokens = create_auth_tokens(str(created.id), created.role)
        await self._persist_session(user=created, tokens=tokens)
        await AuditService(self.session).record_event(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id=str(created.id),
            ip_address=ip_address,
            user_agent=user_agent,
            details={"flow": "register"},
        )
        await self.session.commit()
        return created, tokens

    async def login(
        self,
        *,
        email: str,
        password: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> tuple[User, AuthTokens]:
        repository = UserRepository(self.session)
        user = await repository.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            await AuditService(self.session).record_event(
                event_type=AuditEventType.LOGIN_FAILED,
                user_id=str(user.id) if user else None,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"email": email},
            )
            await self.session.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

        tokens = create_auth_tokens(str(user.id), user.role)
        await self._persist_session(user=user, tokens=tokens)
        await AuditService(self.session).record_event(
            event_type=AuditEventType.LOGIN_SUCCESS,
            user_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent,
            details={"flow": "login"},
        )
        await self.session.commit()
        return user, tokens

    async def refresh_session(
        self,
        *,
        refresh_token: str,
        ip_address: str | None,
        user_agent: str | None,
    ) -> tuple[User, AuthTokens]:
        try:
            token_payload = decode_token(refresh_token, expected_type="refresh")
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.") from exc

        redis = get_redis_client()
        session_key = self._session_key(token_payload.sid or "")
        session_data = await redis.hgetall(session_key)
        if not session_data or session_data.get("refresh_jti") != token_payload.jti:
            await redis.delete(session_key)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired.")

        repository = UserRepository(self.session)
        user = await repository.get_by_id(token_payload.sub)
        if not user:
            await redis.delete(session_key)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is no longer available.")

        tokens = create_rotated_tokens(str(user.id), user.role, token_payload.sid or "")
        await self._persist_session(user=user, tokens=tokens)
        await AuditService(self.session).record_event(
            event_type=AuditEventType.REFRESH,
            user_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent,
            details={"session_id": token_payload.sid or ""},
        )
        await self.session.commit()
        return user, tokens

    async def logout(
        self,
        *,
        refresh_token: str | None,
        ip_address: str | None,
        user_agent: str | None,
    ) -> None:
        if not refresh_token:
            return
        try:
            token_payload = decode_token(refresh_token, expected_type="refresh")
        except ValueError:
            return

        redis = get_redis_client()
        await redis.delete(self._session_key(token_payload.sid or ""))
        await AuditService(self.session).record_event(
            event_type=AuditEventType.LOGOUT,
            user_id=token_payload.sub,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"session_id": token_payload.sid or ""},
        )
        await self.session.commit()

    async def touch_admin_activity(self, *, user_id: str, role: UserRole) -> None:
        if role not in {UserRole.ADMIN, UserRole.OWNER}:
            return
        redis = get_redis_client()
        settings = get_settings()
        key = self._admin_activity_key(user_id)
        now_value = int(datetime.now(timezone.utc).timestamp())
        await redis.set(key, now_value, ex=settings.refresh_token_ttl_days * 24 * 60 * 60)

    async def enforce_admin_idle_timeout(self, *, user_id: str, role: UserRole) -> None:
        if role not in {UserRole.ADMIN, UserRole.OWNER}:
            return
        redis = get_redis_client()
        settings = get_settings()
        key = self._admin_activity_key(user_id)
        last_activity = await redis.get(key)
        now_value = int(datetime.now(timezone.utc).timestamp())
        if last_activity and now_value - int(last_activity) > settings.admin_idle_timeout_minutes * 60:
            await redis.delete(key)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin session expired due to inactivity.")
        await redis.set(key, now_value, ex=settings.refresh_token_ttl_days * 24 * 60 * 60)

    async def _persist_session(self, *, user: User, tokens: AuthTokens) -> None:
        redis = get_redis_client()
        settings = get_settings()
        await redis.hset(
            self._session_key(tokens.session_id),
            mapping={
                "user_id": str(user.id),
                "role": user.role,
                "refresh_jti": tokens.refresh_jti,
            },
        )
        await redis.expire(self._session_key(tokens.session_id), settings.refresh_token_ttl_days * 24 * 60 * 60)
        await self.touch_admin_activity(user_id=str(user.id), role=user.role)

    @staticmethod
    def _session_key(session_id: str) -> str:
        return f"auth:session:{session_id}"

    @staticmethod
    def _admin_activity_key(user_id: str) -> str:
        return f"auth:admin-activity:{user_id}"
