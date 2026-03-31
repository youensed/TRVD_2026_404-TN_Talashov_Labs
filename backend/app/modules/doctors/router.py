from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.session import get_db_session
from app.modules.doctors.schemas import DoctorResponse
from app.modules.doctors.service import DoctorsService


router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("", response_model=list[DoctorResponse])
async def list_doctors(
    specialty: str | None = Query(default=None),
    _: object = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[DoctorResponse]:
    doctors = await DoctorsService(session).list_doctors(specialty=specialty)
    return [
        DoctorResponse(
            id=str(doctor.doctor_profile.id),
            user_id=str(doctor.id),
            first_name=doctor.first_name,
            last_name=doctor.last_name,
            specialty=doctor.doctor_profile.specialty,
            cabinet_number=doctor.doctor_profile.cabinet_number,
            bio=doctor.doctor_profile.bio,
        )
        for doctor in doctors
        if doctor.doctor_profile
    ]
