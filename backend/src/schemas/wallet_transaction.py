from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# BASE
# ==========================================================

class WalletTransactionBase(BaseModel):
    transaction_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    amount: Decimal = Field(
        ...,
        gt=0,
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
    )

    reference_type: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    reference_id: Optional[UUID] = None


# ==========================================================
# CREATE
# ==========================================================

class WalletTransactionCreate(WalletTransactionBase):
    wallet_id: UUID


# ==========================================================
# UPDATE
# ==========================================================

class WalletTransactionUpdate(BaseModel):
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
    )

    status: Optional[str] = Field(
        default=None,
        max_length=30,
    )


# ==========================================================
# RESPONSE
# ==========================================================

class WalletTransactionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    wallet_id: UUID

    transaction_type: str

    amount: Decimal

    balance_before: Decimal

    balance_after: Decimal

    available_before: Decimal

    available_after: Decimal

    locked_before: Decimal

    locked_after: Decimal

    currency: str

    status: str

    description: Optional[str]

    reference_type: Optional[str]

    reference_id: Optional[UUID]

    created_at: datetime


# ==========================================================
# HISTORY FILTER
# ==========================================================

class WalletTransactionFilter(BaseModel):
    transaction_type: Optional[str] = None

    status: Optional[str] = None

    from_date: Optional[datetime] = None

    to_date: Optional[datetime] = None