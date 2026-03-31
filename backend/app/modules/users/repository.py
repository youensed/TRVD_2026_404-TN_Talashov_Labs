from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.common.enums import UserRole
from app.modules.common.utils import to_uuid
from app.modules.users.model import User


@dataclass(slots=True)
class UserRepository:
    session: AsyncSession

    async def get_by_id(self, user_id: str) -> User | None:
        statement = select(User).where(User.id == to_uuid(user_id)).options(selectinload(User.doctor_profile))
        return await self.session.scalar(statement)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email).options(selectinload(User.doctor_profile))
        return await self.session.scalar(statement)

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def list_patients(self) -> list[User]:
        statement = (
            select(User)
            .where(User.role == UserRole.PATIENT)
            .order_by(User.created_at.desc())
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def list_doctors(self) -> list[User]:
        statement = (
            select(User)
            .where(User.role == UserRole.DOCTOR)
            .options(selectinload(User.doctor_profile))
            .order_by(User.last_name.asc(), User.first_name.asc())
        )
        result = await self.session.scalars(statement)
        return list(result.all())

    async def update(self, user: User) -> User:
        await self.session.flush()
        await self.session.refresh(user)
        return user
