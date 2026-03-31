from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.common.utils import to_uuid
from app.modules.reminders.model import ReminderEvent


@dataclass(slots=True)
class ReminderRepository:
    session: AsyncSession

    async def exists_for_appointment(self, appointment_id: str) -> bool:
        statement = select(ReminderEvent).where(ReminderEvent.appointment_id == to_uuid(appointment_id))
        return await self.session.scalar(statement) is not None

    async def create(self, reminder: ReminderEvent) -> ReminderEvent:
        self.session.add(reminder)
        await self.session.flush()
        await self.session.refresh(reminder)
        return reminder
