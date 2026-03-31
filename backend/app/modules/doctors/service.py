from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.doctors.repository import DoctorRepository
from app.modules.users.model import User


@dataclass(slots=True)
class DoctorsService:
    session: AsyncSession

    async def list_doctors(self, specialty: str | None = None) -> list[User]:
        repository = DoctorRepository(self.session)
        return await repository.list_doctors(specialty=specialty)

    async def get_doctor(self, user_id: str) -> User | None:
        repository = DoctorRepository(self.session)
        return await repository.get_doctor(user_id)
