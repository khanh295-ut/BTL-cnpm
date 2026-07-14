from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class Recommendation(Base):
    """
    Lưu kết quả gợi ý chuyên gia cho từng dự án.

    Mục đích:

    - Ghi lại chuyên gia nào đã được gợi ý cho dự án.
    - Lưu điểm phù hợp và các thành phần tạo nên điểm.
    - Phục vụ thống kê và đánh giá độ chính xác của AI.
    - Hạn chế tính toán lại nếu dữ liệu không thay đổi.

    Quan hệ:

        Project 1 --- N Recommendation N --- 1 Expert
    """

    __tablename__ = "recommendations"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "expert_id",
            name="uq_recommendations_project_expert",
        ),
    )

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
    # FOREIGN KEYS
    # ======================================================

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    expert_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "experts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ======================================================
    # SCORE
    # ======================================================

    match_score = Column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        index=True,
    )

    skill_score = Column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    rating_score = Column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    experience_score = Column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    price_score = Column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    # ======================================================
    # EXPLANATION
    # ======================================================

    matched_skills = Column(
        JSONB,
        nullable=False,
        default=list,
    )

    missing_skills = Column(
        JSONB,
        nullable=False,
        default=list,
    )

    reason = Column(
        Text,
        nullable=True,
    )

    recommendation_level = Column(
        String(30),
        nullable=False,
        default="MEDIUM",
        index=True,
    )

    algorithm_version = Column(
        String(50),
        nullable=False,
        default="v1.0",
    )

    # ======================================================
    # USER FEEDBACK
    # Dùng để đánh giá hiệu quả recommendation.
    # ======================================================

    was_viewed = Column(
        String(10),
        nullable=False,
        default="NO",
    )

    was_selected = Column(
        String(10),
        nullable=False,
        default="NO",
        index=True,
    )

    feedback = Column(
        Text,
        nullable=True,
    )

    # ======================================================
    # TIME
    # ======================================================

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # ======================================================
    # RELATIONSHIPS
    # ======================================================

    project = relationship(
        "Project",
        back_populates="recommendations",
    )

    expert = relationship(
        "Expert",
        back_populates="recommendations",
    )

    def __repr__(self) -> str:
        return (
            f"<Recommendation("
            f"id={self.id}, "
            f"project_id={self.project_id}, "
            f"expert_id={self.expert_id}, "
            f"match_score={self.match_score}, "
            f"level='{self.recommendation_level}'"
            f")>"
        )