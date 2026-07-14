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
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class WalletTransaction(Base):
    """
    Lưu lịch sử biến động số dư của ví.

    Ví dụ:
    - DEPOSIT: nạp tiền
    - WITHDRAW: rút tiền
    - LOCK: khóa tiền ký quỹ
    - RELEASE: mở khóa tiền
    - TRANSFER_IN: nhận tiền chuyển
    - TRANSFER_OUT: chuyển tiền đi
    - PAYMENT: thanh toán
    - REFUND: hoàn tiền
    """

    __tablename__ = "wallet_transactions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    wallet_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "wallets.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    transaction_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    amount = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    balance_before = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    balance_after = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    available_before = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    available_after = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    locked_before = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    locked_after = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    currency = Column(
        String(10),
        nullable=False,
        default="VND",
    )

    status = Column(
        String(30),
        nullable=False,
        default="COMPLETED",
        index=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    reference_type = Column(
        String(50),
        nullable=True,
        index=True,
    )

    reference_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    # ======================================================
    # RELATIONSHIPS
    # ======================================================

    wallet = relationship(
        "Wallet",
        back_populates="transactions",
    )

    def __repr__(self) -> str:
        return (
            f"<WalletTransaction("
            f"id={self.id}, "
            f"wallet_id={self.wallet_id}, "
            f"type='{self.transaction_type}', "
            f"amount={self.amount}, "
            f"status='{self.status}'"
            f")>"
        )