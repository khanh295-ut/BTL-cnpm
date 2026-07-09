from datetime import datetime, timedelta

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from backend.src.config.database import Base
from backend.src.models.association import (
    user_roles,
    role_permissions,
)
from backend.src.utils.security import hash_password, verify_password


# =====================================================
# PASSWORD RESET TOKEN
# =====================================================
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = {"extend_existing": True}

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    token = Column(
        String(255),
        unique=True,
        nullable=False,
    )

    expires_at = Column(
        DateTime,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=True,
    )

    # Quan hệ với User
    user = relationship(
        "User",
        back_populates="tokens",
    )

    @classmethod
    def create_for_user(cls, user, token: str, expires_in_minutes: int = 15):
        now = datetime.utcnow()
        return cls(
            user_id=user.id,
            token=token,
            expires_at=now + timedelta(minutes=expires_in_minutes),
            created_at=now,
        )

    def is_valid(self) -> bool:
        return self.expires_at > datetime.utcnow()


# =====================================================
# PERMISSION
# =====================================================
class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = {"extend_existing": True}

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    name = Column(
        String(100),
        unique=True,
        nullable=False,
    )

    description = Column(
        String(255),
        nullable=True,
    )

    roles = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
        lazy="selectin",
    )


# =====================================================
# ROLE
# =====================================================
class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"extend_existing": True}

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    name = Column(
        String(50),
        unique=True,
        nullable=False,
    )

    description = Column(
        String(255),
        nullable=True,
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


# =====================================================
# USER
# =====================================================
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
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

    password_hash = Column(
        String(255),
        nullable=False,
    )

    full_name = Column(
        String(255),
        nullable=True,
        default="",
        server_default="",
    )

    bio = Column(
        String(500),
        nullable=True,
    )

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
        lazy="selectin",
    )

    def set_password(self, password: str):
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

    def has_role(self, role_name: str) -> bool:
        return any(role.name.lower() == role_name.lower() for role in self.roles)

    def is_admin(self) -> bool:
        return self.has_role("admin")

    @property
    def role(self) -> str | None:
        return self.roles[0].name if self.roles else None

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
