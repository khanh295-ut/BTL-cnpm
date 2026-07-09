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
    Generate reset password token for demo environments.
    """

    token = service.forgot_password(
        db,
        str(data.email),
    )

    return {
        "message": "If the email exists in the system, a reset link has been generated.",
        "reset_token": token,
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
    Reset password with token validation.
    """

    success = service.reset_password(
        db,
        data.token,
        data.new_password,
        data.confirm_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token, or passwords do not match.",
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