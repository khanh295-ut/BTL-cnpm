from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.admin import (
    DashboardResponse,
    ChangeRoleRequest,
    MessageResponse,
    AdminUserResponse,
    ProjectStatistic,
    ProposalStatistic,
    RoleStatistic,
)
from backend.src.services.admin_service import AdminService
from backend.src.services.jwt_service import get_current_admin


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

service = AdminService()


# =====================================================
# DASHBOARD
# =====================================================

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
)
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    return service.dashboard(db)


# =====================================================
# LIST USERS
# =====================================================

@router.get(
    "/users",
    response_model=list[AdminUserResponse],
)
def get_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    return service.get_all_users(db)


# =====================================================
# USER DETAIL
# =====================================================

@router.get(
    "/users/{user_id}",
    response_model=AdminUserResponse,
)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):

    user = service.get_user(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


# =====================================================
# DELETE USER
# =====================================================

@router.delete(
    "/users/{user_id}",
    response_model=MessageResponse,
)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):

    success = service.delete_user(db, user_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return {
        "message": "User deleted successfully."
    }


# =====================================================
# CHANGE ROLE
# =====================================================

@router.put(
    "/users/{user_id}/role",
    response_model=AdminUserResponse,
)
def change_role(
    user_id: UUID,
    data: ChangeRoleRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):

    user = service.change_role(
        db,
        user_id,
        data.role,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User or Role not found",
        )

    return user


# =====================================================
# PROJECT STATISTICS
# =====================================================

@router.get(
    "/statistics/projects",
    response_model=list[ProjectStatistic],
)
def project_statistics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    return service.project_statistics(db)


# =====================================================
# PROPOSAL STATISTICS
# =====================================================

@router.get(
    "/statistics/proposals",
    response_model=list[ProposalStatistic],
)
def proposal_statistics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    return service.proposal_statistics(db)


# =====================================================
# ROLE STATISTICS
# =====================================================

@router.get(
    "/statistics/roles",
    response_model=list[RoleStatistic],
)
def role_statistics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    return service.users_by_role(db)


# =====================================================
# REVIEW STATISTICS
# =====================================================

@router.get(
    "/statistics/reviews",
)
def review_statistics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):

    return {
        "average_rating": service.average_rating(db)
    }