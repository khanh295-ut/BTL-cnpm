from datetime import datetime, timedelta

import bcrypt
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from backend.src.config.database import Base

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles", lazy="selectin")
    users = relationship("User", secondary=user_roles, back_populates="roles", lazy="selectin")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(120), nullable=True)
    bio = Column(String(500), nullable=True)

    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="selectin")

    @property
    def role(self):
        return self.roles[0].name if self.roles else "User"

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))

    def is_admin(self):
        return any(role.name == "Admin" for role in self.roles)

    def has_permission(self, permission_name):
        if self.is_admin():
            return True
        return any(
            permission.name == permission_name
            for role in self.roles
            for permission in role.permissions
        )


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(128), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", backref="reset_tokens", lazy="selectin")

    def is_valid(self):
        return datetime.utcnow() < self.expires_at

    @classmethod
    def create_for_user(cls, user, token, expires_in_minutes=30):
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        return cls(user_id=user.id, token=token, expires_at=expires_at)
