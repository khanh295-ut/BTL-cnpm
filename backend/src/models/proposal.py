from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    Numeric
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class Proposal(Base):
    __tablename__ = "proposals"


    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True
    )


    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "projects.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )


    expert_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "experts.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )


    price = Column(
        Numeric(12,2),
        nullable=False
    )


    comment = Column(
        Text,
        nullable=True
    )


    status = Column(
        String(30),
        default="PENDING",
        nullable=False
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    project = relationship(
        "Project",
        back_populates="proposals"
    )


    expert = relationship(
        "Expert",
        back_populates="proposals"
    )