from datetime import datetime
import uuid

from sqlalchemy import Column, DateTime, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class Expert(Base):
    __tablename__ = "experts"
    __table_args__ = {"extend_existing": True}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    full_name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=True)
    bio = Column(String(500), nullable=True)
    hourly_rate = Column(Numeric(12, 2), nullable=False, default=0)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    proposals = relationship("Proposal", back_populates="expert", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="expert", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="expert", cascade="all, delete-orphan", lazy="selectin")
    contracts = relationship("Contract", back_populates="expert", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<Expert(id={self.id}, full_name='{self.full_name}')>"
