from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.appointments.repository import AppointmentRepository
from app.modules.common.enums import AppointmentStatus, UserRole
from app.modules.common.utils import ensure_utc, to_uuid
from app.modules.medical_records.model import MedicalRecord
from app.modules.medical_records.repository import MedicalRecordRepository
from app.modules.users.model import User


@dataclass(slots=True)
class MedicalRecordsService:
    session: AsyncSession

    async def list_for_patient(self, actor: User, patient_id: str | None = None) -> list[MedicalRecord]:
        repository = MedicalRecordRepository(self.session)
        if actor.role == UserRole.PATIENT:
            return await repository.list_for_patient(str(actor.id))
        if actor.role in {UserRole.DOCTOR, UserRole.ADMIN, UserRole.OWNER} and patient_id:
            return await repository.list_for_patient(patient_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Patient id is required.")

    async def upsert_record(
        self,
        *,
        actor: User,
        appointment_id: str,
        complaints: str,
        diagnosis: str,
        treatment_plan: str,
    ) -> MedicalRecord:
        if actor.role != UserRole.DOCTOR:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can update medical records.")

        appointment_repository = AppointmentRepository(self.session)
        appointment = await appointment_repository.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")
        if str(appointment.doctor_id) != str(actor.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Doctor can update only own appointments.")
        if appointment.status == AppointmentStatus.CANCELLED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cancelled appointment cannot have medical record.")
        if ensure_utc(appointment.start_time) > datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Medical record can be filled only after appointment starts.")

        repository = MedicalRecordRepository(self.session)
        record = await repository.get_by_appointment_id(appointment_id)
        if record is None:
            record = MedicalRecord(
                appointment_id=to_uuid(appointment_id),
                patient_id=appointment.patient_id,
                doctor_id=appointment.doctor_id,
                complaints=complaints,
                diagnosis=diagnosis,
                treatment_plan=treatment_plan,
            )
        else:
            record.complaints = complaints
            record.diagnosis = diagnosis
            record.treatment_plan = treatment_plan

        saved = await repository.save(record)
        if appointment.status == AppointmentStatus.SCHEDULED:
            appointment.status = AppointmentStatus.COMPLETED
            await appointment_repository.update(appointment)
        await self.session.commit()
        return saved
