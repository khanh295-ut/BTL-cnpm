from __future__ import annotations

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from backend.src.domain.exceptions import UnauthorizedError
from backend.src.config.database import get_db
from backend.src.infrastructure.repositories import SQLAlchemyAuthRepository


def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if user_id is None:
        raise UnauthorizedError("Chưa đăng nhập.")
    user = SQLAlchemyAuthRepository(db).get_user_by_id(int(user_id))
    if user is None:
        raise UnauthorizedError("Chưa đăng nhập.")
    return user


def require_admin(current_user=Depends(get_current_user)):
    if not current_user.is_admin():
        raise UnauthorizedError("Không đủ quyền truy cập.")
    return current_user

