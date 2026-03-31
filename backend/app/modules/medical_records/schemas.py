from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MedicalRecordUpsertRequest(BaseModel):
    appointment_id: str
    complaints: str = Field(min_length=2)
    diagnosis: str = Field(min_length=2)
    treatment_plan: str = Field(min_length=2)


class MedicalRecordResponse(BaseModel):
    id: UUID
    appointment_id: UUID
    patient_id: UUID
    doctor_id: UUID
    complaints: str
    diagnosis: str
    treatment_plan: str
    created_at: datetime
    updated_at: datetime
