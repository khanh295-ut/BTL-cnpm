from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.auth import UserCreate, LoginRequest, TokenResponse
from backend.src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])

service = AuthService()


@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    user = service.register(db, data)

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username
    }


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):

    token = service.login(db, data)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )