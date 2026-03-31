from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.common.enums import PaymentMethod, PaymentStatus


class PaymentCreateRequest(BaseModel):
    appointment_id: str
    amount: Decimal = Field(gt=0)
    currency: str = Field(default="UAH", min_length=3, max_length=3)
    status: PaymentStatus = PaymentStatus.PENDING
    method: PaymentMethod = PaymentMethod.CARD


class PaymentResponse(BaseModel):
    id: UUID
    appointment_id: UUID
    patient_id: UUID
    amount: Decimal
    currency: str
    status: PaymentStatus
    method: PaymentMethod
    created_at: datetime
    updated_at: datetime
