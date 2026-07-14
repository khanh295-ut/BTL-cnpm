from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


class Notification(Base):
    """
    Thông báo dành cho người dùng trong hệ thống AITasker.

    Ví dụ:
    - Proposal được chấp nhận
    - Contract được tạo
    - Deliverable được gửi
    - Milestone được phê duyệt
    - Payment được giải ngân
    """

    __tablename__ = "notifications"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    message = Column(
        Text,
        nullable=False,
    )

    notification_type = Column(
        String(50),
        nullable=False,
        default="SYSTEM",
        index=True,
    )

    reference_type = Column(
        String(50),
        nullable=True,
        index=True,
    )

    reference_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    is_read = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    read_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    user = relationship(
        "User",
        back_populates="notifications",
    )

    def __repr__(self) -> str:
        return (
            f"<Notification("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"type='{self.notification_type}', "
            f"is_read={self.is_read}"
            f")>"
        )