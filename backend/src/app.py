"""
AITasker Backend Application

Công nghệ:
- FastAPI
- SQLAlchemy
- PostgreSQL
- Gemini AI
- React/Vite frontend

Quy ước router:
- app.py chỉ thêm prefix /api đúng một lần.
- presentation/router thêm prefix tài nguyên.
- các file *_routes.py không tự thêm lại /api.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware


# ==========================================================
# PATH CONFIGURATION
# ==========================================================

SRC_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SRC_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

ENV_FILE = PROJECT_ROOT / ".env"


# ==========================================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================================

load_dotenv(
    dotenv_path=ENV_FILE,
    override=False,
)


# ==========================================================
# ENVIRONMENT
# ==========================================================

APP_ENV = os.getenv(
    "APP_ENV",
    "development",
).strip().lower()

IS_DEVELOPMENT = APP_ENV in {
    "development",
    "dev",
    "local",
}

HOST = os.getenv(
    "HOST",
    "127.0.0.1",
)

PORT = int(
    os.getenv(
        "PORT",
        "8000",
    )
)

RELOAD = (
    os.getenv(
        "RELOAD",
        "true",
    ).strip().lower()
    == "true"
)


# ==========================================================
# LOGGING
# ==========================================================

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
).upper()

logging.basicConfig(
    level=getattr(
        logging,
        LOG_LEVEL,
        logging.INFO,
    ),
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger("AITasker")


# ==========================================================
# STATIC DIRECTORY
# ==========================================================

STATIC_DIRECTORY = Path(
    os.getenv(
        "STATIC_DIR",
        str(PROJECT_ROOT / "static"),
    )
).resolve()

STATIC_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


# ==========================================================
# DATABASE
# ==========================================================

from backend.src.config.database import get_db, init_db


# ==========================================================
# IMPORT SQLALCHEMY MODELS
#
# Các model phải được import trước init_db() để SQLAlchemy
# đăng ký đầy đủ bảng, khóa ngoại và relationship.
# ==========================================================

import backend.src.models.association
import backend.src.models.auth
import backend.src.models.category
import backend.src.models.contract
import backend.src.models.enterprise
import backend.src.models.expert
import backend.src.models.project
import backend.src.models.proposal
import backend.src.models.review
import backend.src.models.skill
import backend.src.models.token_blacklist

try:
    import backend.src.models.payment
except ModuleNotFoundError:
    logger.warning(
        "Không tìm thấy backend.src.models.payment. "
        "Chức năng Payment có thể chưa hoạt động."
    )


# ==========================================================
# ROUTER
# ==========================================================

from backend.src.presentation import router as api_router


# ==========================================================
# CUSTOM EXCEPTIONS
# ==========================================================

from backend.src.domain.exceptions import AppError


# ==========================================================
# CORS CONFIGURATION
# ==========================================================

def get_allowed_origins() -> list[str]:
    """
    Đọc danh sách origin từ biến CORS_ORIGINS.

    Ví dụ trong .env:

    CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
    """

    default_origins = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173"
    )

    raw_origins = os.getenv(
        "CORS_ORIGINS",
        default_origins,
    )

    origins = [
        origin.strip().rstrip("/")
        for origin in raw_origins.split(",")
        if origin.strip()
    ]

    return list(dict.fromkeys(origins))


ALLOWED_ORIGINS = get_allowed_origins()


# ==========================================================
# APPLICATION LIFESPAN
# ==========================================================

@asynccontextmanager
async def lifespan(_: FastAPI):
    """
    Công việc được thực hiện khi backend khởi động và dừng.
    """

    logger.info("=" * 70)
    logger.info("Starting AITasker Backend...")
    logger.info("Environment: %s", APP_ENV)
    logger.info("Project root: %s", PROJECT_ROOT)
    logger.info("Environment file: %s", ENV_FILE)
    logger.info("Static directory: %s", STATIC_DIRECTORY)
    logger.info("Allowed origins: %s", ALLOWED_ORIGINS)
    logger.info("=" * 70)

    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.exception(
            "Database initialization failed: %s",
            exc,
        )

        # Không raise tại đây để /docs, /health và /api/ping
        # vẫn có thể hoạt động phục vụ việc kiểm tra lỗi.

    yield

    logger.info("=" * 70)
    logger.info("AITasker Backend stopped.")
    logger.info("=" * 70)


# ==========================================================
# CREATE INTERNAL FASTAPI APPLICATION
#
# Dùng internal_app để sau cùng bọc toàn bộ ứng dụng bằng
# CORSMiddleware. Cách này bảo đảm lỗi 500 vẫn có header CORS.
# ==========================================================

internal_app = FastAPI(
    title="AITasker Backend API",
    version="4.0.0",
    description=(
        "AI Marketplace Platform kết nối doanh nghiệp "
        "và chuyên gia AI."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "System",
            "description": (
                "Kiểm tra trạng thái ứng dụng, database "
                "và các dịch vụ hệ thống."
            ),
        },
        {
            "name": "AI Chatbot",
            "description": (
                "Trợ lý AI sử dụng dữ liệu PostgreSQL "
                "và Gemini để hỗ trợ người dùng."
            ),
        },
        {
            "name": "Authentication",
            "description": (
                "Đăng ký, đăng nhập và đặt lại mật khẩu."
            ),
        },
        {
            "name": "Users",
            "description": (
                "Quản lý tài khoản và hồ sơ người dùng."
            ),
        },
        {
            "name": "Projects",
            "description": "Quản lý các dự án AI.",
        },
        {
            "name": "Experts",
            "description": "Quản lý chuyên gia AI.",
        },
        {
            "name": "Enterprises",
            "description": "Quản lý doanh nghiệp.",
        },
        {
            "name": "Categories",
            "description": "Quản lý danh mục dự án.",
        },
        {
            "name": "Skills",
            "description": "Quản lý kỹ năng chuyên gia.",
        },
        {
            "name": "Proposals",
            "description": "Quản lý đề xuất và báo giá.",
        },
        {
            "name": "Contracts",
            "description": "Quản lý hợp đồng.",
        },
        {
            "name": "Payments",
            "description": "Quản lý thanh toán.",
        },
        {
            "name": "Reviews",
            "description": "Quản lý đánh giá.",
        },
        {
            "name": "Analytics",
            "description": "Dashboard và dữ liệu phân tích.",
        },
        {
            "name": "Statistics",
            "description": "Thống kê hệ thống.",
        },
        {
            "name": "Uploads",
            "description": (
                "Tải avatar, logo, CV và portfolio."
            ),
        },
    ],
)


# ==========================================================
# SESSION MIDDLEWARE
# ==========================================================

internal_app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv(
        "SECRET_KEY",
        "aitasker-development-secret-key-change-me",
    ),
    session_cookie=os.getenv(
        "SESSION_COOKIE_NAME",
        "aitasker_session",
    ),
    max_age=int(
        os.getenv(
            "SESSION_MAX_AGE",
            "86400",
        )
    ),
    same_site=os.getenv(
        "SESSION_SAME_SITE",
        "lax",
    ),
    https_only=(
        os.getenv(
            "SESSION_HTTPS_ONLY",
            "false",
        ).strip().lower()
        == "true"
    ),
)


# ==========================================================
# STATIC FILES
# ==========================================================

internal_app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIRECTORY),
    ),
    name="static",
)


# ==========================================================
# EXCEPTION HANDLER: APPLICATION ERROR
# ==========================================================

@internal_app.exception_handler(AppError)
async def app_error_handler(
    request: Request,
    exc: AppError,
) -> JSONResponse:
    logger.warning(
        "%s %s -> %s",
        request.method,
        request.url.path,
        exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_type": type(exc).__name__,
        },
    )


# ==========================================================
# EXCEPTION HANDLER: GLOBAL ERROR
# ==========================================================

@internal_app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Ghi đầy đủ traceback vào terminal.

    Trong development:
    - Trả message thật để dễ sửa lỗi.

    Trong production:
    - Chỉ trả thông báo chung để không lộ thông tin hệ thống.
    """

    logger.exception(
        "Unhandled error at %s %s",
        request.method,
        request.url.path,
    )

    content: dict[str, Any] = {
        "success": False,
        "message": "Internal Server Error",
        "error_type": type(exc).__name__,
    }

    if IS_DEVELOPMENT:
        content["message"] = str(exc)
        content["path"] = request.url.path
        content["method"] = request.method

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content,
    )


