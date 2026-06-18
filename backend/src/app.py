from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from backend.src.domain.exceptions import AppError
from backend.src.config.database import Base, SessionLocal, engine
from backend.src.models import Permission, PasswordResetToken, Project, Proposal, Review, Role, User
from backend.src.infrastructure.repositories import SQLAlchemyAuthRepository
from backend.src.presentation.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AITasker Backend")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key="change-me-in-production", same_site="lax")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


app.include_router(router)


@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    try:
        repo = SQLAlchemyAuthRepository(db)
        admin_role = repo.ensure_role("Admin", "Administrator role")
        user_role = repo.ensure_role("User", "Standard user role")
        manage_users = repo.ensure_permission("manage_users", "Quản lý người dùng")
        reset_password = repo.ensure_permission("reset_password", "Reset mật khẩu")
        if manage_users not in admin_role.permissions:
            admin_role.permissions.append(manage_users)
        if reset_password not in admin_role.permissions:
            admin_role.permissions.append(reset_password)
        if reset_password not in user_role.permissions:
            user_role.permissions.append(reset_password)

        if repo.get_user_by_username("admin") is None:
            admin = User(username="admin", email="admin@example.com", full_name="Admin System", bio="Tài khoản Admin mẫu.")
            admin.set_password("Admin@123")
            admin.roles.append(admin_role)
            repo.save_user(admin)

        if repo.get_user_by_username("alice") is None:
            member = User(username="alice", email="alice@example.com", full_name="Alice Nguyen", bio="Người dùng mẫu.")
            member.set_password("User@123")
            member.roles.append(user_role)
            repo.save_user(member)

        repo.commit()
    finally:
        db.close()