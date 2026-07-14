from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# BASE
# ==========================================================

class DeliverableBase(BaseModel):
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    file_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    demo_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )


# ==========================================================
# CREATE
# ==========================================================

class DeliverableCreate(DeliverableBase):
    milestone_id: UUID


# ==========================================================
# UPDATE
# ==========================================================

class DeliverableUpdate(BaseModel):
    description: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    file_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    demo_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    status: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    feedback: Optional[str] = Field(
        default=None,
        max_length=5000,
    )


# ==========================================================
# REVIEW
# ==========================================================

class DeliverableReview(BaseModel):
    status: str = Field(
        ...,
        examples=["APPROVED"],
    )

    feedback: Optional[str] = None


# ==========================================================
# RESPONSE
# ==========================================================

class DeliverableResponse(DeliverableBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    milestone_id: UUID

    status: str

    feedback: Optional[str]

    submitted_at: Optional[datetime]

    reviewed_at: Optional[datetime]

    created_at: datetime

    updated_at: datetime