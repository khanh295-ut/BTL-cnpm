from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.expert import (
    ExpertCreate,
    ExpertUpdate,
    ExpertResponse,
)
from backend.src.services.expert_service import expert_service


# ==========================================================
# ROUTER
# Prefix /experts đã được thêm trong all_routes.py
# Prefix /api đã được thêm trong app.py
# ==========================================================

router = APIRouter(
    tags=["Experts"],
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[ExpertResponse],
)
def get_all_experts(
    db: Session = Depends(get_db),
):
    return expert_service.get_all(db)


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{expert_id}",
    response_model=ExpertResponse,
)
def get_expert(
    expert_id: UUID,
    db: Session = Depends(get_db),
):
    expert = expert_service.get_by_id(
        db,
        expert_id,
    )

    if expert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    return expert


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "",
    response_model=ExpertResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_expert(
    data: ExpertCreate,
    db: Session = Depends(get_db),
):
    return expert_service.create(
        db,
        data,
    )


# ==========================================================
# UPDATE
# ==========================================================

@router.put(
    "/{expert_id}",
    response_model=ExpertResponse,
)
def update_expert(
    expert_id: UUID,
    data: ExpertUpdate,
    db: Session = Depends(get_db),
):
    expert = expert_service.update(
        db,
        expert_id,
        data,
    )

    if expert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    return expert


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{expert_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expert(
    expert_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = expert_service.delete(
        db,
        expert_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    return None