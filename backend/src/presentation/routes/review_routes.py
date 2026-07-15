from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.schemas.review import ReviewCreate
from src.services.review_service import (
    create_review,
    get_reviews,
    get_review_by_id,
    update_review,
    delete_review,
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/")
def create(data: ReviewCreate, db: Session = Depends(get_db)):
    review = create_review(db, data)
    if not review:
        raise HTTPException(status_code=404, detail="Project not found")
    return review


@router.get("/")
def get_all(
    expert_id: int = None,
    project_id: int = None,
    db: Session = Depends(get_db),
):
    return get_reviews(db, expert_id, project_id)


@router.get("/{review_id}")
def get_one(review_id: int, db: Session = Depends(get_db)):
    review = get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.put("/{review_id}")
def update(review_id: int, data: ReviewCreate, db: Session = Depends(get_db)):
    review = update_review(db, review_id, data)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.delete("/{review_id}")
def delete(review_id: int, db: Session = Depends(get_db)):
    success = delete_review(db, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted successfully"}