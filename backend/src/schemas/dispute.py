from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ==========================================================
# BASE
# ==========================================================

class DisputeBase(BaseModel):
    contract_id: UUID

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    reason: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    description: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    evidence_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    payment_id: Optional[UUID] = None

    milestone_id: Optional[UUID] = None

    deliverable_id: Optional[UUID] = None


# ==========================================================
# CREATE
# ==========================================================

class DisputeCreate(DisputeBase):
    opened_by_user_id: UUID


# ==========================================================
# UPDATE
# Chỉ nên dùng khi tranh chấp chưa được xử lý hoàn tất.
# ==========================================================

class DisputeUpdate(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    reason: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    description: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=5000,
    )

    evidence_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    payment_id: Optional[UUID] = None

    milestone_id: Optional[UUID] = None

    deliverable_id: Optional[UUID] = None


# ==========================================================
# ASSIGN ADMIN
# ==========================================================

class DisputeAssignAdminRequest(BaseModel):
    assigned_admin_id: UUID


# ==========================================================
# STATUS UPDATE
# ==========================================================

class DisputeStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        min_length=1,
        max_length=50,
        examples=["UNDER_REVIEW"],
    )

    @model_validator(mode="after")
    def validate_status(self):
        normalized_status = self.status.strip().upper()

        allowed_statuses = {
            "OPEN",
            "UNDER_REVIEW",
            "RESOLVED_CLIENT",
            "RESOLVED_EXPERT",
            "RESOLVED_PARTIAL",
            "CANCELLED",
            "CLOSED",
        }

        if normalized_status not in allowed_statuses:
            raise ValueError(
                "Invalid dispute status."
            )

        self.status = normalized_status

        return self


# ==========================================================
# RESOLVE
# ==========================================================

class DisputeResolveRequest(BaseModel):
    resolved_by_user_id: UUID

    resolution_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        examples=["RESOLVED_CLIENT"],
    )

    resolution_note: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    @model_validator(mode="after")
    def validate_resolution_type(self):
        normalized_type = (
            self.resolution_type
            .strip()
            .upper()
        )

        allowed_types = {
            "RESOLVED_CLIENT",
            "RESOLVED_EXPERT",
            "RESOLVED_PARTIAL",
        }

        if normalized_type not in allowed_types:
            raise ValueError(
                "Invalid dispute resolution type."
            )

        self.resolution_type = normalized_type

        return self


# ==========================================================
# CLOSE
# ==========================================================

class DisputeCloseRequest(BaseModel):
    resolution_note: Optional[str] = Field(
        default=None,
        max_length=5000,
    )


# ==========================================================
# RESPONSE
# ==========================================================

class DisputeResponse(DisputeBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    opened_by_user_id: UUID

    assigned_admin_id: Optional[UUID] = None

    resolved_by_user_id: Optional[UUID] = None

    status: str

    resolution_type: Optional[str] = None

    resolution_note: Optional[str] = None

    opened_at: datetime

    resolved_at: Optional[datetime] = None

    closed_at: Optional[datetime] = None

    created_at: datetime

    updated_at: datetime