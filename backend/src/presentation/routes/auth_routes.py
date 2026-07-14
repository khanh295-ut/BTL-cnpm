from __future__ import annotations

import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    UserCreate,
)
from backend.src.services.auth_service import auth_service


logger = logging.getLogger(
    "AITasker.AuthRoutes"
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ==========================================================
# REGISTER
# ==========================================================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản",
)
def register(
    data: UserCreate,
    db: Session = Depends(get_db),
) -> dict:
    """
    Đăng ký tài khoản mới.

    Vai trò cho phép:
    - ENTERPRISE
    - EXPERT
    """

    try:
        user = auth_service.register(
            db=db,
            data=data,
        )

        return {
            "success": True,
            "message": "Đăng ký tài khoản thành công.",
            "data": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "roles": auth_service.get_role_names(
                    user
                ),
            },
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()

        logger.exception(
            "Lỗi cơ sở dữ liệu khi đăng ký tài khoản."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể đăng ký tài khoản do lỗi cơ sở dữ liệu.",
        ) from exc

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Lỗi không xác định khi đăng ký tài khoản."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể đăng ký tài khoản.",
        ) from exc


# ==========================================================
# LOGIN
# ==========================================================

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Đăng nhập hệ thống",
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    Xác thực người dùng bằng email và mật khẩu.

    Nếu thành công, hệ thống trả về JWT Access Token.
    """

    try:
        result = auth_service.login(
            db=db,
            data=data,
        )

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email hoặc mật khẩu không chính xác.",
                headers={
                    "WWW-Authenticate": "Bearer",
                },
            )

        return {
            "success": True,
            "message": "Đăng nhập thành công.",
            "data": result,
        }

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except SQLAlchemyError as exc:
        logger.exception(
            "Lỗi cơ sở dữ liệu khi đăng nhập."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể đăng nhập do lỗi cơ sở dữ liệu.",
        ) from exc

    except Exception as exc:
        logger.exception(
            "Lỗi không xác định khi đăng nhập."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể đăng nhập.",
        ) from exc


# ==========================================================
# FORGOT PASSWORD
# ==========================================================

@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Yêu cầu đặt lại mật khẩu",
)
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    Tạo JWT Password Reset Token.

    Trong môi trường production, token nên được gửi qua email
    thay vì trả trực tiếp cho người dùng.
    """

    try:
        reset_token = auth_service.forgot_password(
            db=db,
            email=data.email,
        )

        # Không tiết lộ email có tồn tại hay không.
        if reset_token is None:
            return {
                "success": True,
                "message": (
                    "Nếu email tồn tại trong hệ thống, "
                    "hướng dẫn đặt lại mật khẩu sẽ được gửi."
                ),
            }

        return {
            "success": True,
            "message": "Token đặt lại mật khẩu đã được tạo.",
            "data": {
                # Chỉ nên trả token trực tiếp khi đang phát triển.
                "reset_token": reset_token,
                "token_type": "bearer",
                "expires_in": (
                    auth_service.RESET_TOKEN_EXPIRE_MINUTES
                    * 60
                ),
            },
        }

    except SQLAlchemyError as exc:
        logger.exception(
            "Lỗi cơ sở dữ liệu khi tạo reset token."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể xử lý yêu cầu đặt lại mật khẩu "
                "do lỗi cơ sở dữ liệu."
            ),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Lỗi không xác định khi tạo reset token."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể xử lý yêu cầu đặt lại mật khẩu.",
        ) from exc


# ==========================================================
# RESET PASSWORD
# ==========================================================

@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Đặt lại mật khẩu",
)
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    Đặt lại mật khẩu bằng Password Reset Token.
    """

    try:
        success = auth_service.reset_password(
            db=db,
            token=data.token,
            new_password=data.new_password,
        )

        if success is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Token đặt lại mật khẩu không hợp lệ "
                    "hoặc đã hết hạn."
                ),
            )

        return {
            "success": True,
            "message": "Đặt lại mật khẩu thành công.",
        }

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()

        logger.exception(
            "Lỗi cơ sở dữ liệu khi đặt lại mật khẩu."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể đặt lại mật khẩu "
                "do lỗi cơ sở dữ liệu."
            ),
        ) from exc

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Lỗi không xác định khi đặt lại mật khẩu."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể đặt lại mật khẩu.",
        ) from exc


# ==========================================================
# HEALTH CHECK
# ==========================================================

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Kiểm tra Authentication API",
)
def auth_health_check() -> dict:
    """
    Kiểm tra nhanh trạng thái hoạt động của Authentication API.
    """

    return {
        "success": True,
        "message": "Authentication API is running.",
    }