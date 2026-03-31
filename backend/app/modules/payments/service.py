from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.appointments.repository import AppointmentRepository
from app.modules.common.enums import PaymentMethod, PaymentStatus
from app.modules.common.utils import to_uuid
from app.modules.payments.model import Payment
from app.modules.payments.repository import PaymentRepository


@dataclass(slots=True)
class PaymentsService:
    session: AsyncSession

    async def create_payment(
        self,
        *,
        appointment_id: str,
        amount: Decimal,
        currency: str,
        status_value: PaymentStatus,
        method: PaymentMethod,
    ) -> Payment:
        appointment_repository = AppointmentRepository(self.session)
        appointment = await appointment_repository.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")

        payment_repository = PaymentRepository(self.session)
        if await payment_repository.get_by_appointment_id(appointment_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Payment for this appointment already exists.")

        payment = Payment(
            appointment_id=to_uuid(appointment_id),
            patient_id=appointment.patient_id,
            amount=amount,
            currency=currency.upper(),
            status=status_value,
            method=method,
        )
        created = await payment_repository.create(payment)
        await self.session.commit()
        return created

    async def list_payments(self) -> list[Payment]:
        return await PaymentRepository(self.session).list_all()
