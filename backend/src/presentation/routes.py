from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend.src.application.auth_use_cases import (
    forgot_password,
    login_user,
    register_user,
    reset_password,
    serialize_user,
)
from backend.src.application.content_use_cases import (
    accept_proposal,
    change_project_status,
    create_project,
    create_proposal,
    create_review,
    list_projects,
    list_proposals,
    list_reviews,
    update_project,
)
from backend.src.application.user_use_cases import change_password, get_profile, update_profile
from backend.src.domain.exceptions import AppError
from backend.src.config.database import get_db
from backend.src.infrastructure.repositories import SQLAlchemyAuthRepository
from backend.src.presentation.dependencies import get_current_user, require_admin as require_admin_dependency
from backend.src.schemas.auth import ForgotPasswordRequest, LoginRequest, UserCreate, ResetPasswordRequest
from backend.src.schemas.project import ProjectCreate, ProjectResponse, ProjectStatusUpdate, ProjectUpdate
from backend.src.schemas.proposal import ProposalCreate, ProposalResponse
from backend.src.schemas.review import ReviewCreate, ReviewResponse
from backend.src.schemas.user import ChangePasswordRequest, ChangeRoleRequest, ProfileUpdateRequest

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def handle_app_error(exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@router.get("/", include_in_schema=False)
def index():
    return RedirectResponse(url="/login")


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse, include_in_schema=False)
def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", {"request": request})


@router.get("/forgot-password", response_class=HTMLResponse, include_in_schema=False)
def forgot_password_page(request: Request):
    return templates.TemplateResponse(request, "forgot_password.html", {"request": request})


@router.get("/reset-password/{token}", response_class=HTMLResponse, include_in_schema=False)
def reset_password_page(request: Request, token: str, db: Session = Depends(get_db)):
    reset_item = SQLAlchemyAuthRepository(db).get_reset_token(token)
    invalid = reset_item is None or not reset_item.is_valid()
    return templates.TemplateResponse(request, "reset_password.html", {"request": request, "token": token, "invalid": invalid})


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard_page(request: Request):
    return templates.TemplateResponse(request, "dashboard.html", {"request": request})


@router.get("/profile", response_class=HTMLResponse, include_in_schema=False)
def profile_page(request: Request):
    return templates.TemplateResponse(request, "profile.html", {"request": request})


@router.post("/login")
def login_api(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = login_user(db, payload.email, payload.password)
    request.session["user_id"] = user.id
    return {"message": "Đăng nhập thành công.", "user": serialize_user(user)}


@router.post("/register", status_code=201)
def register_api(payload: UserCreate, db: Session = Depends(get_db)):
    user = register_user(db, payload.username.strip(), payload.email.lower(), payload.password)
    return {"message": "Đăng ký thành công. Vui lòng đăng nhập.", "user": serialize_user(user)}
