from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.models.auth import User

# =====================================================
# JWT CONFIG
# =====================================================

SECRET_KEY = "change-this-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

# =====================================================
# CREATE TOKEN
# =====================================================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
):

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update(
        {
            "exp": expire
        }
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# =====================================================
# DECODE TOKEN
# =====================================================

def decode_token(token: str):

    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )


# =====================================================
# CURRENT USER
# =====================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise credentials_exception

    return user


# =====================================================
# CURRENT ADMIN
# =====================================================

def get_current_admin(
    current_user: User = Depends(get_current_user),
):

    role_names = [
        role.name.lower()
        for role in current_user.roles
    ]

    if "admin" not in role_names:

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required",
        )

    return current_user


# =====================================================
# OPTIONAL USER
# =====================================================

def get_optional_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            return None

        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    except Exception:
        return None