from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_roles
from app.db.session import get_db_session
from app.modules.common.enums import UserRole
from app.modules.reports.schemas import DoctorLoadReportResponse, RevenueReportResponse
from app.modules.reports.service import ReportsService


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/revenue", response_model=RevenueReportResponse)
async def get_revenue_report(
    date_from: datetime = Query(...),
    date_to: datetime = Query(...),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> RevenueReportResponse:
    return await ReportsService(session).build_revenue_report(date_from=date_from, date_to=date_to)


@router.get("/doctor-load", response_model=DoctorLoadReportResponse)
async def get_doctor_load_report(
    date_from: datetime = Query(...),
    date_to: datetime = Query(...),
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> DoctorLoadReportResponse:
    return await ReportsService(session).build_doctor_load_report(date_from=date_from, date_to=date_to)

