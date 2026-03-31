from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.appointments.model import Appointment
from app.modules.appointments.repository import ACTIVE_APPOINTMENT_STATUSES, AppointmentRepository
from app.modules.common.enums import AppointmentStatus, UserRole
from app.modules.common.utils import ensure_utc, to_uuid
from app.modules.doctors.repository import DoctorRepository
from app.modules.schedules.repository import ScheduleRepository
from app.modules.users.model import User


@dataclass(slots=True)
class AppointmentsService:
    session: AsyncSession

    async def book_appointment(
        self,
        *,
        patient: User,
        doctor_id: str,
        start_time: datetime,
    ) -> Appointment:
        start_time = ensure_utc(start_time)
        doctor = await DoctorRepository(self.session).get_doctor(doctor_id)
        if not doctor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")

        shift_repository = ScheduleRepository(self.session)
        shifts = await shift_repository.list_shifts(
            doctor_id=doctor_id,
            date_from=start_time,
            date_to=start_time,
            active_only=True,
        )
        matching_shift = None
        slot_end_time = None
        for shift in shifts:
            shift_start = ensure_utc(shift.start_time)
            shift_end = ensure_utc(shift.end_time)
            candidate_end = start_time + timedelta(minutes=shift.slot_minutes)
            delta_minutes = int((start_time - shift_start).total_seconds() / 60)
            if shift_start <= start_time and candidate_end <= shift_end and delta_minutes % shift.slot_minutes == 0:
                matching_shift = shift
                slot_end_time = candidate_end
                break

        if not matching_shift or not slot_end_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected slot is unavailable.")

        repository = AppointmentRepository(self.session)
        conflict = await repository.find_conflict(
            doctor_id=doctor_id,
            patient_id=str(patient.id),
            start_time=start_time,
        )
        if conflict:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Appointment slot is already booked.")

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=to_uuid(doctor_id),
            start_time=start_time,
            end_time=slot_end_time,
            status=AppointmentStatus.SCHEDULED,
        )
        created = await repository.create(appointment)
        await self.session.commit()
        loaded = await repository.get_by_id(str(created.id))
        if not loaded:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to load appointment.")
        return loaded

    async def list_for_user(self, user: User) -> list[Appointment]:
        repository = AppointmentRepository(self.session)
        if user.role in {UserRole.ADMIN, UserRole.OWNER}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Use dedicated admin views for managing appointments.",
            )
        return await repository.list_for_user(user_id=str(user.id), role=user.role)

    async def list_all(self) -> list[Appointment]:
        return await AppointmentRepository(self.session).list_all()

    async def get_appointment(self, appointment_id: str) -> Appointment:
        repository = AppointmentRepository(self.session)
        appointment = await repository.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")
        return appointment

    async def cancel_appointment(self, appointment_id: str, actor: User) -> Appointment:
        repository = AppointmentRepository(self.session)
        appointment = await repository.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")

        if actor.role == UserRole.PATIENT and str(appointment.patient_id) != str(actor.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can cancel only your own appointments.")
        if actor.role == UserRole.DOCTOR and str(appointment.doctor_id) != str(actor.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor can manage only own appointments.")
        if appointment.status != AppointmentStatus.SCHEDULED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only scheduled appointments can be cancelled.")

        now = datetime.now(timezone.utc)
        appointment_start = ensure_utc(appointment.start_time)
        if actor.role == UserRole.PATIENT and appointment_start - now < timedelta(hours=2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment cannot be cancelled later than 2 hours before start.",
            )

        appointment.status = AppointmentStatus.CANCELLED
        updated = await repository.update(appointment)
        await self.session.commit()
        return updated

    async def update_status(self, appointment_id: str, *, actor: User, status_value: AppointmentStatus) -> Appointment:
        repository = AppointmentRepository(self.session)
        appointment = await repository.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")
        if actor.role == UserRole.DOCTOR and str(appointment.doctor_id) != str(actor.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor can manage only own appointments.")
        if actor.role not in {UserRole.DOCTOR, UserRole.ADMIN, UserRole.OWNER}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions.")
        if status_value not in ACTIVE_APPOINTMENT_STATUSES and status_value != AppointmentStatus.CANCELLED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported appointment status.")

        appointment.status = status_value
        updated = await repository.update(appointment)
        await self.session.commit()
        return updated
