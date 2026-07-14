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


class Deliverable(Base):
    """
    Sản phẩm bàn giao của chuyên gia cho một Milestone.

    Ví dụ:
    - source_code.zip
    - report.pdf
    - demo_url
    - mô tả kết quả thực hiện
    """

    __tablename__ = "deliverables"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    milestone_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "milestones.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    file_url = Column(
        String(500),
        nullable=True,
    )

    demo_url = Column(
        String(500),
        nullable=True,
    )

    status = Column(
        String(50),
        nullable=False,
        default="DRAFT",
        index=True,
    )

    feedback = Column(
        Text,
        nullable=True,
    )

    submitted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    reviewed_at = Column(
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

    milestone = relationship(
        "Milestone",
        back_populates="deliverables",
    )
    disputes = relationship(
    "Dispute",
    back_populates="deliverable",
    passive_deletes=True,
    lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Deliverable("
            f"id={self.id}, "
            f"milestone_id={self.milestone_id}, "
            f"status='{self.status}'"
            f")>"
        )