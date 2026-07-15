from __future__ import annotations

import uuid
from datetime import datetime, timezone

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


def utc_now() -> datetime:
    """
    Trả về thời gian UTC có timezone.
    """
    return datetime.now(timezone.utc)


class Enterprise(Base):
    __tablename__ = "enterprises"
    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # ======================================================
    # USER RELATIONSHIP FOREIGN KEY
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

    name = Column(
        String(255),
        nullable=False,
    )

    email = Column(
        String(120),
        unique=True,
        nullable=True,
        index=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

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
        back_populates="enterprise",
        foreign_keys=[user_id],
        lazy="selectin",
    )

    # ======================================================
    # PROJECT RELATIONSHIP
    # ======================================================

    projects = relationship(
        "Project",
        back_populates="enterprise",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # ======================================================
    # SERVICE ORDER RELATIONSHIP
    # ======================================================

    service_orders = relationship(
        "ServiceOrder",
        back_populates="enterprise",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="ServiceOrder.created_at.desc()",
    )

    def __repr__(self) -> str:
        return (
            "<Enterprise("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"name='{self.name}'"
            ")>"
        )