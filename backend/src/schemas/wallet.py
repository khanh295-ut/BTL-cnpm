from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ==========================================================
# BASE
# ==========================================================

class WalletBase(BaseModel):
    currency: str = Field(
        default="VND",
        min_length=1,
        max_length=10,
    )

    status: str = Field(
        default="ACTIVE",
        min_length=1,
        max_length=30,
    )


# ==========================================================
# CREATE
# ==========================================================

class WalletCreate(WalletBase):
    user_id: UUID

    balance: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )

    available_balance: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )

    locked_balance: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )

    @model_validator(mode="after")
    def validate_balances(self):
        expected_total = (
            self.available_balance
            + self.locked_balance
        )

        if self.balance != expected_total:
            raise ValueError(
                "balance must equal available_balance + locked_balance."
            )

        return self


# ==========================================================
# UPDATE
# ==========================================================

class WalletUpdate(BaseModel):
    currency: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=10,
    )

    status: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=30,
    )


# ==========================================================
# AMOUNT REQUEST
# Dùng cho nạp, khóa, mở khóa và rút tiền.
# ==========================================================

class WalletAmountRequest(BaseModel):
    amount: Decimal = Field(
        ...,
        gt=0,
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
    )


# ==========================================================
# TRANSFER REQUEST
# ==========================================================

class WalletTransferRequest(BaseModel):
    from_user_id: UUID

    to_user_id: UUID

    amount: Decimal = Field(
        ...,
        gt=0,
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    @model_validator(mode="after")
    def validate_users(self):
        if self.from_user_id == self.to_user_id:
            raise ValueError(
                "Sender and receiver must be different users."
            )

        return self


# ==========================================================
# BALANCE RESPONSE
# ==========================================================

class WalletBalanceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    balance: Decimal

    available_balance: Decimal

    locked_balance: Decimal

    currency: str


# ==========================================================
# RESPONSE
# ==========================================================

class WalletResponse(WalletBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    user_id: UUID

    balance: Decimal

    available_balance: Decimal

    locked_balance: Decimal

    created_at: datetime

    updated_at: datetime