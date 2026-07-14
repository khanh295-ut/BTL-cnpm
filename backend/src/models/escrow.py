from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class Escrow(Base):
    """
    Quản lý tiền ký quỹ an toàn cho một Contract.

    Luồng trạng thái đề xuất:

        PENDING
            ↓
        FUNDED
            ↓
        HELD
          ↙   ↘
    RELEASED  REFUNDED

    Trạng thái bổ sung:
    - PARTIALLY_RELEASED
    - DISPUTED
    - CANCELLED

    Ý nghĩa số tiền:
    - amount: tổng giá trị ký quỹ
    - released_amount: số tiền đã giải ngân cho chuyên gia
    - refunded_amount: số tiền đã hoàn lại cho doanh nghiệp
    - remaining_amount:
        amount - released_amount - refunded_amount
    """

    __tablename__ = "escrows"

    __table_args__ = (
        UniqueConstraint(
            "contract_id",
            name="uq_escrows_contract_id",
        ),
        CheckConstraint(
            "amount >= 0",
            name="ck_escrows_amount_non_negative",
        ),
        CheckConstraint(
            "released_amount >= 0",
            name="ck_escrows_released_non_negative",
        ),
        CheckConstraint(
            "refunded_amount >= 0",
            name="ck_escrows_refunded_non_negative",
        ),
        CheckConstraint(
            "released_amount + refunded_amount <= amount",
            name="ck_escrows_amount_distribution",
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

    contract_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "contracts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    payment_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "payments.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    payer_wallet_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "wallets.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    receiver_wallet_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "wallets.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    # ======================================================
    # AMOUNTS
    # ======================================================

    amount = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    released_amount = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    refunded_amount = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    currency = Column(
        String(10),
        nullable=False,
        default="VND",
    )

    # ======================================================
    # STATUS
    # ======================================================

    status = Column(
        String(50),
        nullable=False,
        default="PENDING",
        index=True,
    )

    note = Column(
        Text,
        nullable=True,
    )

    # ======================================================
    # TIME
    # ======================================================

    funded_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    released_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    refunded_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

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

    contract = relationship(
        "Contract",
        back_populates="escrow",
    )

    payment = relationship(
        "Payment",
        back_populates="escrow",
    )

    payer_wallet = relationship(
        "Wallet",
        foreign_keys=[payer_wallet_id],
        back_populates="funded_escrows",
    )

    receiver_wallet = relationship(
        "Wallet",
        foreign_keys=[receiver_wallet_id],
        back_populates="received_escrows",
    )
    
    service_order = relationship(
    "ServiceOrder",
    back_populates="escrow",
    uselist=False,
)

    # ======================================================
    # COMPUTED PROPERTY
    # ======================================================

    @property
    def remaining_amount(self) -> Decimal:
        total = Decimal(
            str(self.amount or 0)
        )

        released = Decimal(
            str(self.released_amount or 0)
        )

        refunded = Decimal(
            str(self.refunded_amount or 0)
        )

        return total - released - refunded

    def __repr__(self) -> str:
        return (
            f"<Escrow("
            f"id={self.id}, "
            f"contract_id={self.contract_id}, "
            f"amount={self.amount}, "
            f"released_amount={self.released_amount}, "
            f"refunded_amount={self.refunded_amount}, "
            f"status='{self.status}'"
            f")>"
        )