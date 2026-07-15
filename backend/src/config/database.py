from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ==========================================================
# PATH CONFIGURATION
# ==========================================================

CONFIG_DIR = Path(__file__).resolve().parent
SRC_DIR = CONFIG_DIR.parent
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
# LOGGING
# ==========================================================

logger = logging.getLogger("AITasker.Database")


# ==========================================================
# DATABASE URL
# ==========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:mat_khau@localhost:5432/aitasker",
).strip()

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL chưa được cấu hình trong file .env"
    )


# ==========================================================
# BASE MODEL
# ==========================================================

class Base(DeclarativeBase):
    """
    Base class cho toàn bộ SQLAlchemy models.
    """

    pass


# ==========================================================
# DATABASE ENGINE
# ==========================================================

engine: Engine = create_engine(
    DATABASE_URL,
    echo=(
        os.getenv(
            "SQL_ECHO",
            "false",
        ).strip().lower()
        == "true"
    ),
    pool_pre_ping=True,
    pool_recycle=1800,
)


# ==========================================================
# SESSION FACTORY
# ==========================================================

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

def init_db() -> None:
    """
    Import toàn bộ models trước khi tạo bảng.

    Việc import giúp SQLAlchemy đăng ký đầy đủ:
    - bảng
    - khóa ngoại
    - relationship
    - mapper
    """

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
            "Bỏ qua model payment."
        )

    try:
        Base.metadata.create_all(
            bind=engine,
        )

        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        logger.info(
            "Database initialized successfully."
        )

    except Exception as exc:
        logger.exception(
            "Database initialization failed: %s",
            exc,
        )
        raise


# ==========================================================
# DATABASE DEPENDENCY
# ==========================================================

def get_db() -> Generator[Session, None, None]:
    """
    Dependency cấp Session cho FastAPI endpoint.

    Session sẽ:
    - rollback nếu có lỗi
    - luôn đóng sau khi xử lý xong
    """

    db = SessionLocal()

    try:
        yield db

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ==========================================================
# DATABASE CONNECTION CHECK
# ==========================================================

def check_database_connection() -> bool:
    """
    Kiểm tra kết nối PostgreSQL.

    Trả về:
    - True: kết nối thành công
    - False: kết nối thất bại
    """

    try:
        with engine.connect() as connection:
            connection.execute(
                text("SELECT 1")
            )

        return True

    except Exception as exc:
        logger.exception(
            "Database connection failed: %s",
            exc,
        )

        return False