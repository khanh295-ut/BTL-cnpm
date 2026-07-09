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
from backend.src.services.jwt_service import get_current_user, oauth2_scheme
from backend.src.models.auth import User

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


# =====================================================
# LOGOUT
# =====================================================
@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revoke the current access token so it cannot be used again."""

    success = service.logout(db, token)

    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to logout")

    return {"message": "Logged out successfully."}