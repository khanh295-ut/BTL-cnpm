# backend/src/presentation/routes/user_routes.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.models.auth import User
from backend.src.schemas.user import (
    ChangePasswordRequest,
    ProfileUpdateRequest,
    UserResponse,
)
from backend.src.services.jwt_service import get_current_user
from backend.src.services.user_service import UserService


# ==========================================================
# ROUTER
# Prefix /users được thêm trong all_routes.py.
# Prefix /api được thêm trong app.py.
# ==========================================================

router = APIRouter(
    tags=["Users"],
)

service = UserService()


# ==========================================================
# CURRENT PROFILE
# ==========================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


# ==========================================================
# UPDATE PROFILE
# ==========================================================

@router.put(
    "/me",
    response_model=UserResponse,
)
def update_profile(
    data: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = service.update_profile(
        db=db,
        user_id=current_user.id,
        full_name=data.full_name,
        email=data.email,
        bio=data.bio,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user


# ==========================================================
# CHANGE PASSWORD
# ==========================================================

@router.put("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.check_password(data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    service.change_password(
        db=db,
        user=current_user,
        new_password=data.new_password,
    )

    return {
        "message": "Password changed successfully.",
    }


# ==========================================================
# USER DETAIL
# Đặt sau /me và /change-password để tránh route động bắt nhầm.
# ==========================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    user = service.get_profile(
        db=db,
        user_id=user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user