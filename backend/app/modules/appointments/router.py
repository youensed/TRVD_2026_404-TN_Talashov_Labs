from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import csrf_protected, get_current_user, require_roles
from app.db.session import get_db_session
from app.modules.appointments.schemas import AppointmentCreateRequest, AppointmentListResponse, AppointmentResponse, AppointmentStatusUpdateRequest
from app.modules.appointments.service import AppointmentsService
from app.modules.common.enums import UserRole
from app.modules.users.model import User
from app.modules.users.schemas import UserPreview


router = APIRouter(prefix="/appointments", tags=["appointments"])


def _build_appointment_response(appointment: object) -> AppointmentResponse:
    return AppointmentResponse(
        id=str(appointment.id),
        patient=UserPreview(
            id=str(appointment.patient.id),
            first_name=appointment.patient.first_name,
            last_name=appointment.patient.last_name,
        ),
        doctor=UserPreview(
            id=str(appointment.doctor.id),
            first_name=appointment.doctor.first_name,
            last_name=appointment.doctor.last_name,
        ),
        start_time=appointment.start_time,
        end_time=appointment.end_time,
        status=appointment.status,
        created_at=appointment.created_at,
        updated_at=appointment.updated_at,
    )


@router.get("/mine", response_model=AppointmentListResponse)
async def list_my_appointments(
    current_user: User = Depends(require_roles(UserRole.PATIENT, UserRole.DOCTOR)),
    session: AsyncSession = Depends(get_db_session),
) -> AppointmentListResponse:
    appointments = await AppointmentsService(session).list_for_user(current_user)
    return AppointmentListResponse(items=[_build_appointment_response(item) for item in appointments])


@router.get("", response_model=list[AppointmentResponse])
async def list_all_appointments(
    _: User = Depends(require_roles(UserRole.ADMIN, UserRole.OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> list[AppointmentResponse]:
    appointments = await AppointmentsService(session).list_all()
    return [_build_appointment_response(item) for item in appointments]


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> AppointmentResponse:
    appointment = await AppointmentsService(session).get_appointment(appointment_id)
    if current_user.role == UserRole.PATIENT and str(appointment.patient_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions.")
    if current_user.role == UserRole.DOCTOR and str(appointment.doctor_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions.")
    return _build_appointment_response(appointment)


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protected)],
)
async def book_appointment(
    payload: AppointmentCreateRequest,
    current_user: User = Depends(require_roles(UserRole.PATIENT)),
    session: AsyncSession = Depends(get_db_session),
) -> AppointmentResponse:
    appointment = await AppointmentsService(session).book_appointment(
        patient=current_user,
        doctor_id=payload.doctor_id,
        start_time=payload.start_time,
    )
    return _build_appointment_response(appointment)


@router.patch(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
    dependencies=[Depends(csrf_protected)],
)
async def cancel_appointment(
    appointment_id: str,
    current_user: User = Depends(require_roles(UserRole.PATIENT, UserRole.DOCTOR, UserRole.ADMIN, UserRole.OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> AppointmentResponse:
    appointment = await AppointmentsService(session).cancel_appointment(appointment_id, current_user)
    return _build_appointment_response(appointment)


@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentResponse,
    dependencies=[Depends(csrf_protected)],
)
async def update_appointment_status(
    appointment_id: str,
    payload: AppointmentStatusUpdateRequest,
    current_user: User = Depends(require_roles(UserRole.DOCTOR, UserRole.ADMIN, UserRole.OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> AppointmentResponse:
    appointment = await AppointmentsService(session).update_status(
        appointment_id,
        actor=current_user,
        status_value=payload.status,
    )
    return _build_appointment_response(appointment)
