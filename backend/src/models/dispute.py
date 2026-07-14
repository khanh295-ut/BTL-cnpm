from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class Dispute(Base):
    """
    Tranh chấp phát sinh trong quá trình thực hiện hợp đồng.

    Một tranh chấp có thể liên quan đến:
    - Contract
    - Payment
    - Milestone
    - Deliverable

    Luồng trạng thái đề xuất:

        OPEN
          ↓
        UNDER_REVIEW
          ↓
        RESOLVED_CLIENT
        RESOLVED_EXPERT
        RESOLVED_PARTIAL
        CANCELLED
        CLOSED
    """

    __tablename__ = "disputes"

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
    # REQUIRED RELATIONSHIPS
    # ======================================================

    contract_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "contracts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    opened_by_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ======================================================
    # OPTIONAL REFERENCES
    # ======================================================

    payment_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "payments.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    milestone_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "milestones.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    deliverable_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "deliverables.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    assigned_admin_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    resolved_by_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # ======================================================
    # CONTENT
    # ======================================================

    title = Column(
        String(255),
        nullable=False,
    )

    reason = Column(
        String(100),
        nullable=False,
        index=True,
    )

    description = Column(
        Text,
        nullable=False,
    )

    evidence_url = Column(
        String(500),
        nullable=True,
    )

    resolution_note = Column(
        Text,
        nullable=True,
    )

    # ======================================================
    # STATUS
    # ======================================================

    status = Column(
        String(50),
        nullable=False,
        default="OPEN",
        index=True,
    )

    resolution_type = Column(
        String(50),
        nullable=True,
        index=True,
    )

    # ======================================================
    # TIME
    # ======================================================

    opened_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    closed_at = Column(
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
        back_populates="disputes",
    )

    payment = relationship(
        "Payment",
        back_populates="disputes",
    )

    milestone = relationship(
        "Milestone",
        back_populates="disputes",
    )

    deliverable = relationship(
        "Deliverable",
        back_populates="disputes",
    )

    opened_by = relationship(
        "User",
        foreign_keys=[opened_by_user_id],
        back_populates="opened_disputes",
    )

    assigned_admin = relationship(
        "User",
        foreign_keys=[assigned_admin_id],
        back_populates="assigned_disputes",
    )

    resolved_by = relationship(
        "User",
        foreign_keys=[resolved_by_user_id],
        back_populates="resolved_disputes",
    )

    def __repr__(self) -> str:
        return (
            f"<Dispute("
            f"id={self.id}, "
            f"contract_id={self.contract_id}, "
            f"opened_by_user_id={self.opened_by_user_id}, "
            f"status='{self.status}', "
            f"reason='{self.reason}'"
            f")>"
        )