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
- all_routes.py thêm prefix tài nguyên.
- các file *_routes.py không tự khai báo prefix.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

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
# STATIC DIRECTORY
# ==========================================================

STATIC_DIRECTORY = Path(
    os.getenv(
        "STATIC_DIR",
        str(PROJECT_ROOT / "static"),
    )
).resolve()


# ==========================================================
# LOGGING
# ==========================================================

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
).upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)

logger = logging.getLogger("AITasker")


# ==========================================================
# DATABASE
# ==========================================================

from backend.src.config.database import get_db, init_db


# ==========================================================
# IMPORT SQLALCHEMY MODELS
#
# Các model phải được import trước khi init_db() chạy để
# SQLAlchemy đăng ký đầy đủ bảng và quan hệ trong metadata.
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
        "Chức năng Payment có thể chưa hoạt động đầy đủ."
    )


# ==========================================================
# APPLICATION ROUTER
# ==========================================================

from backend.src.presentation import router as api_router


# ==========================================================
# CUSTOM EXCEPTIONS
# ==========================================================

from backend.src.domain.exceptions import AppError


# ==========================================================
# CORS HELPERS
# ==========================================================

def get_allowed_origins() -> list[str]:
    """
    Đọc danh sách CORS origins từ biến CORS_ORIGINS trong .env.

    Ví dụ:
    CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
    """

    raw_origins = os.getenv(
        "CORS_ORIGINS",
        (
            "http://localhost:5173,"
            "http://127.0.0.1:5173,"
            "http://localhost:5000,"
            "http://127.0.0.1:5000"
        ),
    )

    return [
        origin.strip()
        for origin in raw_origins.split(",")
        if origin.strip()
    ]


# ==========================================================
# APPLICATION LIFESPAN
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Xử lý công việc khi FastAPI khởi động và kết thúc.
    """

    logger.info("=" * 60)
    logger.info("Starting AITasker Backend...")
    logger.info("=" * 60)

    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.exception(
            "Database initialization failed: %s",
            exc,
        )
        # Không raise để Swagger và endpoint health vẫn có thể
        # khởi động, giúp kiểm tra lỗi cấu hình hoặc database.

    yield

    logger.info("=" * 60)
    logger.info("AITasker Backend stopped.")
    logger.info("=" * 60)


# ==========================================================
# CREATE FASTAPI APPLICATION
# ==========================================================

app = FastAPI(
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
                "Trợ lý AI đọc dữ liệu thật từ PostgreSQL "
                "và sử dụng Gemini để diễn giải."
            ),
        },
        {
            "name": "Authentication",
            "description": "Đăng ký, đăng nhập và đặt lại mật khẩu.",
        },
        {
            "name": "Users",
            "description": "Quản lý tài khoản và hồ sơ người dùng.",
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
            "description": "Tải avatar, logo, CV và portfolio.",
        },
    ],
)


# ==========================================================
# CORS MIDDLEWARE
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# SESSION MIDDLEWARE
#
# Chatbot dùng session để nhớ đối tượng được hỏi trước đó.
# Frontend phải bật credentials:
# - Axios: withCredentials: true
# - fetch: credentials: "include"
# ==========================================================

app.add_middleware(
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
        ).lower()
        == "true"
    ),
)


# ==========================================================
# STATIC FILES
# ==========================================================

STATIC_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIRECTORY),
    ),
    name="static",
)


# ==========================================================
# EXCEPTION HANDLER: APPLICATION ERROR
# ==========================================================

@app.exception_handler(AppError)
async def app_error_handler(
    request: Request,
    exc: AppError,
):
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
        },
    )


# ==========================================================
# EXCEPTION HANDLER: GLOBAL ERROR
# ==========================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled error at %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal Server Error",
        },
    )


# ==========================================================
# ROOT ENDPOINT
# ==========================================================

@app.get(
    "/",
    tags=["System"],
    summary="Thông tin ứng dụng",
)
async def root():
    return {
        "success": True,
        "application": "AITasker Backend",
        "version": "4.0.0",
        "status": "running",
        "documentation": "/docs",
        "api_prefix": "/api",
    }


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get(
    "/health",
    tags=["System"],
    summary="Kiểm tra trạng thái backend",
)
def health_check(
    db: Session = Depends(get_db),
):
    database_status = "disconnected"

    try:
        db.execute(text("SELECT 1"))
        database_status = "connected"
    except Exception as exc:
        db.rollback()
        logger.exception(
            "Database health check failed: %s",
            exc,
        )

    gemini_status = (
        "configured"
        if os.getenv("GEMINI_API_KEY")
        else "disabled"
    )

    return {
        "success": True,
        "status": "ok",
        "database": database_status,
        "gemini": gemini_status,
        "environment": os.getenv(
            "APP_ENV",
            "development",
        ),
    }


# ==========================================================
# API PING
# ==========================================================

@app.get(
    "/api/ping",
    tags=["System"],
    summary="Kiểm tra API",
)
async def ping():
    return {
        "success": True,
        "message": "pong",
    }


# ==========================================================
# INCLUDE ALL BUSINESS ROUTERS
#
# Prefix /api chỉ được thêm tại đây.
#
# Ví dụ:
# app.py:        /api
# all_routes.py: /projects
# project route: ""
#
# Endpoint cuối: /api/projects
# ==========================================================

app.include_router(
    api_router,
    prefix="/api",
)


# ==========================================================
# STARTUP INFORMATION
# ==========================================================

logger.info("=" * 60)
logger.info("AITasker Backend configured successfully.")
logger.info("Project root: %s", PROJECT_ROOT)
logger.info("Environment file: %s", ENV_FILE)
logger.info("Static directory: %s", STATIC_DIRECTORY)
logger.info("Allowed origins: %s", get_allowed_origins())
logger.info("=" * 60)


# ==========================================================
# LOCAL DEVELOPMENT ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.src.app:app",
        host=os.getenv(
            "HOST",
            "127.0.0.1",
        ),
        port=int(
            os.getenv(
                "PORT",
                "8000",
            )
        ),
        reload=(
            os.getenv(
                "RELOAD",
                "true",
            ).lower()
            == "true"
        ),
        log_level=os.getenv(
            "UVICORN_LOG_LEVEL",
            "info",
        ),
    )
