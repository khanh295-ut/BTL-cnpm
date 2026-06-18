from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, Form, HTTPException, Request
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
from backend.src.application.user_use_cases import change_password, get_profile, require_admin, update_profile
from backend.src.domain.exceptions import AppError
from backend.src.config.database import get_db
from backend.src.infrastructure.repositories import SQLAlchemyAuthRepository
from backend.src.presentation.dependencies import get_current_user, require_admin as require_admin_dependency
from backend.src.schemas.auth import ForgotPasswordRequest, LoginRequest, RegisterRequest, ResetPasswordRequest
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
    user = login_user(db, payload.login, payload.password)
    request.session["user_id"] = user.id
    return {"message": "Đăng nhập thành công.", "user": serialize_user(user)}


@router.post("/register", status_code=201)
def register_api(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, payload.username.strip(), payload.email.lower(), payload.password)
    return {"message": "Đăng ký thành công. Vui lòng đăng nhập.", "user": serialize_user(user)}


@router.post("/logout")
def logout_api(request: Request):
    request.session.pop("user_id", None)
    return {"message": "Đã đăng xuất. Vui lòng truy cập lại trang đăng nhập."}


@router.post("/forgot-password")
def forgot_password_api(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    reset_url = forgot_password(db, payload.email.lower())
    response = {"message": "Nếu email tồn tại trong hệ thống, đường dẫn reset mật khẩu đã được tạo."}
    if reset_url:
        response["reset_url"] = reset_url
    return response


@router.post("/reset-password/{token}")
def reset_password_api(token: str, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_password(db, token, payload.password, payload.confirm_password)
    return {"message": "Đổi mật khẩu thành công. Bạn có thể đăng nhập lại."}


@router.get("/api/profile")
def profile_api(current_user=Depends(get_current_user)):
    return {"user": get_profile(current_user)}


@router.post("/profile/update")
def profile_update_api(payload: ProfileUpdateRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = update_profile(db, current_user, payload.full_name, payload.email, payload.bio)
    return {"message": "Cập nhật hồ sơ thành công.", "user": user}


@router.post("/profile/change-password")
def profile_change_password_api(payload: ChangePasswordRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    change_password(db, current_user, payload.current_password, payload.new_password)
    return {"message": "Đổi mật khẩu thành công."}


@router.get("/admin/users")
def list_users_api(current_user=Depends(require_admin_dependency), db: Session = Depends(get_db)):
    users = SQLAlchemyAuthRepository(db).list_users()
    return {"users": [serialize_user(user) for user in users]}


@router.get("/admin/users/{user_id}")
def get_user_api(user_id: int, current_user=Depends(require_admin_dependency), db: Session = Depends(get_db)):
    user = SQLAlchemyAuthRepository(db).get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    return {"user": serialize_user(user)}


@router.post("/admin/users/{user_id}/role")
def change_user_role_api(user_id: int, payload: ChangeRoleRequest, current_user=Depends(require_admin_dependency), db: Session = Depends(get_db)):
    repo = SQLAlchemyAuthRepository(db)
    user = repo.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Not found")
    if payload.role not in {"Admin", "User"}:
        raise HTTPException(status_code=400, detail="Vai trò không hợp lệ. Chỉ hỗ trợ Admin hoặc User.")
    selected_role = repo.ensure_role(payload.role, f"{payload.role} role")
    user.roles = [selected_role]
    repo.commit()
    return {"message": "Cập nhật vai trò thành công.", "user": serialize_user(user)}


@router.get("/projects")
def get_projects_api(db: Session = Depends(get_db)):
    return list_projects(db)


@router.post("/projects", response_model=ProjectResponse)
def create_project_api(payload: ProjectCreate, db: Session = Depends(get_db)):
    return create_project(db, payload.title, payload.description)


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project_api(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    return update_project(db, project_id, payload.title, payload.description)


@router.patch("/projects/{project_id}/status", response_model=ProjectResponse)
def change_project_status_api(project_id: int, payload: ProjectStatusUpdate, db: Session = Depends(get_db)):
    return change_project_status(db, project_id, payload.status)


@router.get("/proposals")
def get_proposals_api(db: Session = Depends(get_db)):
    return list_proposals(db)


@router.post("/proposals", response_model=ProposalResponse)
def create_proposal_api(payload: ProposalCreate, db: Session = Depends(get_db)):
    return create_proposal(db, payload.project_id, payload.expert_id, payload.price, payload.comment)


@router.post("/proposals/{proposal_id}/accept")
def accept_proposal_api(proposal_id: int, db: Session = Depends(get_db)):
    proposal = accept_proposal(db, proposal_id)
    return {"message": "Proposal accepted", "data": proposal}


@router.get("/reviews")
def get_reviews_api(db: Session = Depends(get_db)):
    return list_reviews(db)


@router.post("/reviews", response_model=ReviewResponse)
def create_review_api(payload: ReviewCreate, db: Session = Depends(get_db)):
    return create_review(db, payload.project_id, payload.expert_id, payload.rating, payload.comment)
