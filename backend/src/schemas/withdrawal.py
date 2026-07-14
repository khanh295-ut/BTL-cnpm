from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ==========================================================
# BASE
# ==========================================================

class WithdrawalBase(BaseModel):
    amount: Decimal = Field(
        ...,
        gt=0,
        description="Số tiền cần rút",
    )

    currency: str = Field(
        default="VND",
        min_length=1,
        max_length=10,
    )

    bank_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    account_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    account_number: str = Field(
        ...,
        min_length=4,
        max_length=100,
    )

    note: Optional[str] = Field(
        default=None,
        max_length=2000,
    )


# ==========================================================
# CREATE
# ==========================================================

class WithdrawalCreate(WithdrawalBase):
    wallet_id: UUID
    user_id: UUID


# ==========================================================
# UPDATE
# Chỉ cho phép sửa khi yêu cầu vẫn còn PENDING.
# ==========================================================

class WithdrawalUpdate(BaseModel):
    amount: Optional[Decimal] = Field(
        default=None,
        gt=0,
    )

    currency: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=10,
    )

    bank_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    account_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    account_number: Optional[str] = Field(
        default=None,
        min_length=4,
        max_length=100,
    )

    note: Optional[str] = Field(
        default=None,
        max_length=2000,
    )


# ==========================================================
# STATUS UPDATE
# ==========================================================

class WithdrawalStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        min_length=1,
        max_length=30,
        examples=["APPROVED"],
    )

    rejection_reason: Optional[str] = Field(
        default=None,
        max_length=2000,
    )

    @model_validator(mode="after")
    def validate_status_and_reason(self):
        normalized_status = self.status.strip().upper()

        allowed_statuses = {
            "PENDING",
            "APPROVED",
            "REJECTED",
            "COMPLETED",
            "CANCELLED",
        }

        if normalized_status not in allowed_statuses:
            raise ValueError(
                "Invalid withdrawal status."
            )

        self.status = normalized_status

        if (
            normalized_status == "REJECTED"
            and not self.rejection_reason
        ):
            raise ValueError(
                "rejection_reason is required when status is REJECTED."
            )

        return self


# ==========================================================
# APPROVE REQUEST
# ==========================================================

class WithdrawalApproveRequest(BaseModel):
    note: Optional[str] = Field(
        default=None,
        max_length=2000,
    )


# ==========================================================
# REJECT REQUEST
# ==========================================================

class WithdrawalRejectRequest(BaseModel):
    rejection_reason: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )


# ==========================================================
# RESPONSE
# ==========================================================

class WithdrawalResponse(WithdrawalBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    wallet_id: UUID

    user_id: UUID

    status: str

    rejection_reason: Optional[str] = None

    requested_at: datetime

    processed_at: Optional[datetime] = None

    created_at: datetime

    updated_at: datetime