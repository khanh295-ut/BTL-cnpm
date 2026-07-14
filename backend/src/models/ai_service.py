from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class AIService(Base):
    """
    Dịch vụ AI do Expert đăng trên Marketplace.

    Ví dụ:

    - Xây dựng chatbot AI
    - Phân tích dữ liệu doanh nghiệp
    - Tích hợp LLM vào hệ thống
    - Xây dựng hệ thống Computer Vision
    - Tự động hóa quy trình bằng AI
    """

    __tablename__ = "ai_services"

    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name="ck_ai_services_price_non_negative",
        ),
        CheckConstraint(
            "delivery_days > 0",
            name="ck_ai_services_delivery_days_positive",
        ),
        CheckConstraint(
            "revision_count >= 0",
            name="ck_ai_services_revision_count_non_negative",
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

    expert_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "experts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "categories.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # ======================================================
    # BASIC INFORMATION
    # ======================================================

    title = Column(
        String(255),
        nullable=False,
        index=True,
    )

    slug = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    short_description = Column(
        String(500),
        nullable=True,
    )

    description = Column(
        Text,
        nullable=False,
    )

    # ======================================================
    # PRICE & DELIVERY
    # ======================================================

    price = Column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
        index=True,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="VND",
    )

    delivery_days = Column(
        Integer,
        nullable=False,
        default=7,
    )

    revision_count = Column(
        Integer,
        nullable=False,
        default=1,
    )

    # ======================================================
    # MARKETPLACE CONTENT
    # ======================================================

    skills = Column(
        JSONB,
        nullable=False,
        default=list,
    )

    deliverables = Column(
        JSONB,
        nullable=False,
        default=list,
    )

    requirements = Column(
        JSONB,
        nullable=False,
        default=list,
    )

    features = Column(
        JSONB,
        nullable=False,
        default=list,
    )

    image_url = Column(
        String(500),
        nullable=True,
    )

    demo_url = Column(
        String(500),
        nullable=True,
    )

    portfolio_url = Column(
        String(500),
        nullable=True,
    )

    # ======================================================
    # STATUS
    # ======================================================

    status = Column(
        String(30),
        nullable=False,
        default="DRAFT",
        index=True,
    )

    rejection_reason = Column(
        Text,
        nullable=True,
    )

    is_featured = Column(
        String(10),
        nullable=False,
        default="NO",
        index=True,
    )

    # ======================================================
    # STATISTICS
    # ======================================================

    view_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    order_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    # ======================================================
    # TIME
    # ======================================================

    published_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

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

    expert = relationship(
        "Expert",
        back_populates="ai_services",
    )

    category = relationship(
        "Category",
        back_populates="ai_services",
    )
    
    orders = relationship(
    "ServiceOrder",
    back_populates="service",
    lazy="selectin",
    order_by="ServiceOrder.created_at.desc()",
)

    def __repr__(self) -> str:
        return (
            f"<AIService("
            f"id={self.id}, "
            f"expert_id={self.expert_id}, "
            f"title='{self.title}', "
            f"price={self.price}, "
            f"status='{self.status}'"
            f")>"
        )