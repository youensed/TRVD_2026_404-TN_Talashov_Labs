from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.modules.appointments.repository import ACTIVE_APPOINTMENT_STATUSES, AppointmentRepository
from app.modules.common.utils import ensure_utc, to_uuid
from app.modules.doctors.repository import DoctorRepository
from app.modules.doctors.schemas import DoctorResponse
from app.modules.schedules.model import ScheduleShift
from app.modules.schedules.repository import ScheduleRepository
from app.modules.schedules.schemas import DoctorScheduleResponse, ScheduleSlotResponse


@dataclass(slots=True)
class SchedulesService:
    session: AsyncSession

    async def create_shift(
        self,
        *,
        doctor_id: str,
        start_time: datetime,
        end_time: datetime,
        slot_minutes: int,
        is_active: bool,
    ) -> ScheduleShift:
        if end_time <= start_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Shift end time must be after start time.")

        doctor = await DoctorRepository(self.session).get_doctor(doctor_id)
        if not doctor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")

        repository = ScheduleRepository(self.session)
        overlaps = await repository.find_overlaps(
            doctor_id=doctor_id,
            start_time=start_time,
            end_time=end_time,
        )
        if overlaps:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Shift overlaps with an existing shift.")

        shift = ScheduleShift(
            doctor_id=to_uuid(doctor_id),
            start_time=start_time,
            end_time=end_time,
            slot_minutes=slot_minutes,
            is_active=is_active,
        )
        created = await repository.create(shift)
        await self.session.commit()
        return created

    async def update_shift(
        self,
        shift_id: str,
        *,
        start_time: datetime | None,
        end_time: datetime | None,
        slot_minutes: int | None,
        is_active: bool | None,
    ) -> ScheduleShift:
        repository = ScheduleRepository(self.session)
        shift = await repository.get_by_id(shift_id)
        if not shift:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found.")

        if start_time is not None:
            shift.start_time = start_time
        if end_time is not None:
            shift.end_time = end_time
        if slot_minutes is not None:
            shift.slot_minutes = slot_minutes
        if is_active is not None:
            shift.is_active = is_active

        if shift.end_time <= shift.start_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Shift end time must be after start time.")

        overlaps = await repository.find_overlaps(
            doctor_id=str(shift.doctor_id),
            start_time=shift.start_time,
            end_time=shift.end_time,
            exclude_shift_id=str(shift.id),
        )
        if overlaps:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Shift overlaps with an existing shift.")

        await repository.create(shift)
        await self.session.commit()
        return shift

    async def delete_shift(self, shift_id: str) -> None:
        repository = ScheduleRepository(self.session)
        shift = await repository.get_by_id(shift_id)
        if not shift:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found.")
        await repository.delete(shift)
        await self.session.commit()

    async def list_shifts(
        self,
        *,
        doctor_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[ScheduleShift]:
        repository = ScheduleRepository(self.session)
        return await repository.list_shifts(
            doctor_id=doctor_id,
            date_from=date_from,
            date_to=date_to,
        )

    async def list_available_schedule(
        self,
        *,
        specialty: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> list[DoctorScheduleResponse]:
        settings = get_settings()
        start_at = ensure_utc(date_from or datetime.now().astimezone())
        end_at = ensure_utc(date_to or (start_at + timedelta(days=7)))

        doctor_repository = DoctorRepository(self.session)
        schedule_repository = ScheduleRepository(self.session)
        appointment_repository = AppointmentRepository(self.session)

        doctors = await doctor_repository.list_doctors(specialty=specialty)
        if not doctors:
            return []

        doctor_ids = [str(doctor.id) for doctor in doctors]
        shifts = await schedule_repository.list_shifts(
            date_from=start_at,
            date_to=end_at,
            active_only=True,
        )
        appointments = await appointment_repository.list_for_doctors_between(
            doctor_ids=doctor_ids,
            date_from=start_at,
            date_to=end_at,
        )

        busy_slots = {
            (str(appointment.doctor_id), ensure_utc(appointment.start_time))
            for appointment in appointments
            if appointment.status in ACTIVE_APPOINTMENT_STATUSES
        }

        shifts_by_doctor: dict[str, list[ScheduleShift]] = {doctor_id: [] for doctor_id in doctor_ids}
        for shift in shifts:
            doctor_key = str(shift.doctor_id)
            if doctor_key in shifts_by_doctor:
                shifts_by_doctor[doctor_key].append(shift)

        schedule_rows: list[DoctorScheduleResponse] = []
        for doctor in doctors:
            slots: list[ScheduleSlotResponse] = []
            for shift in shifts_by_doctor.get(str(doctor.id), []):
                slot_start = ensure_utc(shift.start_time)
                shift_end = ensure_utc(shift.end_time)
                slot_step = shift.slot_minutes or settings.default_slot_minutes
                while slot_start + timedelta(minutes=slot_step) <= shift_end:
                    if slot_start >= start_at and slot_start <= end_at:
                        is_busy = (str(doctor.id), slot_start) in busy_slots
                        if not is_busy:
                            slots.append(
                                ScheduleSlotResponse(
                                    start_time=slot_start,
                                    end_time=slot_start + timedelta(minutes=slot_step),
                                    is_available=True,
                                )
                            )
                    slot_start += timedelta(minutes=slot_step)

            if slots and doctor.doctor_profile:
                schedule_rows.append(
                    DoctorScheduleResponse(
                        doctor=DoctorResponse(
                            id=str(doctor.doctor_profile.id),
                            user_id=str(doctor.id),
                            first_name=doctor.first_name,
                            last_name=doctor.last_name,
                            specialty=doctor.doctor_profile.specialty,
                            cabinet_number=doctor.doctor_profile.cabinet_number,
                            bio=doctor.doctor_profile.bio,
                        ),
                        slots=slots,
                    )
                )
        return schedule_rows
