from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.auth import (
    UserCreate,
    LoginRequest,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from backend.src.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

service = AuthService()


# =====================================================
# REGISTER
# =====================================================
@router.post("/register")
def register(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user
    """

    try:
        user = service.register(db, data)

        return {
            "message": "Register successfully.",
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# =====================================================
# LOGIN
# =====================================================
@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Login user
    """

    result = service.login(db, data)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return result


# =====================================================
# FORGOT PASSWORD
# =====================================================
@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Generate reset password token
    """

    token = service.forgot_password(
        db,
        data.email,
    )

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return {
        "message": "Reset token generated successfully.",
        "token": token,
    }


# =====================================================
# RESET PASSWORD
# =====================================================
@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """
    Reset password
    """

    success = service.reset_password(
        db,
        data.token,
        data.new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token.",
        )

    return {
        "message": "Password reset successfully."
    }