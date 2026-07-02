from datetime import datetime, timedelta
import uuid
import bcrypt

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.src.config.database import Base


# =========================
# ROLE
# =========================
class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    users = relationship("User", secondary="user_roles", back_populates="roles")


# =========================
# PERMISSION
# =========================
class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")


# =========================
# USER
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    full_name = Column(String(255))
    bio = Column(String(500))

    roles = relationship("Role", secondary="user_roles", back_populates="users")
    reset_tokens = relationship("PasswordResetToken", back_populates="user")

    def set_password(self, password: str):
        self.password_hash = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode(),
            self.password_hash.encode()
        )


# =========================
# PASSWORD RESET TOKEN (ONLY ONE VERSION)
# =========================
class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String(128), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="reset_tokens")

    @classmethod
    def create_for_user(cls, user, token: str, minutes: int = 30):
        return cls(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(minutes=minutes)
        )