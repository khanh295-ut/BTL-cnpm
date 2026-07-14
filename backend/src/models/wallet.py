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
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class Wallet(Base):
    """
    Ví điện tử của người dùng trong AITasker.

    Mỗi User chỉ có duy nhất một Wallet.

    Công thức:

        balance = available_balance + locked_balance
    """

    __tablename__ = "wallets"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            name="uq_wallets_user_id",
        ),
        CheckConstraint(
            "balance >= 0",
            name="ck_wallet_balance",
        ),
        CheckConstraint(
            "available_balance >= 0",
            name="ck_wallet_available",
        ),
        CheckConstraint(
            "locked_balance >= 0",
            name="ck_wallet_locked",
        ),
        CheckConstraint(
            "balance = available_balance + locked_balance",
            name="ck_wallet_balance_consistency",
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
    # OWNER
    # ======================================================

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    # ======================================================
    # BALANCE
    # ======================================================

    balance = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    available_balance = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    locked_balance = Column(
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
        default="ACTIVE",
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

    user = relationship(
        "User",
        back_populates="wallet",
    )

    transactions = relationship(
        "WalletTransaction",
        back_populates="wallet",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="WalletTransaction.created_at.desc()",
    )

    withdrawals = relationship(
        "Withdrawal",
        back_populates="wallet",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="Withdrawal.created_at.desc()",
    )

    funded_escrows = relationship(
        "Escrow",
        foreign_keys="Escrow.payer_wallet_id",
        back_populates="payer_wallet",
        lazy="selectin",
    )

    received_escrows = relationship(
        "Escrow",
        foreign_keys="Escrow.receiver_wallet_id",
        back_populates="receiver_wallet",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Wallet("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"balance={self.balance}, "
            f"available_balance={self.available_balance}, "
            f"locked_balance={self.locked_balance}, "
            f"currency='{self.currency}', "
            f"status='{self.status}'"
            f")>"
        )