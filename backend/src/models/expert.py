from __future__ import annotations

import uuid
from datetime import datetime, timezone
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


def utc_now() -> datetime:
    """
    Trả về thời gian UTC có timezone.
    """
    return datetime.now(timezone.utc)


class Expert(Base):
    """
    Thông tin chuyên gia AI trong hệ thống AITasker.

    Một Expert có thể có:
    - Một tài khoản User.
    - Nhiều Proposal.
    - Nhiều Review.
    - Nhiều Skill.
    - Nhiều Contract.
    - Nhiều Recommendation.
    - Nhiều AIService.
    - Nhiều ServiceOrder.
    """

    __tablename__ = "experts"

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
    # USER FOREIGN KEY
    # ======================================================

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=True,
        index=True,
    )

    # ======================================================
    # BASIC INFORMATION
    # ======================================================

    full_name = Column(
        String(255),
        nullable=False,
    )

    title = Column(
        String(255),
        nullable=True,
    )

    bio = Column(
        String(500),
        nullable=True,
    )

    hourly_rate = Column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    location = Column(
        String(255),
        nullable=True,
    )

    # ======================================================
    # TIME
    # ======================================================

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    # ======================================================
    # USER RELATIONSHIP
    # ======================================================

    user = relationship(
        "User",
        back_populates="expert",
        foreign_keys=[user_id],
        lazy="selectin",
    )

    # ======================================================
    # PROPOSALS
    # ======================================================

    proposals = relationship(
        "Proposal",
        back_populates="expert",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # ======================================================
    # REVIEWS
    # ======================================================

    reviews = relationship(
        "Review",
        back_populates="expert",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # ======================================================
    # SKILLS
    # ======================================================

    skills = relationship(
        "Skill",
        back_populates="expert",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # ======================================================
    # CONTRACTS
    # ======================================================

    contracts = relationship(
        "Contract",
        back_populates="expert",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # ======================================================
    # RECOMMENDATIONS
    # ======================================================

    recommendations = relationship(
        "Recommendation",
        back_populates="expert",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="Recommendation.match_score.desc()",
    )

    # ======================================================
    # AI SERVICES
    # ======================================================

    ai_services = relationship(
        "AIService",
        back_populates="expert",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="AIService.created_at.desc()",
    )

    # ======================================================
    # SERVICE ORDERS
    # ======================================================

    service_orders = relationship(
        "ServiceOrder",
        back_populates="expert",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="ServiceOrder.created_at.desc()",
    )

    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(self) -> str:
        return (
            "<Expert("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"full_name='{self.full_name}', "
            f"title='{self.title}'"
            ")>"
        )