from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.common.enums import UserRole
from app.modules.common.utils import to_uuid
from app.modules.doctors.model import DoctorProfile
from app.modules.users.model import User


@dataclass(slots=True)
class DoctorRepository:
    session: AsyncSession

    async def list_doctors(self, specialty: str | None = None) -> list[User]:
        statement = (
            select(User)
            .join(DoctorProfile, DoctorProfile.user_id == User.id)
            .where(User.role == UserRole.DOCTOR)
            .options(selectinload(User.doctor_profile))
            .order_by(User.last_name.asc(), User.first_name.asc())
        )
        if specialty:
            statement = statement.where(DoctorProfile.specialty.ilike(f"%{specialty}%"))
        result = await self.session.scalars(statement)
        return list(result.unique().all())

    async def get_doctor(self, user_id: str) -> User | None:
        statement = (
            select(User)
            .join(DoctorProfile, DoctorProfile.user_id == User.id)
            .where(User.id == to_uuid(user_id), User.role == UserRole.DOCTOR)
            .options(selectinload(User.doctor_profile))
        )
        return await self.session.scalar(statement)

    async def create_profile(self, profile: DoctorProfile) -> DoctorProfile:
        self.session.add(profile)
        await self.session.flush()
        await self.session.refresh(profile)
        return profile
