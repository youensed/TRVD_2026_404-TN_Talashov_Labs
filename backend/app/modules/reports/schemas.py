from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ReportPeriod(BaseModel):
    date_from: datetime
    date_to: datetime


class RevenueReportResponse(BaseModel):
    period: ReportPeriod
    total_amount: Decimal
    paid_transactions: int
    pending_transactions: int


class DoctorLoadItem(BaseModel):
    doctor_id: UUID
    doctor_name: str
    specialty: str
    completed_appointments: int
    scheduled_appointments: int


class DoctorLoadReportResponse(BaseModel):
    period: ReportPeriod
    doctors: list[DoctorLoadItem]
