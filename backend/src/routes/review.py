from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.models.review import Review
from src.schemas.review import ReviewCreate

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("/")
def create_review(data: ReviewCreate, db: Session = Depends(get_db)):
    review = Review(**data.dict())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

@router.get("/")
def get_reviews(db: Session = Depends(get_db)):
    return db.query(Review).all()