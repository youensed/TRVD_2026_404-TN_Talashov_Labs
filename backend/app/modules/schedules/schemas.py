from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.doctors.schemas import DoctorResponse


class ScheduleShiftCreateRequest(BaseModel):
    doctor_id: str
    start_time: datetime
    end_time: datetime
    slot_minutes: int = Field(default=30, ge=15, le=120)
    is_active: bool = True


class ScheduleShiftUpdateRequest(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    slot_minutes: int | None = Field(default=None, ge=15, le=120)
    is_active: bool | None = None


class ScheduleShiftResponse(BaseModel):
    id: UUID
    doctor_id: UUID
    start_time: datetime
    end_time: datetime
    slot_minutes: int
    is_active: bool


class ScheduleSlotResponse(BaseModel):
    start_time: datetime
    end_time: datetime
    is_available: bool


class DoctorScheduleResponse(BaseModel):
    doctor: DoctorResponse
    slots: list[ScheduleSlotResponse]
