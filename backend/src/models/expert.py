from datetime import datetime
import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Numeric,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class Expert(Base):
    """
    Thông tin chuyên gia AI trong hệ thống AITasker.

    Một Expert có thể có:
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
        default=0,
    )

    location = Column(
        String(255),
        nullable=True,
    )

    # ======================================================
    # TIME
    # ======================================================

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    # ======================================================
    # RELATIONSHIPS
    # ======================================================

    proposals = relationship(
        "Proposal",
        back_populates="expert",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    reviews = relationship(
        "Review",
        back_populates="expert",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    skills = relationship(
        "Skill",
        back_populates="expert",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    contracts = relationship(
        "Contract",
        back_populates="expert",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    recommendations = relationship(
        "Recommendation",
        back_populates="expert",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="Recommendation.match_score.desc()",
    )

    ai_services = relationship(
        "AIService",
        back_populates="expert",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="AIService.created_at.desc()",
    )

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
            f"<Expert("
            f"id={self.id}, "
            f"full_name='{self.full_name}', "
            f"title='{self.title}'"
            f")>"
        )