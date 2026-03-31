from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.common.enums import UserRole


class UserPreview(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)


class CurrentUserResponse(BaseModel):
    id: UUID
    email: EmailStr | None
    role: UserRole
    first_name: str
    last_name: str
    phone: str | None
    is_verified: bool
    specialty: str | None = None
    cabinet_number: str | None = None


class PatientResponse(BaseModel):
    id: UUID
    email: EmailStr | None
    first_name: str
    last_name: str
    phone: str | None
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatientCreateRequest(BaseModel):
    email: EmailStr | None = None
    first_name: str = Field(min_length=2, max_length=80)
    last_name: str = Field(min_length=2, max_length=80)
    phone: str | None = Field(default=None, max_length=32)
    is_verified: bool = True


class PatientUpdateRequest(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = Field(default=None, min_length=2, max_length=80)
    last_name: str | None = Field(default=None, min_length=2, max_length=80)
    phone: str | None = Field(default=None, max_length=32)
    is_verified: bool | None = None
