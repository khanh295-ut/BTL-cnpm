# backend/src/presentation/routes/skill_routes.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.skill import (
    SkillCreate,
    SkillResponse,
    SkillUpdate,
)
from backend.src.services.skill_service import skill_service


# ==========================================================
# ROUTER
# Prefix /skills được thêm trong all_routes.py.
# Prefix /api được thêm trong app.py.
# ==========================================================

router = APIRouter(
    tags=["Skills"],
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[SkillResponse],
)
def get_all_skills(
    db: Session = Depends(get_db),
):
    return skill_service.get_all(db)


# ==========================================================
# GET BY EXPERT
# Đặt route tĩnh trước route /{skill_id}
# ==========================================================

@router.get(
    "/expert/{expert_id}",
    response_model=list[SkillResponse],
)
def get_skills_by_expert(
    expert_id: UUID,
    db: Session = Depends(get_db),
):
    return skill_service.get_by_expert(
        db,
        expert_id,
    )


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{skill_id}",
    response_model=SkillResponse,
)
def get_skill(
    skill_id: UUID,
    db: Session = Depends(get_db),
):
    skill = skill_service.get_by_id(
        db,
        skill_id,
    )

    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    return skill


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_skill(
    data: SkillCreate,
    db: Session = Depends(get_db),
):
    return skill_service.create(
        db,
        data,
    )


# ==========================================================
# UPDATE
# ==========================================================

@router.put(
    "/{skill_id}",
    response_model=SkillResponse,
)
def update_skill(
    skill_id: UUID,
    data: SkillUpdate,
    db: Session = Depends(get_db),
):
    skill = skill_service.update(
        db,
        skill_id,
        data,
    )

    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    return skill


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_skill(
    skill_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = skill_service.delete(
        db,
        skill_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )

    return None