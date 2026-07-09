from datetime import datetime
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    String,
)
from sqlalchemy.dialects.postgresql import UUID

# Import chuẩn từ backend.src.config.database
from backend.src.config.database import Base


class UserRegisterRequest(Base):
    """
    Model lưu trữ các yêu cầu đăng ký tài khoản từ người dùng (Expert / Enterprise)
    chờ Ban quản trị (Admin) phê duyệt.
    """
    __tablename__ = "user_register_requests"
    __table_args__ = {"extend_existing": True}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    email = Column(
        String(120),
        unique=True,
        nullable=False,
        index=True,
    )

    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password = Column(
        String(255),
        nullable=False,
    )

    full_name = Column(
        String(100),
        nullable=False,
    )

    # Vai trò mong muốn đăng ký (Ví dụ: "expert" hoặc "enterprise")
    requested_role = Column(
        String(50),
        nullable=False,
    )

    # Trạng thái phê duyệt
    is_approved = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Trạng thái từ chối
    is_rejected = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    processed_at = Column(
        DateTime,
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<UserRegisterRequest(id={self.id}, email='{self.email}', role='{self.requested_role}', approved={self.is_approved}, rejected={self.is_rejected})>"
