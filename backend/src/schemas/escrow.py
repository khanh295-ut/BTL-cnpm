from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    model_validator,
)


# ==========================================================
# BASE
# ==========================================================

class EscrowBase(BaseModel):
    contract_id: UUID

    payment_id: Optional[UUID] = None

    payer_wallet_id: UUID

    receiver_wallet_id: UUID

    amount: Decimal = Field(
        ...,
        gt=0,
        description="Tổng số tiền ký quỹ",
    )

    currency: str = Field(
        default="VND",
        min_length=1,
        max_length=10,
    )

    note: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    @model_validator(mode="after")
    def validate_wallets(self):
        if self.payer_wallet_id == self.receiver_wallet_id:
            raise ValueError(
                "Payer wallet and receiver wallet must be different."
            )

        self.currency = self.currency.strip().upper()

        return self


# ==========================================================
# CREATE
# ==========================================================

class EscrowCreate(EscrowBase):
    pass


# ==========================================================
# UPDATE
#
# Chỉ cho phép chỉnh sửa khi Escrow chưa được cấp vốn.
# ==========================================================

class EscrowUpdate(BaseModel):
    payment_id: Optional[UUID] = None

    payer_wallet_id: Optional[UUID] = None

    receiver_wallet_id: Optional[UUID] = None

    amount: Optional[Decimal] = Field(
        default=None,
        gt=0,
    )

    currency: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=10,
    )

    note: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    @model_validator(mode="after")
    def normalize_currency(self):
        if self.currency is not None:
            self.currency = self.currency.strip().upper()

        if (
            self.payer_wallet_id is not None
            and self.receiver_wallet_id is not None
            and self.payer_wallet_id
            == self.receiver_wallet_id
        ):
            raise ValueError(
                "Payer wallet and receiver wallet must be different."
            )

        return self


# ==========================================================
# AMOUNT REQUEST
#
# Dùng cho release và refund từng phần.
# ==========================================================

class EscrowAmountRequest(BaseModel):
    amount: Decimal = Field(
        ...,
        gt=0,
    )

    note: Optional[str] = Field(
        default=None,
        max_length=5000,
    )


# ==========================================================
# FUND REQUEST
#
# Dùng để doanh nghiệp đưa tiền vào ký quỹ.
# ==========================================================

class EscrowFundRequest(BaseModel):
    note: Optional[str] = Field(
        default=None,
        max_length=5000,
    )


# ==========================================================
# STATUS UPDATE
# ==========================================================

class EscrowStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        min_length=1,
        max_length=50,
        examples=["DISPUTED"],
    )

    note: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    @model_validator(mode="after")
    def validate_status(self):
        normalized_status = self.status.strip().upper()

        allowed_statuses = {
            "PENDING",
            "FUNDED",
            "HELD",
            "PARTIALLY_RELEASED",
            "RELEASED",
            "PARTIALLY_REFUNDED",
            "REFUNDED",
            "DISPUTED",
            "CANCELLED",
        }

        if normalized_status not in allowed_statuses:
            raise ValueError(
                "Invalid escrow status."
            )

        self.status = normalized_status

        return self


# ==========================================================
# RELEASE REQUEST
# ==========================================================

class EscrowReleaseRequest(EscrowAmountRequest):
    reference_type: Optional[str] = Field(
        default="ESCROW_RELEASE",
        max_length=50,
    )

    reference_id: Optional[UUID] = None


# ==========================================================
# REFUND REQUEST
# ==========================================================

class EscrowRefundRequest(EscrowAmountRequest):
    reference_type: Optional[str] = Field(
        default="ESCROW_REFUND",
        max_length=50,
    )

    reference_id: Optional[UUID] = None


# ==========================================================
# RESPONSE
# ==========================================================

class EscrowResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    contract_id: UUID

    payment_id: Optional[UUID] = None

    payer_wallet_id: UUID

    receiver_wallet_id: UUID

    amount: Decimal

    released_amount: Decimal

    refunded_amount: Decimal

    currency: str

    status: str

    note: Optional[str] = None

    funded_at: Optional[datetime] = None

    released_at: Optional[datetime] = None

    refunded_at: Optional[datetime] = None

    created_at: datetime

    updated_at: datetime

    @computed_field
    @property
    def remaining_amount(self) -> Decimal:
        return (
            Decimal(str(self.amount or 0))
            - Decimal(str(self.released_amount or 0))
            - Decimal(str(self.refunded_amount or 0))
        )


# ==========================================================
# SUMMARY RESPONSE
# ==========================================================

class EscrowSummaryResponse(BaseModel):
    total_amount: Decimal

    total_released: Decimal

    total_refunded: Decimal

    total_remaining: Decimal

    pending_count: int

    held_count: int

    released_count: int

    refunded_count: int

    disputed_count: int