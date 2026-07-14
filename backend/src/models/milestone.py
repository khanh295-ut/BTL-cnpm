# backend/src/models/milestone.py

from __future__ import annotations

import uuid
from datetime import datetime

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


class Milestone(Base):
    """
    Milestone đại diện cho từng giai đoạn thực hiện của một Contract.

    Ví dụ:

    Contract
        ├── Phân tích yêu cầu
        ├── Thiết kế hệ thống
        ├── Phát triển AI
        ├── Kiểm thử
        └── Bàn giao
    """

    __tablename__ = "milestones"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    contract_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "contracts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    amount = Column(
        Numeric(18, 2),
        nullable=False,
        default=0,
    )

    deadline = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    status = Column(
        String(50),
        nullable=False,
        default="PENDING",
        index=True,
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

    # =====================================================
    # RELATIONSHIPS
    # =====================================================

    contract = relationship(
        "Contract",
        back_populates="milestones",
    )

    deliverables = relationship(
        "Deliverable",
        back_populates="milestone",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    disputes = relationship(
    "Dispute",
    back_populates="milestone",
    passive_deletes=True,
    lazy="selectin",
    )

    def __repr__(self):
        return (
            f"<Milestone("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"status='{self.status}'"
            f")>"
        )