# ==========================================================
# ROOT ENDPOINT
# ==========================================================

@internal_app.get(
    "/",
    tags=["System"],
    summary="Thông tin ứng dụng",
)
async def root() -> dict[str, Any]:
    return {
        "success": True,
        "application": "AITasker Backend",
        "version": "4.0.0",
        "status": "running",
        "environment": APP_ENV,
        "documentation": "/docs",
        "redoc": "/redoc",
        "api_prefix": "/api",
    }


# ==========================================================
# HEALTH CHECK
# ==========================================================

@internal_app.get(
    "/health",
    tags=["System"],
    summary="Kiểm tra trạng thái backend",
)
def health_check(
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    database_status = "disconnected"
    database_error: str | None = None

    try:
        db.execute(text("SELECT 1"))
        database_status = "connected"

    except Exception as exc:
        db.rollback()

        database_error = str(exc)

        logger.exception(
            "Database health check failed: %s",
            exc,
        )

    response: dict[str, Any] = {
        "success": database_status == "connected",
        "status": (
            "ok"
            if database_status == "connected"
            else "degraded"
        ),
        "database": database_status,
        "gemini": (
            "configured"
            if os.getenv("GEMINI_API_KEY")
            else "disabled"
        ),
        "environment": APP_ENV,
    }

    if IS_DEVELOPMENT and database_error:
        response["database_error"] = database_error

    return response


# ==========================================================
# API PING
# ==========================================================

@internal_app.get(
    "/api/ping",
    tags=["System"],
    summary="Kiểm tra API",
)
async def ping() -> dict[str, Any]:
    return {
        "success": True,
        "message": "pong",
        "environment": APP_ENV,
    }


# ==========================================================
# INCLUDE BUSINESS ROUTERS
#
# Prefix /api chỉ được thêm tại đây.
#
# Ví dụ:
# app.py:            /api
# presentation:      /projects
# project_routes.py: /
#
# Endpoint cuối:
# /api/projects
# ==========================================================

internal_app.include_router(
    api_router,
    prefix="/api",
)


# ==========================================================
# WRAP ENTIRE APPLICATION WITH CORS
#
# Không dùng internal_app.add_middleware(CORSMiddleware, ...)
# ở đây.
#
# Bọc toàn bộ application giúp response lỗi 500 vẫn có:
# Access-Control-Allow-Origin
# ==========================================================

app = CORSMiddleware(
    app=internal_app,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=(
        r"^https?://"
        r"(localhost|127\.0\.0\.1)"
        r"(:\d+)?$"
    ),
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ==========================================================
# STARTUP CONFIGURATION LOG
# ==========================================================

logger.info("=" * 70)
logger.info("AITasker Backend configured successfully.")
logger.info("Application environment: %s", APP_ENV)
logger.info("Project root: %s", PROJECT_ROOT)
logger.info("Environment file: %s", ENV_FILE)
logger.info("Static directory: %s", STATIC_DIRECTORY)
logger.info("Allowed origins: %s", ALLOWED_ORIGINS)
logger.info("=" * 70)


# ==========================================================
# LOCAL DEVELOPMENT ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.src.app:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level=os.getenv(
            "UVICORN_LOG_LEVEL",
            "info",
        ),
    )