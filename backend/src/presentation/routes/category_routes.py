from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)
from backend.src.services.category_service import category_service


# ==========================================================
# ROUTER
# ==========================================================

router = APIRouter(
    tags=["Categories"]
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[CategoryResponse],
)
def get_categories(
    db: Session = Depends(get_db),
):
    return category_service.get_all(db)


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: UUID,
    db: Session = Depends(get_db),
):
    category = category_service.get_by_id(
        db,
        category_id,
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return category


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
):
    return category_service.create(
        db,
        data,
    )


# ==========================================================
# UPDATE
# ==========================================================

@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
):
    category = category_service.update(
        db,
        category_id,
        data,
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return category


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
):
    success = category_service.delete(
        db,
        category_id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return None