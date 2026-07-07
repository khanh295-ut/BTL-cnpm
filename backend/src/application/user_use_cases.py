from __future__ import annotations

from backend.src.domain.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from backend.src.infrastructure.repositories import SQLAlchemyAuthRepository


def serialize_profile(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "roles": [role.name for role in user.roles],
        "full_name": user.full_name,
        "bio": user.bio,
    }


def get_profile(user):
    return serialize_profile(user)


def update_profile(db, current_user, full_name=None, email=None, bio=None):
    repo = SQLAlchemyAuthRepository(db)
    if email and email != current_user.email:
        existing_user = repo.get_user_by_email(email)
        if existing_user and existing_user.id != current_user.id:
            raise ConflictError("Email đã tồn tại.")
        current_user.email = email
    if full_name is not None:
        current_user.full_name = full_name.strip() if full_name else None
    if bio is not None:
        current_user.bio = bio.strip() if bio else None
    repo.commit()
    return serialize_profile(current_user)


def change_password(db, current_user, current_password: str, new_password: str):
    if not current_user.check_password(current_password):
        raise ValidationError("Sai mật khẩu hiện tại.")
    current_user.set_password(new_password)
    SQLAlchemyAuthRepository(db).commit()


def require_admin(current_user):
    if not current_user.is_admin():
        raise ForbiddenError("Không đủ quyền truy cập.")

