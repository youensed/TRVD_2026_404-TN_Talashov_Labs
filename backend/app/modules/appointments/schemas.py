from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.modules.common.enums import AppointmentStatus
from app.modules.users.schemas import UserPreview


class AppointmentCreateRequest(BaseModel):
    doctor_id: str
    start_time: datetime


class AppointmentStatusUpdateRequest(BaseModel):
    status: AppointmentStatus


class AppointmentResponse(BaseModel):
    id: UUID
    patient: UserPreview
    doctor: UserPreview
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime


class AppointmentListResponse(BaseModel):
    items: list[AppointmentResponse]
