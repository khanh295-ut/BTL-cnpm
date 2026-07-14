from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# ==========================================================
# BASE
# ==========================================================

class ServiceOrderBase(BaseModel):
    service_id: UUID

    enterprise_id: UUID

    requirements: Optional[str] = Field(
        default=None,
        max_length=10000,
    )

    note: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    @model_validator(mode="after")
    def normalize_text_fields(self):
        if self.requirements is not None:
            self.requirements = (
                self.requirements.strip()
            )

        if self.note is not None:
            self.note = self.note.strip()

        return self


# ==========================================================
# CREATE
#
# expert_id, giá, currency, delivery_days và revision_count
# sẽ được service lấy từ AIService để tránh frontend giả mạo.
# ==========================================================

class ServiceOrderCreate(ServiceOrderBase):
    pass


# ==========================================================
# UPDATE
#
# Chỉ cho phép sửa nội dung đơn khi còn PENDING.
# ==========================================================

class ServiceOrderUpdate(BaseModel):
    requirements: Optional[str] = Field(
        default=None,
        max_length=10000,
    )

    note: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    @model_validator(mode="after")
    def normalize_text_fields(self):
        if self.requirements is not None:
            self.requirements = (
                self.requirements.strip()
            )

        if self.note is not None:
            self.note = self.note.strip()

        return self


# ==========================================================
# STATUS UPDATE
# ==========================================================

class ServiceOrderStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        min_length=1,
        max_length=30,
        examples=["CONFIRMED"],
    )

    note: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    @model_validator(mode="after")
    def validate_status(self):
        normalized_status = (
            self.status.strip().upper()
        )

        allowed_statuses = {
            "PENDING",
            "CONFIRMED",
            "IN_PROGRESS",
            "DELIVERED",
            "COMPLETED",
            "DISPUTED",
            "CANCELLED",
            "REFUNDED",
        }

        if normalized_status not in allowed_statuses:
            raise ValueError(
                "Invalid service order status."
            )

        self.status = normalized_status

        if self.note is not None:
            self.note = self.note.strip()

        return self


# ==========================================================
# CONFIRM REQUEST
#
# Có thể truyền payment_id hoặc payer_wallet_id nếu service
# muốn tạo Escrow tự động trong bước xác nhận.
# ==========================================================

class ServiceOrderConfirmRequest(BaseModel):
    payment_id: Optional[UUID] = None

    payer_wallet_id: Optional[UUID] = None

    note: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    @model_validator(mode="after")
    def normalize_note(self):
        if self.note is not None:
            self.note = self.note.strip()

        return self


# ==========================================================
# START REQUEST
# ==========================================================

class ServiceOrderStartRequest(BaseModel):
    note: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    @model_validator(mode="after")
    def normalize_note(self):
        if self.note is not None:
            self.note = self.note.strip()

        return self


# ==========================================================
# DELIVER REQUEST
#
# Có thể mở rộng thêm deliverable_id sau này.
# ==========================================================

class ServiceOrderDeliverRequest(BaseModel):
    deliverable_id: Optional[UUID] = None

    note: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    @model_validator(mode="after")
    def normalize_note(self):
        if self.note is not None:
            self.note = self.note.strip()

        return self


# ==========================================================
# COMPLETE REQUEST
#
# release_escrow=True:
# service sẽ giải ngân toàn bộ Escrow còn lại khi hoàn thành.
# ==========================================================

class ServiceOrderCompleteRequest(BaseModel):
    release_escrow: bool = True

    note: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    @model_validator(mode="after")
    def normalize_note(self):
        if self.note is not None:
            self.note = self.note.strip()

        return self


# ==========================================================
# CANCEL REQUEST
# ==========================================================

class ServiceOrderCancelRequest(BaseModel):
    cancellation_reason: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    refund_escrow: bool = True

    @model_validator(mode="after")
    def normalize_reason(self):
        self.cancellation_reason = (
            self.cancellation_reason.strip()
        )

        return self


# ==========================================================
# DISPUTE REQUEST
#
# Có thể dùng để kết nối với module Dispute.
# ==========================================================

class ServiceOrderDisputeRequest(BaseModel):
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

    @model_validator(mode="after")
    def normalize_values(self):
        self.reason = self.reason.strip().upper()
        self.description = (
            self.description.strip()
        )

        if self.evidence_url is not None:
            self.evidence_url = (
                self.evidence_url.strip()
            )

        return self


# ==========================================================
# RESPONSE
# ==========================================================

class ServiceOrderResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    service_id: UUID

    enterprise_id: UUID

    expert_id: UUID

    contract_id: Optional[UUID] = None

    escrow_id: Optional[UUID] = None

    service_title: str

    price: Decimal

    currency: str

    delivery_days: int

    revision_count: int

    requirements: Optional[str] = None

    note: Optional[str] = None

    cancellation_reason: Optional[str] = None

    status: str

    confirmed_at: Optional[datetime] = None

    started_at: Optional[datetime] = None

    delivered_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    cancelled_at: Optional[datetime] = None

    created_at: datetime

    updated_at: datetime


# ==========================================================
# MARKETPLACE ORDER ITEM
#
# Dùng cho dashboard của Enterprise hoặc Expert.
# ==========================================================

class ServiceOrderListItem(BaseModel):
    id: UUID

    service_id: UUID

    service_title: str

    enterprise_id: UUID

    expert_id: UUID

    price: Decimal

    currency: str

    status: str

    created_at: datetime

    delivery_days: int

    confirmed_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None


# ==========================================================
# SUMMARY RESPONSE
# ==========================================================

class ServiceOrderSummaryResponse(BaseModel):
    total_orders: int

    pending_orders: int

    confirmed_orders: int

    in_progress_orders: int

    delivered_orders: int

    completed_orders: int

    disputed_orders: int

    cancelled_orders: int

    refunded_orders: int

    total_order_value: Decimal