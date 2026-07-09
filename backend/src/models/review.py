from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Import chuẩn từ backend.src.config.database
from backend.src.config.database import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = {"extend_existing": True}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expert_id = Column(
        UUID(as_uuid=True),
        ForeignKey("experts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship(
        "Project",
        back_populates="reviews",
    )
    expert = relationship(
        "Expert",
        back_populates="reviews",
    )

    def __repr__(self):
        return f"<Review(id={self.id}, project_id={self.project_id}, expert_id={self.expert_id}, rating={self.rating})>"
