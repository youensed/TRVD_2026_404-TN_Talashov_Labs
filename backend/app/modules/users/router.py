from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import csrf_protected, require_roles
from app.db.session import get_db_session
from app.modules.common.enums import UserRole
from app.modules.users.schemas import PatientCreateRequest, PatientResponse, PatientUpdateRequest
from app.modules.users.service import UsersService


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/patients", response_model=list[PatientResponse])
async def list_patients(
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> list[PatientResponse]:
    patients = await UsersService(session).list_patients()
    return [PatientResponse.model_validate(patient) for patient in patients]


@router.post(
    "/patients",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protected)],
)
async def create_patient(
    payload: PatientCreateRequest,
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> PatientResponse:
    patient = await UsersService(session).create_patient(payload)
    return PatientResponse.model_validate(patient)


@router.patch(
    "/patients/{patient_id}",
    response_model=PatientResponse,
    dependencies=[Depends(csrf_protected)],
)
async def update_patient(
    patient_id: str,
    payload: PatientUpdateRequest,
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> PatientResponse:
    patient = await UsersService(session).update_patient(patient_id, payload)
    return PatientResponse.model_validate(patient)

