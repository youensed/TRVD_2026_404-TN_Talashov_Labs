from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.common.enums import UserRole
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import CurrentUserResponse, PatientCreateRequest, PatientUpdateRequest


@dataclass(slots=True)
class UsersService:
    session: AsyncSession

    async def list_patients(self) -> list[User]:
        repository = UserRepository(self.session)
        return await repository.list_patients()

    async def create_patient(self, payload: PatientCreateRequest) -> User:
        repository = UserRepository(self.session)
        if payload.email and await repository.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Patient with this email already exists.")

        patient = User(
            email=payload.email,
            password_hash=None,
            role=UserRole.PATIENT,
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone=payload.phone,
            is_verified=payload.is_verified,
        )
        created = await repository.create(patient)
        await self.session.commit()
        return created

    async def update_patient(self, user_id: str, payload: PatientUpdateRequest) -> User:
        repository = UserRepository(self.session)
        patient = await repository.get_by_id(user_id)
        if not patient or patient.role != UserRole.PATIENT:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")

        if payload.email and payload.email != patient.email:
            existing_user = await repository.get_by_email(payload.email)
            if existing_user and str(existing_user.id) != str(patient.id):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Patient with this email already exists.")

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(patient, field, value)

        updated = await repository.update(patient)
        await self.session.commit()
        return updated


def build_current_user_response(user: User) -> CurrentUserResponse:
    doctor_profile = user.__dict__.get("doctor_profile")
    specialty = doctor_profile.specialty if doctor_profile else None
    cabinet_number = doctor_profile.cabinet_number if doctor_profile else None
    return CurrentUserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        is_verified=user.is_verified,
        specialty=specialty,
        cabinet_number=cabinet_number,
    )
