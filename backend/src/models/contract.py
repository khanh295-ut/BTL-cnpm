import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
# ĐÃ SỬA: Thêm "relationship" vào gói import từ sqlalchemy.orm
from sqlalchemy.orm import relationship 

from backend.src.config.database import Base

class Contract(Base):
    __tablename__ = "contracts"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    expert_id = Column(UUID(as_uuid=True), ForeignKey("experts.id", ondelete="CASCADE"), nullable=False)
    terms = Column(String(500), nullable=False)
    status = Column(String(50), default="PENDING", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # ĐÃ SỬA: Thêm các mối quan hệ (Relationships) để đồng bộ ánh xạ dữ liệu với Project và Expert
    project = relationship("Project", back_populates="contracts")
    expert = relationship("Expert", back_populates="contracts")