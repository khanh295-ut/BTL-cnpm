from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.infrastructure.repositories import SQLAlchemyAuthRepository
from backend.src.schemas.user import ChangeRoleRequest
from backend.src.presentation.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
def get_users(
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    repo = SQLAlchemyAuthRepository(db)

    return {
        "users": repo.list_users()
    }


@router.post("/users/{user_id}/role")
def change_role(
    user_id: str,
    data: ChangeRoleRequest,
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    repo = SQLAlchemyAuthRepository(db)

    user = repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = repo.ensure_role(data.role)

    user.roles = [role]
    repo.commit()

    return {"message": "Role updated"}