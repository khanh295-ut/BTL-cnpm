from __future__ import annotations

import logging
from typing import Any

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


# ==========================================================
# LOGGING
# ==========================================================

logger = logging.getLogger("AITasker.AuthRoutes")


# ==========================================================
# ROUTER
#
# Không thêm prefix="/auth" tại đây.
#
# Prefix được ghép như sau:
#
# app.py:
#     /api
#
# all_routes.py:
#     /auth
#
# auth_routes.py:
#     /login
#
# Endpoint cuối:
#     /api/auth/login
# ==========================================================

router = APIRouter(
    tags=["Authentication"],
)


# ==========================================================
# RESPONSE HELPERS
# ==========================================================

def success_response(
    message: str,
    data: Any | None = None,
) -> dict[str, Any]:
    """
    Chuẩn hóa response thành công.
    """

    response: dict[str, Any] = {
        "success": True,
        "message": message,
    }

    if data is not None:
        response["data"] = data

    return response


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
) -> dict[str, Any]:
    """
    Đăng ký tài khoản mới.

    Vai trò được hỗ trợ:
    - ENTERPRISE
    - EXPERT
    """

    try:
        user = auth_service.register(
            db=db,
            data=data,
        )

        return success_response(
            message="Đăng ký tài khoản thành công.",
            data={
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "roles": auth_service.get_role_names(user),
            },
        )

    except ValueError as exc:
        db.rollback()

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
            detail=(
                "Không thể đăng ký tài khoản "
                "do lỗi cơ sở dữ liệu."
            ),
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
) -> dict[str, Any]:
    """
    Xác thực người dùng.

    Nếu thành công, hệ thống trả về:
    - access token
    - token type
    - thông tin người dùng
    """

    try:
        result = auth_service.login(
            db=db,
            data=data,
        )

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "Tài khoản hoặc mật khẩu "
                    "không chính xác."
                ),
                headers={
                    "WWW-Authenticate": "Bearer",
                },
            )

        return success_response(
            message="Đăng nhập thành công.",
            data=result,
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()

        logger.exception(
            "Lỗi cơ sở dữ liệu khi đăng nhập."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể đăng nhập "
                "do lỗi cơ sở dữ liệu."
            ),
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
) -> dict[str, Any]:
    """
    Tạo token đặt lại mật khẩu.

    Không tiết lộ email có tồn tại trong hệ thống hay không.
    """

    try:
        reset_token = auth_service.forgot_password(
            db=db,
            email=data.email,
        )

        if reset_token is None:
            return success_response(
                message=(
                    "Nếu email tồn tại trong hệ thống, "
                    "hướng dẫn đặt lại mật khẩu sẽ được gửi."
                )
            )

        return success_response(
            message=(
                "Token đặt lại mật khẩu "
                "đã được tạo."
            ),
            data={
                "reset_token": reset_token,
                "token_type": "bearer",
                "expires_in": (
                    auth_service.RESET_TOKEN_EXPIRE_MINUTES
                    * 60
                ),
            },
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()

        logger.exception(
            "Lỗi cơ sở dữ liệu khi tạo reset token."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể xử lý yêu cầu đặt lại "
                "mật khẩu do lỗi cơ sở dữ liệu."
            ),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Lỗi không xác định khi tạo reset token."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể xử lý yêu cầu "
                "đặt lại mật khẩu."
            ),
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
) -> dict[str, Any]:
    """
    Đặt lại mật khẩu bằng reset token.
    """

    try:
        result = auth_service.reset_password(
            db=db,
            token=data.token,
            new_password=data.new_password,
        )

        if result is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Token đặt lại mật khẩu "
                    "không hợp lệ hoặc đã hết hạn."
                ),
            )

        return success_response(
            message="Đặt lại mật khẩu thành công."
        )

    except HTTPException:
        raise

    except ValueError as exc:
        db.rollback()

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
def auth_health_check() -> dict[str, Any]:
    """
    Kiểm tra trạng thái Authentication API.
    """

    return success_response(
        message="Authentication API is running.",
        data={
            "endpoints": {
                "register": "/api/auth/register",
                "login": "/api/auth/login",
                "forgot_password": (
                    "/api/auth/forgot-password"
                ),
                "reset_password": (
                    "/api/auth/reset-password"
                ),
            },
        },
    )