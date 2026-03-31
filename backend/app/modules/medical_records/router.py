from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import csrf_protected, require_roles
from app.db.session import get_db_session
from app.modules.common.enums import UserRole
from app.modules.medical_records.schemas import MedicalRecordResponse, MedicalRecordUpsertRequest
from app.modules.medical_records.service import MedicalRecordsService
from app.modules.users.model import User


router = APIRouter(prefix="/medical-records", tags=["medical-records"])


def _build_record_response(record: object) -> MedicalRecordResponse:
    return MedicalRecordResponse(
        id=str(record.id),
        appointment_id=str(record.appointment_id),
        patient_id=str(record.patient_id),
        doctor_id=str(record.doctor_id),
        complaints=record.complaints,
        diagnosis=record.diagnosis,
        treatment_plan=record.treatment_plan,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@router.get("/mine", response_model=list[MedicalRecordResponse])
async def list_my_records(
    current_user: User = Depends(require_roles(UserRole.PATIENT)),
    session: AsyncSession = Depends(get_db_session),
) -> list[MedicalRecordResponse]:
    records = await MedicalRecordsService(session).list_for_patient(current_user)
    return [_build_record_response(record) for record in records]


@router.get("/patient/{patient_id}", response_model=list[MedicalRecordResponse])
async def list_patient_records(
    patient_id: str,
    current_user: User = Depends(require_roles(UserRole.DOCTOR, UserRole.ADMIN, UserRole.OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> list[MedicalRecordResponse]:
    records = await MedicalRecordsService(session).list_for_patient(current_user, patient_id=patient_id)
    return [_build_record_response(record) for record in records]


@router.post(
    "",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protected)],
)
async def upsert_medical_record(
    payload: MedicalRecordUpsertRequest,
    current_user: User = Depends(require_roles(UserRole.DOCTOR)),
    session: AsyncSession = Depends(get_db_session),
) -> MedicalRecordResponse:
    record = await MedicalRecordsService(session).upsert_record(actor=current_user, **payload.model_dump())
    return _build_record_response(record)

