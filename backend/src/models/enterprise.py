from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Import chuẩn từ backend.src.config.database
from backend.src.config.database import Base


class Enterprise(Base):
    __tablename__ = "enterprises"
    __table_args__ = {"extend_existing": True}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name = Column(String(255), nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    projects = relationship(
        "Project",
        back_populates="enterprise",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<Enterprise(id={self.id}, name='{self.name}')>"
