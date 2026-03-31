from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.common.enums import AppointmentStatus, PaymentStatus
from app.modules.reports.repository import ReportsRepository
from app.modules.reports.schemas import DoctorLoadItem, DoctorLoadReportResponse, ReportPeriod, RevenueReportResponse


@dataclass(slots=True)
class ReportsService:
    session: AsyncSession

    async def build_revenue_report(self, *, date_from: datetime, date_to: datetime) -> RevenueReportResponse:
        repository = ReportsRepository(self.session)
        payments = await repository.list_payments_between(date_from=date_from, date_to=date_to)

        total_amount = sum((payment.amount for payment in payments if payment.status == PaymentStatus.PAID), Decimal("0.00"))
        paid_transactions = sum(1 for payment in payments if payment.status == PaymentStatus.PAID)
        pending_transactions = sum(1 for payment in payments if payment.status == PaymentStatus.PENDING)

        return RevenueReportResponse(
            period=ReportPeriod(date_from=date_from, date_to=date_to),
            total_amount=total_amount,
            paid_transactions=paid_transactions,
            pending_transactions=pending_transactions,
        )

    async def build_doctor_load_report(self, *, date_from: datetime, date_to: datetime) -> DoctorLoadReportResponse:
        repository = ReportsRepository(self.session)
        doctors = await repository.list_doctors()
        doctor_ids = [str(doctor.id) for doctor in doctors]
        appointments = await repository.list_doctor_appointments_between(
            doctor_ids=doctor_ids,
            date_from=date_from,
            date_to=date_to,
        )

        stats: dict[str, DoctorLoadItem] = {}
        for doctor in doctors:
            if not doctor.doctor_profile:
                continue
            stats[str(doctor.id)] = DoctorLoadItem(
                doctor_id=str(doctor.id),
                doctor_name=f"{doctor.first_name} {doctor.last_name}",
                specialty=doctor.doctor_profile.specialty,
                completed_appointments=0,
                scheduled_appointments=0,
            )

        for appointment in appointments:
            bucket = stats[str(appointment.doctor_id)]
            if appointment.status == AppointmentStatus.COMPLETED:
                bucket.completed_appointments += 1
            if appointment.status == AppointmentStatus.SCHEDULED:
                bucket.scheduled_appointments += 1

        ordered_stats = sorted(
            stats.values(),
            key=lambda item: (item.completed_appointments, item.scheduled_appointments),
            reverse=True,
        )
        return DoctorLoadReportResponse(
            period=ReportPeriod(date_from=date_from, date_to=date_to),
            doctors=ordered_stats,
        )

