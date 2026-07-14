from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.src.config.database import Base


class Payment(Base):
    """
    Quản lý giao dịch thanh toán của một Contract.

    Một Contract có thể có nhiều Payment.
    Một Payment có thể liên kết với tối đa một Escrow.
    """

    __tablename__ = "payments"
    __table_args__ = {
        "extend_existing": True,
    }

    # ======================================================
    # PRIMARY KEY
    # ======================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # ======================================================
    # FOREIGN KEY
    # ======================================================

    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "contracts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ======================================================
    # PAYMENT INFORMATION
    # ======================================================

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="VND",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
        index=True,
    )

    # ======================================================
    # TIME
    # ======================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ======================================================
    # RELATIONSHIPS
    # ======================================================

    contract = relationship(
        "Contract",
        back_populates="payments",
    )

    escrow = relationship(
        "Escrow",
        back_populates="payment",
        uselist=False,
    )

    disputes = relationship(
        "Dispute",
        back_populates="payment",
        passive_deletes=True,
        lazy="selectin",
    )

    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(self) -> str:
        return (
            f"<Payment("
            f"id={self.id}, "
            f"contract_id={self.contract_id}, "
            f"amount={self.amount}, "
            f"currency='{self.currency}', "
            f"status='{self.status}'"
            f")>"
        )