from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DoctorResponse(BaseModel):
    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    specialty: str
    cabinet_number: str
    bio: str | None

    model_config = ConfigDict(from_attributes=True)
