from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class Contract(Base):
    """
    Hợp đồng giữa doanh nghiệp và chuyên gia AI.

    Contract có thể được tạo từ:
    - Proposal được ACCEPTED.
    - ServiceOrder được CONFIRMED.
    """

    __tablename__ = "contracts"
    __table_args__ = {
        "extend_existing": True,
    }

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

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    expert_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "experts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ======================================================
    # CONTRACT INFORMATION
    # ======================================================

    title = Column(
        String(255),
        nullable=False,
    )

    total_amount = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    currency = Column(
        String(10),
        nullable=False,
        default="VND",
    )

    terms = Column(
        String(2000),
        nullable=False,
        default=(
            "Thực hiện công việc theo nội dung đề xuất "
            "hoặc đơn dịch vụ đã được chấp nhận."
        ),
    )

    status = Column(
        String(50),
        nullable=False,
        default="PENDING",
        index=True,
    )

    # ======================================================
    # TIME
    # ======================================================

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
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

    project = relationship(
        "Project",
        back_populates="contracts",
    )

    expert = relationship(
        "Expert",
        back_populates="contracts",
    )

    payments = relationship(
        "Payment",
        back_populates="contract",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    milestones = relationship(
        "Milestone",
        back_populates="contract",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="Milestone.created_at",
    )

    service_order = relationship(
        "ServiceOrder",
        back_populates="contract",
        uselist=False,
    )

    disputes = relationship(
        "Dispute",
        back_populates="contract",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="Dispute.created_at.desc()",
    )

    escrow = relationship(
    "Escrow",
    back_populates="contract",
    cascade="all, delete-orphan",
    passive_deletes=True,
    lazy="selectin",
    uselist=False,
    )
    # ======================================================

    def __repr__(self) -> str:
        return (
            f"<Contract("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"total_amount={self.total_amount}, "
            f"status='{self.status}'"
            f")>"
        )