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


# ==========================================================
# TIME HELPER
# ==========================================================

def utc_now() -> datetime:
    """
    Trả về thời gian UTC có thông tin múi giờ.
    """

    return datetime.now(timezone.utc)


# ==========================================================
# PASSWORD RESET TOKEN
# ==========================================================

class PasswordResetToken(Base):
    """
    Token dùng để đặt lại mật khẩu.

    Mỗi token thuộc về đúng một User.
    Khi User bị xóa, các token liên quan cũng bị xóa.
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
        nullable=False,
        unique=True,
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
        foreign_keys=[user_id],
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
    Quyền thực hiện một hành động trong hệ thống.

    Ví dụ:
    - users.read
    - users.create
    - projects.update
    - payments.manage
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
        nullable=False,
        unique=True,
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
        nullable=False,
        unique=True,
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
    Tài khoản chung của hệ thống AITasker.

    Hồ sơ nghiệp vụ chi tiết được lưu tại:

    - Enterprise: nếu tài khoản thuộc doanh nghiệp.
    - Expert: nếu tài khoản thuộc chuyên gia AI.

    Quan hệ ví:

        User
          └── Wallet
                ├── WalletTransaction
                └── Withdrawal

    Quan hệ ServiceOrder:

        User
          ├── Enterprise
          │     └── ServiceOrder
          │
          └── Expert
                └── ServiceOrder

    Vì vậy User không khai báo trực tiếp:

    - wallet_transactions
    - withdrawals
    - service_orders
    """

    __tablename__ = "users"

    __table_args__ = {
        "extend_existing": True,
    }

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
    # ACCOUNT INFORMATION
    # ======================================================

    username = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    email = Column(
        String(120),
        nullable=False,
        unique=True,
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
        foreign_keys="PasswordResetToken.user_id",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # ======================================================
    # ENTERPRISE PROFILE
    #
    # Enterprise phải có:
    #
    # user_id = Column(
    #     UUID(as_uuid=True),
    #     ForeignKey("users.id", ondelete="CASCADE"),
    #     unique=True,
    # )
    # ======================================================

    enterprise = relationship(
        "Enterprise",
        back_populates="user",
        foreign_keys="Enterprise.user_id",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # ======================================================
    # EXPERT PROFILE
    #
    # Expert phải có:
    #
    # user_id = Column(
    #     UUID(as_uuid=True),
    #     ForeignKey("users.id", ondelete="CASCADE"),
    #     unique=True,
    # )
    # ======================================================

    expert = relationship(
        "Expert",
        back_populates="user",
        foreign_keys="Expert.user_id",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # ======================================================
    # WALLET
    #
    # Giao dịch được truy cập bằng:
    #
    # user.wallet.transactions
    #
    # Yêu cầu rút tiền được truy cập bằng:
    #
    # user.wallet.withdrawals
    # ======================================================

    wallet = relationship(
        "Wallet",
        back_populates="user",
        foreign_keys="Wallet.user_id",
        uselist=False,
        single_parent=True,
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    # ======================================================
    # NOTIFICATIONS
    # ======================================================

    notifications = relationship(
        "Notification",
        back_populates="user",
        foreign_keys="Notification.user_id",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="Notification.created_at.desc()",
    )

    # ======================================================
    # WITHDRAWALS
    # Withdrawal liên kết trực tiếp với User và Wallet.
    # ======================================================

    withdrawals = relationship(
        "Withdrawal",
        back_populates="user",
        foreign_keys="Withdrawal.user_id",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="Withdrawal.created_at.desc()",
    )

    # ======================================================
    # DISPUTES
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
    # REPRESENTATION
    # ======================================================

    def __repr__(self) -> str:
        return (
            "<User("
            f"id={self.id}, "
            f"username='{self.username}', "
            f"email='{self.email}', "
            f"is_active={self.is_active}"
            ")>"
        )