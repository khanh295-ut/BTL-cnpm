from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.models.auth import User
from backend.src.schemas.user import (
    ProfileUpdateRequest,
    ChangePasswordRequest,
    UserResponse,
)
from backend.src.services.jwt_service import get_current_user
from backend.src.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

service = UserService()


# =====================================================
# CURRENT PROFILE
# =====================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


# =====================================================
# UPDATE PROFILE
# =====================================================

@router.put(
    "/me",
    response_model=UserResponse
)
def update_profile(
    data: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return service.update_profile(
        db=db,
        user_id=current_user.id,
        full_name=data.full_name,
        email=data.email,
        bio=data.bio,
    )


# =====================================================
# CHANGE PASSWORD
# =====================================================

@router.put("/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if not current_user.check_password(data.current_password):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect."
        )

    service.change_password(
        db=db,
        user=current_user,
        new_password=data.new_password,
    )

    return {
        "message": "Password changed successfully."
    }


# =====================================================
# USER DETAIL
# =====================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
):

    user = service.get_profile(
        db=db,
        user_id=user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return user