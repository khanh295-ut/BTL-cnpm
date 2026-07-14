from datetime import datetime
import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {"extend_existing": True}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )

    enterprise_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "enterprises.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "categories.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
        index=True,
    )

    description = Column(
        Text,
        nullable=False,
    )

    budget = Column(
        Numeric(12, 2),
        nullable=True,
    )

    deadline = Column(
        Date,
        nullable=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="OPEN",
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    # ======================================================
    # RELATIONSHIPS
    # ======================================================

    enterprise = relationship(
        "Enterprise",
        back_populates="projects",
        lazy="joined",
    )

    category = relationship(
        "Category",
        back_populates="projects",
        lazy="joined",
    )

    proposals = relationship(
        "Proposal",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reviews = relationship(
        "Review",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    contracts = relationship(
        "Contract",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    recommendations = relationship(
        "Recommendation",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="Recommendation.match_score.desc()",
    )

    def __repr__(self) -> str:
        return (
            f"<Project("
            f"id={self.id}, "
            f"title='{self.title}', "
            f"status='{self.status}'"
            f")>"
        )