from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.model import AuditLog


@dataclass(slots=True)
class AuditRepository:
    session: AsyncSession

    async def create(self, log_entry: AuditLog) -> AuditLog:
        self.session.add(log_entry)
        await self.session.flush()
        await self.session.refresh(log_entry)
        return log_entry
