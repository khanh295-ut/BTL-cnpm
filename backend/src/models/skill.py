import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# Import chuẩn từ backend.src.config.database
from backend.src.config.database import Base


class Skill(Base):
    __tablename__ = "skills"
    __table_args__ = {"extend_existing": True}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    expert_id = Column(
        UUID(as_uuid=True),
        ForeignKey("experts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(100), nullable=False)

    # Relationships
    expert = relationship(
        "Expert",
        back_populates="skills",
        lazy="joined",
    )

    def __repr__(self):
        return f"<Skill(id={self.id}, name='{self.name}')>"
