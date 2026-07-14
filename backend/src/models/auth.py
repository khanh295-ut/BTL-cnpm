from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base
from backend.src.models.association import (
    role_permissions,
    user_roles,
)


def utc_now() -> datetime:
    """
    Trả về thời gian UTC có timezone.

    Sử dụng thay cho datetime.utcnow() để tránh tạo datetime
    không có thông tin múi giờ.
    """
    return datetime.now(timezone.utc)


# ==========================================================
# PASSWORD RESET TOKEN
# ==========================================================

class PasswordResetToken(Base):
    """
    Token dùng để đặt lại mật khẩu người dùng.
    """

    __tablename__ = "password_reset_tokens"
    __table_args__ = {
        "extend_existing": True,
    }

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

    token = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    user = relationship(
        "User",
        back_populates="tokens",
    )

    def __repr__(self) -> str:
        return (
            "<PasswordResetToken("
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"expires_at={self.expires_at}"
            ")>"
        )


# ==========================================================
# PERMISSION
# ==========================================================

class Permission(Base):
    """
    Quyền truy cập trong hệ thống.
    """

    __tablename__ = "permissions"
    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    description = Column(
        String(255),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    roles = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            "<Permission("
            f"id={self.id}, "
            f"name='{self.name}'"
            ")>"
        )


# ==========================================================
# ROLE
# ==========================================================

class Role(Base):
    """
    Vai trò người dùng.

    Các vai trò chính:
    - ADMIN
    - ENTERPRISE
    - EXPERT
    """

    __tablename__ = "roles"
    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    name = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    description = Column(
        String(255),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )

    users = relationship(
        "User",
        secondary=user_roles,
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            "<Role("
            f"id={self.id}, "
            f"name='{self.name}'"
            ")>"
        )


# ==========================================================
# USER
# ==========================================================

class User(Base):
    """
    Tài khoản người dùng chung của hệ thống.

    Hồ sơ nghiệp vụ chi tiết được lưu tại:
    - Enterprise
    - Expert
    """

    __tablename__ = "users"
    __table_args__ = {
        "extend_existing": True,
    }

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    email = Column(
        String(120),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password = Column(
        String(255),
        nullable=False,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    # ======================================================
    # AUTHORIZATION RELATIONSHIPS
    # ======================================================

    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )

    tokens = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # ======================================================
    # PROFILE RELATIONSHIPS
    # ======================================================

    enterprise = relationship(
        "Enterprise",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    expert = relationship(
        "Expert",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # ======================================================
    # NOTIFICATION RELATIONSHIP
    # ======================================================

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="Notification.created_at.desc()",
    )

    # ======================================================
    # WALLET RELATIONSHIPS
    # ======================================================

    wallet = relationship(
        "Wallet",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    wallet_transactions = relationship(
        "WalletTransaction",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="WalletTransaction.created_at.desc()",
    )

    withdrawals = relationship(
        "Withdrawal",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="Withdrawal.created_at.desc()",
    )

    # ======================================================
    # DISPUTE RELATIONSHIPS
    # ======================================================

    opened_disputes = relationship(
        "Dispute",
        foreign_keys="Dispute.opened_by_user_id",
        back_populates="opened_by",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    assigned_disputes = relationship(
        "Dispute",
        foreign_keys="Dispute.assigned_admin_id",
        back_populates="assigned_admin",
        lazy="selectin",
    )

    resolved_disputes = relationship(
        "Dispute",
        foreign_keys="Dispute.resolved_by_user_id",
        back_populates="resolved_by",
        lazy="selectin",
    )

    # ======================================================
    # SERVICE ORDER RELATIONSHIPS
    # ======================================================

    service_orders = relationship(
        "ServiceOrder",
        back_populates="customer",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # ======================================================
    # RECOMMENDATION RELATIONSHIPS
    # ======================================================

    recommendations = relationship(
        "Recommendation",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            "<User("
            f"id={self.id}, "
            f"username='{self.username}', "
            f"email='{self.email}', "
            f"is_active={self.is_active}"
            ")>"
        )