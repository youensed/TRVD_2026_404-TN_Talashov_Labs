from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.common.utils import to_uuid
from app.modules.audit.model import AuditLog
from app.modules.audit.repository import AuditRepository
from app.modules.common.enums import AuditEventType


@dataclass(slots=True)
class AuditService:
    session: AsyncSession

    async def record_event(
        self,
        *,
        event_type: AuditEventType,
        user_id: str | None,
        ip_address: str | None,
        user_agent: str | None,
        details: dict[str, str] | None = None,
    ) -> AuditLog:
        repository = AuditRepository(self.session)
        log_entry = AuditLog(
            user_id=to_uuid(user_id),
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
        )
        return await repository.create(log_entry)
