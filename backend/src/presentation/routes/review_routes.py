from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.application.content_use_cases import (
    create_review,
    list_reviews
)

from backend.src.schemas.review import (
    ReviewCreate,
    ReviewResponse
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/", response_model=list[ReviewResponse])
def get_reviews(db: Session = Depends(get_db)):
    return list_reviews(db)


@router.post("/", response_model=ReviewResponse)
def create(data: ReviewCreate, db: Session = Depends(get_db)):
    return create_review(
        db,
        data.project_id,
        data.expert_id,
        data.rating,
        data.comment
    )