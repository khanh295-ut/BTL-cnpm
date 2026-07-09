from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Import chuẩn từ backend.src.config.database
from backend.src.config.database import Base


class Proposal(Base):
    __tablename__ = "proposals"
    __table_args__ = {"extend_existing": True}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
    )
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    expert_id = Column(
        UUID(as_uuid=True),
        ForeignKey("experts.id", ondelete="CASCADE"),
        nullable=False,
    )
    bid_amount = Column(Numeric(12, 2), nullable=False)
    cover_letter = Column(Text, nullable=True)
    estimated_days = Column(Integer, nullable=False)
    status = Column(String(30), default="PENDING", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="proposals")
    expert = relationship("Expert", back_populates="proposals")

    def __repr__(self):
        return f"<Proposal(id={self.id}, project_id={self.project_id}, expert_id={self.expert_id}, status='{self.status}')>"
