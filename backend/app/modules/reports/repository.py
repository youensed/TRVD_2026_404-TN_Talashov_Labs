from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.modules.appointments.model import Appointment
from app.modules.common.enums import AppointmentStatus, PaymentStatus, UserRole
from app.modules.common.utils import to_uuid_list
from app.modules.doctors.model import DoctorProfile
from app.modules.payments.model import Payment
from app.modules.users.model import User


@dataclass(slots=True)
class ReportsRepository:
    session: AsyncSession

    async def list_payments_between(self, *, date_from: datetime, date_to: datetime) -> list[Payment]:
        statement = select(Payment).where(Payment.created_at >= date_from, Payment.created_at <= date_to)
        result = await self.session.scalars(statement)
        return list(result.all())

    async def list_doctors(self) -> list[User]:
        statement = (
            select(User)
            .join(DoctorProfile, DoctorProfile.user_id == User.id)
            .where(User.role == UserRole.DOCTOR)
            .options(selectinload(User.doctor_profile))
        )
        result = await self.session.scalars(statement)
        return list(result.unique().all())

    async def list_doctor_appointments_between(
        self,
        *,
        doctor_ids: list[str],
        date_from: datetime,
        date_to: datetime,
    ) -> list[Appointment]:
        if not doctor_ids:
            return []
        statement = (
            select(Appointment)
            .where(
                Appointment.doctor_id.in_(to_uuid_list(doctor_ids)),
                Appointment.start_time >= date_from,
                Appointment.start_time <= date_to,
                Appointment.status.in_((AppointmentStatus.SCHEDULED, AppointmentStatus.COMPLETED)),
            )
            .options(joinedload(Appointment.doctor))
        )
        result = await self.session.scalars(statement)
        return list(result.unique().all())
