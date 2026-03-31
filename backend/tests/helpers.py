from __future__ import annotations

from datetime import datetime

from httpx import AsyncClient

from app.core.security import hash_password
from app.modules.common.enums import UserRole
from app.modules.common.utils import to_uuid
from app.modules.doctors.model import DoctorProfile
from app.modules.schedules.model import ScheduleShift
from app.modules.users.model import User

from .conftest import TestSessionFactory


async def create_user(
    *,
    email: str,
    password: str,
    role: UserRole,
    first_name: str,
    last_name: str,
    phone: str,
    specialty: str | None = None,
) -> User:
    async with TestSessionFactory() as session:
        user = User(
            email=email,
            password_hash=hash_password(password),
            role=role,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            is_verified=True,
        )
        session.add(user)
        await session.flush()
        if specialty:
            session.add(
                DoctorProfile(
                    user_id=user.id,
                    specialty=specialty,
                    cabinet_number="12",
                    bio="Тестовий лікар",
                )
            )
        await session.commit()
        return user


async def create_shift(doctor_id: str, start_time: datetime, end_time: datetime) -> ScheduleShift:
    async with TestSessionFactory() as session:
        shift = ScheduleShift(
            doctor_id=to_uuid(doctor_id),
            start_time=start_time,
            end_time=end_time,
            slot_minutes=30,
            is_active=True,
        )
        session.add(shift)
        await session.commit()
        return shift


async def login(http_client: AsyncClient, email: str, password: str) -> None:
    response = await http_client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
