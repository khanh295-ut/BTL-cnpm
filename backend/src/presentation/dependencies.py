# backend/src/presentation/dependencies.py

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.domain.exceptions import UnauthorizedError
from backend.src.infrastructure.repositories import SQLAlchemyAuthRepository
from backend.src.models.auth import User


# ==========================================================
# GET CURRENT USER FROM SESSION
# ==========================================================

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """
    Lấy người dùng hiện tại từ SessionMiddleware.

    Session phải chứa:
        request.session["user_id"]
    """

    raw_user_id = request.session.get("user_id")

    if raw_user_id is None:
        raise UnauthorizedError("Chưa đăng nhập.")

    try:
        user_id = UUID(str(raw_user_id))
    except (TypeError, ValueError):
        request.session.clear()
        raise UnauthorizedError("Phiên đăng nhập không hợp lệ.")

    repository = SQLAlchemyAuthRepository(db)

    user = repository.get_user_by_id(user_id)

    if user is None:
        request.session.clear()
        raise UnauthorizedError("Người dùng không tồn tại hoặc phiên đã hết hạn.")

    return user


# ==========================================================
# REQUIRE ADMIN
# ==========================================================

def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Chỉ cho phép tài khoản có quyền quản trị truy cập.
    """

    is_admin_method = getattr(current_user, "is_admin", None)

    if callable(is_admin_method):
        is_admin = bool(is_admin_method())
    else:
        is_admin = bool(getattr(current_user, "is_admin", False))

    if not is_admin:
        raise UnauthorizedError("Không đủ quyền truy cập.")

    return current_user