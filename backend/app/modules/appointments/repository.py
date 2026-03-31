from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.appointments.model import Appointment
from app.modules.common.enums import AppointmentStatus, UserRole
from app.modules.common.utils import to_uuid, to_uuid_list


ACTIVE_APPOINTMENT_STATUSES = (
    AppointmentStatus.SCHEDULED,
    AppointmentStatus.COMPLETED,
    AppointmentStatus.NO_SHOW,
)


@dataclass(slots=True)
class AppointmentRepository:
    session: AsyncSession

    async def create(self, appointment: Appointment) -> Appointment:
        self.session.add(appointment)
        await self.session.flush()
        await self.session.refresh(appointment)
        return appointment

    async def get_by_id(self, appointment_id: str) -> Appointment | None:
        statement = (
            select(Appointment)
            .where(Appointment.id == to_uuid(appointment_id))
            .options(
                joinedload(Appointment.patient),
                joinedload(Appointment.doctor),
                joinedload(Appointment.medical_record),
                joinedload(Appointment.payment),
            )
        )
        return await self.session.scalar(statement)

    async def find_conflict(
        self,
        *,
        doctor_id: str,
        patient_id: str,
        start_time: datetime,
    ) -> Appointment | None:
        statement = select(Appointment).where(
            Appointment.start_time == start_time,
            Appointment.status.in_(ACTIVE_APPOINTMENT_STATUSES),
            or_(
                Appointment.doctor_id == to_uuid(doctor_id),
                Appointment.patient_id == to_uuid(patient_id),
            ),
        )
        return await self.session.scalar(statement)

    async def list_for_user(self, *, user_id: str, role: UserRole) -> list[Appointment]:
        statement = (
            select(Appointment)
            .options(joinedload(Appointment.patient), joinedload(Appointment.doctor))
            .order_by(Appointment.start_time.asc())
        )
        if role == UserRole.PATIENT:
            statement = statement.where(Appointment.patient_id == to_uuid(user_id))
        elif role == UserRole.DOCTOR:
            statement = statement.where(Appointment.doctor_id == to_uuid(user_id))
        result = await self.session.scalars(statement)
        return list(result.unique().all())

    async def list_all(self) -> list[Appointment]:
        statement = (
            select(Appointment)
            .options(joinedload(Appointment.patient), joinedload(Appointment.doctor))
            .order_by(Appointment.start_time.desc())
        )
        result = await self.session.scalars(statement)
        return list(result.unique().all())

    async def list_in_window(self, *, date_from: datetime, date_to: datetime) -> list[Appointment]:
        statement = (
            select(Appointment)
            .where(
                Appointment.start_time >= date_from,
                Appointment.start_time <= date_to,
                Appointment.status == AppointmentStatus.SCHEDULED,
            )
            .options(joinedload(Appointment.patient), joinedload(Appointment.doctor))
            .order_by(Appointment.start_time.asc())
        )
        result = await self.session.scalars(statement)
        return list(result.unique().all())

    async def list_for_doctors_between(
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
            )
            .options(joinedload(Appointment.patient), joinedload(Appointment.doctor))
        )
        result = await self.session.scalars(statement)
        return list(result.unique().all())

    async def update(self, appointment: Appointment) -> Appointment:
        await self.session.flush()
        await self.session.refresh(appointment)
        return appointment
