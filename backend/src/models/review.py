from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class Review(Base):

    __tablename__ = "reviews"


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


    rating = Column(
        Integer,
        nullable=False
    )


    comment = Column(
        Text,
        nullable=False
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    project = relationship(
        "Project",
        back_populates="reviews"
    )


    expert = relationship(
        "Expert",
        back_populates="reviews"
    )