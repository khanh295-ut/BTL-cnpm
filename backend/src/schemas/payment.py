# backend/src/schemas/payment.py

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PaymentBase(BaseModel):
    amount: float
    currency: str = "VND"
    status: str = "PENDING"


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    amount: float | None = None
    currency: str | None = None
    status: str | None = None


class PaymentResponse(PaymentBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime