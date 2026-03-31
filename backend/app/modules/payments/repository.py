from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.common.utils import to_uuid
from app.modules.payments.model import Payment


@dataclass(slots=True)
class PaymentRepository:
    session: AsyncSession

    async def create(self, payment: Payment) -> Payment:
        self.session.add(payment)
        await self.session.flush()
        await self.session.refresh(payment)
        return payment

    async def get_by_appointment_id(self, appointment_id: str) -> Payment | None:
        statement = select(Payment).where(Payment.appointment_id == to_uuid(appointment_id))
        return await self.session.scalar(statement)

    async def list_between(self, *, date_from: datetime, date_to: datetime) -> list[Payment]:
        statement = (
            select(Payment)
            .where(Payment.created_at >= date_from, Payment.created_at <= date_to)
            .options(joinedload(Payment.appointment))
            .order_by(Payment.created_at.desc())
        )
        result = await self.session.scalars(statement)
        return list(result.unique().all())

    async def list_all(self) -> list[Payment]:
        statement = select(Payment).order_by(Payment.created_at.desc())
        result = await self.session.scalars(statement)
        return list(result.all())
