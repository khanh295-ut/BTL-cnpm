from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
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
from backend.src.infrastructure.repositories import (
    SQLAlchemyAuthRepository,
)
from backend.src.models.auth import Role, User
from backend.src.models.token_blacklist import RevokedToken
from backend.src.schemas.auth import LoginRequest, UserCreate


logger = logging.getLogger("AITasker.AuthService")


class AuthService:
    """
    Xử lý đăng ký, đăng nhập, đặt lại mật khẩu và đăng xuất.
    """

    DEFAULT_ROLE = "ENTERPRISE"

    ALLOWED_REGISTER_ROLES = {
        "ENTERPRISE",
        "EXPERT",
    }

    RESET_TOKEN_EXPIRE_MINUTES = 15

    # ======================================================
    # PASSWORD HELPERS
    # ======================================================

    @staticmethod
    def get_password_hash(
        password: str,
    ) -> str:
        """
        Mã hóa mật khẩu trước khi lưu database.
        """

        return hash_password(password)

    @staticmethod
    def verify_user_password(
        password: str,
        hashed_password: str,
    ) -> bool:
        """
        So sánh mật khẩu nhập vào với mật khẩu đã mã hóa.
        """

        return verify_password(
            password,
            hashed_password,
        )

    # ======================================================
    # ROLE HELPERS
    # ======================================================

    @staticmethod
    def get_role_names(
        user: User,
    ) -> list[str]:
        """
        Trả về danh sách tên role của người dùng.
        """

        return [
            role.name
            for role in user.roles
        ]

    # ======================================================
    # REGISTER
    # ======================================================

    def register(
        self,
        db: Session,
        data: UserCreate,
    ) -> User:
        """
        Đăng ký tài khoản mới.
        """

        normalized_email = (
            data.email
            .lower()
            .strip()
        )

        normalized_username = (
            data.username
            .strip()
        )

        existing_email = (
            db.query(User)
            .filter(
                User.email == normalized_email
            )
            .first()
        )

        if existing_email is not None:
            raise ValueError(
                "Email này đã được đăng ký."
            )

        existing_username = (
            db.query(User)
            .filter(
                User.username == normalized_username
            )
            .first()
        )

        if existing_username is not None:
            raise ValueError(
                "Tên đăng nhập đã tồn tại."
            )

        raw_role = (
            getattr(
                data,
                "role",
                None,
            )
            or self.DEFAULT_ROLE
        )

        role_name = str(
            raw_role
        ).upper().strip()

        if role_name not in self.ALLOWED_REGISTER_ROLES:
            raise ValueError(
                "Role đăng ký không hợp lệ."
            )

        role = (
            db.query(Role)
            .filter(
                Role.name == role_name
            )
            .first()
        )

        if role is None:
            raise ValueError(
                f"Role {role_name} chưa tồn tại."
            )

        user = User(
            username=normalized_username,
            email=normalized_email,
            hashed_password=self.get_password_hash(
                data.password
            ),
            is_active=True,
        )

        user.roles.append(role)

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    # ======================================================
    # LOGIN
    # ======================================================

    def login(
        self,
        db: Session,
        data: LoginRequest,
    ) -> dict[str, Any] | None:
        """
        Đăng nhập bằng username hoặc email.
        """

        login_value = (
            getattr(
                data,
                "login",
                None,
            )
            or getattr(
                data,
                "email",
                "",
            )
        )

        login_value = (
            login_value
            .strip()
        )

        if not login_value:
            return None

        user = (
            db.query(User)
            .options(
                selectinload(User.roles)
            )
            .filter(
                or_(
                    User.email
                    == login_value.lower(),

                    User.username
                    == login_value,
                )
            )
            .first()
        )

        if user is None:
            return None

        if not user.is_active:
            raise ValueError(
                "Tài khoản đã bị vô hiệu hóa."
            )

        if not self.verify_user_password(
            data.password,
            user.hashed_password,
        ):
            return None

        role_names = self.get_role_names(
            user
        )

        access_token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "username": user.username,
                "roles": role_names,
                "type": "access",
            },
            timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            ),
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": (
                ACCESS_TOKEN_EXPIRE_MINUTES
                * 60
            ),
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "roles": role_names,
                "is_active": user.is_active,
            },
        }

    # ======================================================
    # FORGOT PASSWORD
    # ======================================================

    def forgot_password(
        self,
        db: Session,
        email: str,
    ) -> str | None:
        """
        Tạo token đặt lại mật khẩu.
        """

        normalized_email = (
            email
            .lower()
            .strip()
        )

        user = (
            db.query(User)
            .filter(
                User.email == normalized_email
            )
            .first()
        )

        if user is None:
            return None

        repository = SQLAlchemyAuthRepository(
            db
        )

        reset_token = secrets.token_urlsafe(
            32
        )

        repository.create_reset_token(
            user,
            reset_token,
            expires_in_minutes=(
                self.RESET_TOKEN_EXPIRE_MINUTES
            ),
        )

        db.commit()

        return reset_token

    # ======================================================
    # RESET PASSWORD
    # ======================================================

    def reset_password(
        self,
        db: Session,
        token: str,
        new_password: str,
    ) -> bool:
        """
        Đặt lại mật khẩu bằng reset token.
        """

        repository = SQLAlchemyAuthRepository(
            db
        )

        reset_item = (
            repository.get_reset_token(
                token
            )
        )

        if (
            reset_item is None
            or not reset_item.is_valid()
        ):
            return False

        reset_item.user.hashed_password = (
            self.get_password_hash(
                new_password
            )
        )

        repository.delete_reset_token(
            reset_item
        )

        db.commit()

        return True

    # ======================================================
    # GET USER FROM TOKEN
    # ======================================================

    def get_user_from_token(
        self,
        db: Session,
        token: str,
    ) -> User | None:
        """
        Lấy người dùng từ JWT access token.
        """

        try:
            payload = decode_access_token(
                token
            )

            user_id = payload.get("sub")

            if not user_id:
                return None

            return (
                db.query(User)
                .options(
                    selectinload(User.roles)
                )
                .filter(
                    User.id == user_id
                )
                .first()
            )

        except Exception:
            logger.exception(
                "Không thể lấy người dùng từ token."
            )

            return None

    # ======================================================
    # LOGOUT
    # ======================================================

    def logout(
        self,
        db: Session,
        token: str,
    ) -> bool:
        """
        Thu hồi access token bằng blacklist.
        """

        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
            )

        except JWTError:
            return False

        expires_at = datetime.fromtimestamp(
            payload["exp"],
            tz=timezone.utc,
        )

        revoked_token = RevokedToken(
            token=token,
            expires_at=expires_at,
        )

        db.add(revoked_token)
        db.commit()

        return True


auth_service = AuthService()