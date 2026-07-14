from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class ServiceOrder(Base):
    """
    Đơn đặt mua dịch vụ AI trên Marketplace.

    Luồng trạng thái đề xuất:

        PENDING
            ↓
        CONFIRMED
            ↓
        IN_PROGRESS
            ↓
        DELIVERED
          ↙     ↘
    COMPLETED  DISPUTED

    Trạng thái bổ sung:

    - CANCELLED
    - REFUNDED

    Luồng nghiệp vụ:

        Enterprise đặt AIService
        → tạo ServiceOrder
        → tạo Contract
        → tạo Escrow
        → Expert thực hiện
        → giao Deliverable
        → Enterprise duyệt
        → Escrow giải ngân
    """

    __tablename__ = "service_orders"

    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name="ck_service_orders_price_non_negative",
        ),
        CheckConstraint(
            "delivery_days > 0",
            name="ck_service_orders_delivery_days_positive",
        ),
        CheckConstraint(
            "revision_count >= 0",
            name="ck_service_orders_revision_count_non_negative",
        ),
    )

    # ======================================================
    # PRIMARY KEY
    # ======================================================

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # ======================================================
    # FOREIGN KEYS
    # ======================================================

    service_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "ai_services.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    enterprise_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "enterprises.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    expert_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "experts.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    contract_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "contracts.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        unique=True,
        index=True,
    )

    escrow_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "escrows.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        unique=True,
        index=True,
    )

    # ======================================================
    # SNAPSHOT INFORMATION
    #
    # Lưu thông tin dịch vụ tại thời điểm đặt đơn.
    # Sau này AIService thay đổi giá thì đơn cũ không đổi.
    # ======================================================

    service_title = Column(
        String(255),
        nullable=False,
    )

    price = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    currency = Column(
        String(10),
        nullable=False,
        default="VND",
    )

    delivery_days = Column(
        Integer,
        nullable=False,
        default=7,
    )

    revision_count = Column(
        Integer,
        nullable=False,
        default=1,
    )

    # ======================================================
    # ORDER CONTENT
    # ======================================================

    requirements = Column(
        Text,
        nullable=True,
    )

    note = Column(
        Text,
        nullable=True,
    )

    cancellation_reason = Column(
        Text,
        nullable=True,
    )

    # ======================================================
    # STATUS
    # ======================================================

    status = Column(
        String(30),
        nullable=False,
        default="PENDING",
        index=True,
    )

    # ======================================================
    # TIME
    # ======================================================

    confirmed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    delivered_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancelled_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # ======================================================
    # RELATIONSHIPS
    # ======================================================

    service = relationship(
        "AIService",
        back_populates="orders",
    )

    enterprise = relationship(
        "Enterprise",
        back_populates="service_orders",
    )

    expert = relationship(
        "Expert",
        back_populates="service_orders",
    )

    contract = relationship(
        "Contract",
        back_populates="service_order",
        uselist=False,
    )

    escrow = relationship(
        "Escrow",
        back_populates="service_order",
        uselist=False,
    )

    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(self) -> str:
        return (
            f"<ServiceOrder("
            f"id={self.id}, "
            f"service_id={self.service_id}, "
            f"enterprise_id={self.enterprise_id}, "
            f"expert_id={self.expert_id}, "
            f"price={self.price}, "
            f"currency='{self.currency}', "
            f"delivery_days={self.delivery_days}, "
            f"revision_count={self.revision_count}, "
            f"status='{self.status}'"
            f")>"
        )