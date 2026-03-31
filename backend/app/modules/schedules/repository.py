from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.common.utils import to_uuid
from app.modules.schedules.model import ScheduleShift


@dataclass(slots=True)
class ScheduleRepository:
    session: AsyncSession

    async def create(self, shift: ScheduleShift) -> ScheduleShift:
        self.session.add(shift)
        await self.session.flush()
        await self.session.refresh(shift)
        return shift

    async def get_by_id(self, shift_id: str) -> ScheduleShift | None:
        statement = select(ScheduleShift).where(ScheduleShift.id == to_uuid(shift_id))
        return await self.session.scalar(statement)

    async def list_shifts(
        self,
        *,
        doctor_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        active_only: bool = False,
    ) -> list[ScheduleShift]:
        statement = select(ScheduleShift).order_by(ScheduleShift.start_time.asc())
        if doctor_id:
            statement = statement.where(ScheduleShift.doctor_id == to_uuid(doctor_id))
        if date_from:
            statement = statement.where(ScheduleShift.end_time >= date_from)
        if date_to:
            statement = statement.where(ScheduleShift.start_time <= date_to)
        if active_only:
            statement = statement.where(ScheduleShift.is_active.is_(True))
        result = await self.session.scalars(statement)
        return list(result.all())

    async def find_overlaps(
        self,
        *,
        doctor_id: str,
        start_time: datetime,
        end_time: datetime,
        exclude_shift_id: str | None = None,
    ) -> list[ScheduleShift]:
        statement = select(ScheduleShift).where(
            ScheduleShift.doctor_id == to_uuid(doctor_id),
            ScheduleShift.is_active.is_(True),
            ScheduleShift.start_time < end_time,
            ScheduleShift.end_time > start_time,
        )
        if exclude_shift_id:
            statement = statement.where(ScheduleShift.id != to_uuid(exclude_shift_id))
        result = await self.session.scalars(statement)
        return list(result.all())

    async def delete(self, shift: ScheduleShift) -> None:
        await self.session.delete(shift)
        await self.session.flush()
