from __future__ import annotations

import os
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from jose import (
    ExpiredSignatureError,
    JWTError,
    jwt,
)
from passlib.context import CryptContext


# ======================================================
# PATH CONFIGURATION
# ======================================================

# File hiện tại:
# backend/src/config/security.py

CONFIG_DIR = Path(__file__).resolve().parent
SRC_DIR = CONFIG_DIR.parent
BACKEND_DIR = SRC_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

ENV_FILE = PROJECT_ROOT / ".env"


# ======================================================
# LOAD ENVIRONMENT
# ======================================================

load_dotenv(
    dotenv_path=ENV_FILE,
    override=False,
)


JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY"
)

if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY chưa được cấu hình. "
        f"Đã tìm file .env tại: {ENV_FILE}"
    )


JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)


try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "10080",
        )
    )
except ValueError as exc:
    raise RuntimeError(
        "ACCESS_TOKEN_EXPIRE_MINUTES phải là số nguyên."
    ) from exc


if ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
    raise RuntimeError(
        "ACCESS_TOKEN_EXPIRE_MINUTES phải lớn hơn 0."
    )


# Alias tương thích code cũ.
SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = JWT_ALGORITHM


# ======================================================
# PASSWORD CONFIGURATION
# ======================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ======================================================
# PASSWORD HELPERS
# ======================================================

def hash_password(
    password: str,
) -> str:
    normalized_password = str(
        password or ""
    )

    if not normalized_password:
        raise ValueError(
            "Mật khẩu không được để trống."
        )

    if len(normalized_password) < 8:
        raise ValueError(
            "Mật khẩu phải có ít nhất 8 ký tự."
        )

    return pwd_context.hash(
        normalized_password
    )


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    if (
        not plain_password
        or not hashed_password
    ):
        return False

    try:
        return pwd_context.verify(
            plain_password,
            hashed_password,
        )

    except (
        TypeError,
        ValueError,
    ):
        return False


# ======================================================
# JWT CREATE
# ======================================================

def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
) -> str:
    payload = data.copy()

    now = datetime.now(
        timezone.utc
    )

    expire = (
        now + expires_delta
        if expires_delta is not None
        else now + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload.update(
        {
            "iat": now,
            "exp": expire,
        }
    )

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


# ======================================================
# JWT DECODE
# ======================================================

def decode_access_token(
    token: str,
) -> dict[str, Any]:
    normalized_token = str(
        token or ""
    ).strip()

    if not normalized_token:
        raise ValueError(
            "Token không được để trống."
        )

    try:
        payload = jwt.decode(
            normalized_token,
            JWT_SECRET_KEY,
            algorithms=[
                JWT_ALGORITHM,
            ],
        )

    except ExpiredSignatureError as exc:
        raise ValueError(
            "Token đã hết hạn."
        ) from exc

    except JWTError as exc:
        raise ValueError(
            "Token không hợp lệ."
        ) from exc

    if not payload.get("sub"):
        raise ValueError(
            "Token không chứa thông tin người dùng."
        )

    return payload