from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# BASE
# ==========================================================

class NotificationBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    notification_type: str = Field(
        default="SYSTEM",
        min_length=1,
        max_length=50,
    )

    reference_type: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    reference_id: Optional[UUID] = None


# ==========================================================
# CREATE
# ==========================================================

class NotificationCreate(NotificationBase):
    user_id: UUID


# ==========================================================
# UPDATE
# Dùng cho Admin hoặc hệ thống cập nhật nội dung thông báo.
# ==========================================================

class NotificationUpdate(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    message: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=5000,
    )

    notification_type: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    reference_type: Optional[str] = Field(
        default=None,
        max_length=50,
    )

    reference_id: Optional[UUID] = None


# ==========================================================
# READ STATUS
# ==========================================================

class NotificationReadUpdate(BaseModel):
    is_read: bool = True


# ==========================================================
# RESPONSE
# ==========================================================

class NotificationResponse(NotificationBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    user_id: UUID

    is_read: bool

    created_at: datetime

    read_at: Optional[datetime] = None