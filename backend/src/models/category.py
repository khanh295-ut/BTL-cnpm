import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"extend_existing": True}

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

    name = Column(
        String(100),
        unique=True,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    # ======================================================
    # RELATIONSHIPS
    # ======================================================

    projects = relationship(
        "Project",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    ai_services = relationship(
        "AIService",
        back_populates="category",
        lazy="selectin",
    )

    # ======================================================

    def __repr__(self) -> str:
        return (
            f"<Category("
            f"id={self.id}, "
            f"name='{self.name}'"
            f")>"
        )