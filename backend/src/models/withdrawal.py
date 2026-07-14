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


class Withdrawal(Base):
    """
    Yêu cầu rút tiền của người dùng.

    Quy trình:

        User
          │
          ▼
      PENDING
          │
      ┌───┴────────┐
      ▼            ▼
    APPROVED    REJECTED
      │
      ▼
    COMPLETED

    Khi APPROVED:
        - Trừ tiền trong Wallet
        - Sinh WalletTransaction
        - Có thể tạo Payment nếu chuyển khoản qua ngân hàng
    """

    __tablename__ = "withdrawals"

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

    wallet_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "wallets.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ======================================================
    # AMOUNT
    # ======================================================

    amount = Column(
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
    # BANK INFORMATION
    # ======================================================

    bank_name = Column(
        String(255),
        nullable=False,
    )

    account_name = Column(
        String(255),
        nullable=False,
    )

    account_number = Column(
        String(100),
        nullable=False,
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

    note = Column(
        Text,
        nullable=True,
    )

    rejection_reason = Column(
        Text,
        nullable=True,
    )

    # ======================================================
    # TIME
    # ======================================================

    requested_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    processed_at = Column(
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

    wallet = relationship(
        "Wallet",
        back_populates="withdrawals",
    )

    user = relationship(
        "User",
        back_populates="withdrawals",
    )

    # ======================================================

    def __repr__(self):
        return (
            f"<Withdrawal("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"amount={self.amount}, "
            f"status='{self.status}'"
            f")>"
        )