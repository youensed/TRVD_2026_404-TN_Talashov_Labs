from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.common.utils import to_uuid
from app.modules.medical_records.model import MedicalRecord


@dataclass(slots=True)
class MedicalRecordRepository:
    session: AsyncSession

    async def get_by_appointment_id(self, appointment_id: str) -> MedicalRecord | None:
        statement = select(MedicalRecord).where(MedicalRecord.appointment_id == to_uuid(appointment_id))
        return await self.session.scalar(statement)

    async def list_for_patient(self, patient_id: str) -> list[MedicalRecord]:
        statement = (
            select(MedicalRecord)
            .where(MedicalRecord.patient_id == to_uuid(patient_id))
            .order_by(MedicalRecord.created_at.desc())
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def save(self, record: MedicalRecord) -> MedicalRecord:
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record
