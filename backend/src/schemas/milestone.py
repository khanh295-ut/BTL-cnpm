# backend/src/schemas/milestone.py

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# BASE
# ==========================================================

class MilestoneBase(BaseModel):
    """
    Schema cơ sở của Milestone.
    """

    contract_id: UUID

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    description: Optional[str] = Field(
        default=None,
        max_length=2000,
    )

    amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
    )

    deadline: Optional[datetime] = None

    status: str = Field(
        default="PENDING",
        max_length=50,
    )


# ==========================================================
# CREATE
# ==========================================================

class MilestoneCreate(MilestoneBase):
    """
    Schema dùng khi tạo Milestone.
    """
    pass


# ==========================================================
# UPDATE
# ==========================================================

class MilestoneUpdate(BaseModel):
    """
    Schema dùng khi cập nhật Milestone.
    """

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: Optional[str] = Field(
        default=None,
        max_length=2000,
    )

    amount: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )

    deadline: Optional[datetime] = None

    status: Optional[str] = Field(
        default=None,
        max_length=50,
    )


# ==========================================================
# RESPONSE
# ==========================================================

class MilestoneResponse(MilestoneBase):
    """
    Schema trả về cho API.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    created_at: datetime

    updated_at: datetime