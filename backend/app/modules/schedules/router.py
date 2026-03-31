from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import csrf_protected, get_current_user, require_roles
from app.db.session import get_db_session
from app.modules.common.enums import UserRole
from app.modules.schedules.schemas import DoctorScheduleResponse, ScheduleShiftCreateRequest, ScheduleShiftResponse, ScheduleShiftUpdateRequest
from app.modules.schedules.service import SchedulesService


router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.get("", response_model=list[DoctorScheduleResponse])
async def list_available_schedule(
    specialty: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    _: object = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[DoctorScheduleResponse]:
    return await SchedulesService(session).list_available_schedule(
        specialty=specialty,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/shifts", response_model=list[ScheduleShiftResponse])
async def list_shifts(
    doctor_id: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    _: object = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[ScheduleShiftResponse]:
    shifts = await SchedulesService(session).list_shifts(
        doctor_id=doctor_id,
        date_from=date_from,
        date_to=date_to,
    )
    return [ScheduleShiftResponse.model_validate(shift, from_attributes=True) for shift in shifts]


@router.post(
    "/shifts",
    response_model=ScheduleShiftResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protected)],
)
async def create_shift(
    payload: ScheduleShiftCreateRequest,
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> ScheduleShiftResponse:
    shift = await SchedulesService(session).create_shift(**payload.model_dump())
    return ScheduleShiftResponse.model_validate(shift, from_attributes=True)


@router.patch(
    "/shifts/{shift_id}",
    response_model=ScheduleShiftResponse,
    dependencies=[Depends(csrf_protected)],
)
async def update_shift(
    shift_id: str,
    payload: ScheduleShiftUpdateRequest,
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> ScheduleShiftResponse:
    shift = await SchedulesService(session).update_shift(shift_id, **payload.model_dump())
    return ScheduleShiftResponse.model_validate(shift, from_attributes=True)


@router.delete("/shifts/{shift_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(csrf_protected)])
async def delete_shift(
    shift_id: str,
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    await SchedulesService(session).delete_shift(shift_id)
