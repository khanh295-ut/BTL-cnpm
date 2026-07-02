from __future__ import annotations

import secrets

from backend.src.domain.exceptions import ConflictError, NotFoundError, UnauthorizedError, ValidationError
from backend.src.infrastructure.repositories import SQLAlchemyAuthRepository


def serialize_user(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "roles": [role.name for role in user.roles],
        "full_name": user.full_name,
        "bio": user.bio,
    }


def login_user(db, login_input: str, password: str):
    repo = SQLAlchemyAuthRepository(db)
    user = repo.get_user_by_login(login_input)
    if user is None:
        raise NotFoundError("Tài khoản không tồn tại.")
    if not user.check_password(password):
        raise UnauthorizedError("Sai mật khẩu.")
    return user


def register_user(db, username: str, email: str, password: str):
    repo = SQLAlchemyAuthRepository(db)
    if repo.get_user_by_username(username):
        raise ConflictError("Username đã tồn tại.")
    if repo.get_user_by_email(email):
        raise ConflictError("Email đã tồn tại.")

    from backend.src.models import User

    user = User(username=username, email=email)
    user.set_password(password)
    role = repo.ensure_role("User", "Standard user role")
    user.roles.append(role)
    repo.save_user(user)
    repo.commit()
    return user


def forgot_password(db, email: str):
    repo = SQLAlchemyAuthRepository(db)
    user = repo.get_user_by_email(email)
    reset_url = None
    if user is not None:
        token = secrets.token_urlsafe(32)
        repo.create_reset_token(user, token)
        repo.commit()
        reset_url = f"/reset-password/{token}"
    return reset_url


def reset_password(db, token: str, password: str, confirm_password: str):
    if password != confirm_password:
        raise ValidationError("Mật khẩu xác nhận không khớp.")

    repo = SQLAlchemyAuthRepository(db)
    reset_item = repo.get_reset_token(token)
    if reset_item is None or not reset_item.is_valid():
        raise NotFoundError("Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.")

    reset_item.user.set_password(password)
    repo.delete_reset_token(reset_item)
    repo.commit()

