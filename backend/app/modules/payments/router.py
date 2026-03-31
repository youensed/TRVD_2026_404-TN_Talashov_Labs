from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import csrf_protected, require_roles
from app.db.session import get_db_session
from app.modules.common.enums import UserRole
from app.modules.payments.schemas import PaymentCreateRequest, PaymentResponse
from app.modules.payments.service import PaymentsService


router = APIRouter(prefix="/payments", tags=["payments"])


def _build_payment_response(payment: object) -> PaymentResponse:
    return PaymentResponse(
        id=str(payment.id),
        appointment_id=str(payment.appointment_id),
        patient_id=str(payment.patient_id),
        amount=payment.amount,
        currency=payment.currency,
        status=payment.status,
        method=payment.method,
        created_at=payment.created_at,
        updated_at=payment.updated_at,
    )


@router.get("", response_model=list[PaymentResponse])
async def list_payments(
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> list[PaymentResponse]:
    payments = await PaymentsService(session).list_payments()
    return [_build_payment_response(payment) for payment in payments]


@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(csrf_protected)],
)
async def create_payment(
    payload: PaymentCreateRequest,
    _: object = Depends(require_roles(UserRole.ADMIN, UserRole.OWNER)),
    session: AsyncSession = Depends(get_db_session),
) -> PaymentResponse:
    payment = await PaymentsService(session).create_payment(
        appointment_id=payload.appointment_id,
        amount=payload.amount,
        currency=payload.currency,
        status_value=payload.status,
        method=payload.method,
    )
    return _build_payment_response(payment)

