# AuthService đã hợp nhất

from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from backend.src.config.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from backend.src.infrastructure.repositories import SQLAlchemyAuthRepository
from backend.src.models.auth import Role, User
from backend.src.models.token_blacklist import RevokedToken
from backend.src.schemas.auth import LoginRequest, UserCreate
from jose import JWTError, jwt

logger = logging.getLogger("AITasker.AuthService")


class AuthService:
    DEFAULT_ROLE = "ENTERPRISE"
    ALLOWED_REGISTER_ROLES = {"ENTERPRISE", "EXPERT"}
    RESET_TOKEN_EXPIRE_MINUTES = 15

    @staticmethod
    def get_password_hash(password: str) -> str:
        return hash_password(password)

    @staticmethod
    def verify_user_password(password: str, hashed: str) -> bool:
        return verify_password(password, hashed)

    def register(self, db: Session, data: UserCreate):
        if db.query(User).filter(User.email == data.email.lower().strip()).first():
            raise ValueError("Email này đã được đăng ký.")

        if db.query(User).filter(User.username == data.username.strip()).first():
            raise ValueError("Tên đăng nhập đã tồn tại.")

        role_name = getattr(data, "role", None) or self.DEFAULT_ROLE

        role = db.query(Role).filter(Role.name == role_name.upper()).first()
        if role is None:
            raise ValueError("Role không tồn tại.")

        user = User(
            username=data.username.strip(),
            email=data.email.lower().strip(),
            full_name=getattr(data, "full_name", ""),
            bio=getattr(data, "bio", ""),
            password_hash=self.get_password_hash(data.password),
            is_active=True,
        )

        user.roles.append(role)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def login(self, db: Session, data: LoginRequest) -> dict[str, Any] | None:
        login = getattr(data, "login", None) or getattr(data, "email", "")

        user = (
            db.query(User)
            .options(selectinload(User.roles))
            .filter(
                or_(
                    User.email == login.lower().strip(),
                    User.username == login.strip(),
                )
            )
            .first()
        )

        if user is None:
            return None

        if not self.verify_user_password(data.password, user.password_hash):
            return None

        token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "roles": [r.name for r in user.roles],
                "type": "access",
            },
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": getattr(user, "full_name", None),
                "bio": getattr(user, "bio", None),
                "roles": [r.name for r in user.roles],
                "is_active": getattr(user, "is_active", True),
            },
        }

    def forgot_password(self, db: Session, email: str):
        repo = SQLAlchemyAuthRepository(db)
        user = db.query(User).filter(User.email == email.lower().strip()).first()
        if not user:
            return None
        token = secrets.token_urlsafe(32)
        repo.create_reset_token(user, token, expires_in_minutes=15)
        db.commit()
        return token

    def reset_password(self, db: Session, token: str, new_password: str):
        repo = SQLAlchemyAuthRepository(db)
        item = repo.get_reset_token(token)
        if item is None or not item.is_valid():
            return False
        item.user.password_hash = self.get_password_hash(new_password)
        repo.delete_reset_token(item)
        db.commit()
        return True

    def get_user_from_token(self, db: Session, token: str):
        try:
            payload = decode_access_token(token)
            return db.query(User).filter(User.id == payload["sub"]).first()
        except Exception:
            return None

    def logout(self, db: Session, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            return False

        revoked = RevokedToken(
            token=token,
            expires_at=datetime.utcfromtimestamp(payload["exp"]),
        )
        db.add(revoked)
        db.commit()
        return True


auth_service = AuthService()