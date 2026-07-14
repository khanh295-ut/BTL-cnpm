# backend/src/presentation/routes/review_routes.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.review import (
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate,
)
from backend.src.services.review_service import review_service


# ==========================================================
# ROUTER
# Prefix /reviews đã được thêm trong all_routes.py.
# Prefix /api đã được thêm trong app.py.
# ==========================================================

router = APIRouter(
    tags=["Reviews"],
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[ReviewResponse],
)
def get_all_reviews(
    db: Session = Depends(get_db),
):
    return review_service.get_all(db)


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{review_id}",
    response_model=ReviewResponse,
)
def get_review(
    review_id: UUID,
    db: Session = Depends(get_db),
):
    review = review_service.get_by_id(
        db,
        review_id,
    )

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    return review


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
):
    return review_service.create(
        db,
        data,
    )


# ==========================================================
# UPDATE
# ==========================================================

@router.put(
    "/{review_id}",
    response_model=ReviewResponse,
)
def update_review(
    review_id: UUID,
    data: ReviewUpdate,
    db: Session = Depends(get_db),
):
    review = review_service.update(
        db,
        review_id,
        data,
    )

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    return review


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_review(
    review_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = review_service.delete(
        db,
        review_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    return None