from sqlalchemy.orm import Session
from src.models.review import Review
from src.models.project import Project
from src.schemas.review import ReviewCreate


def create_review(db: Session, data: ReviewCreate):
    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        return None

    review = Review(
        project_id=data.project_id,
        reviewer_id=data.reviewer_id,
        expert_id=data.expert_id,
        rating=data.rating,
        comment=data.comment
    )

    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_reviews(db: Session, expert_id: int = None, project_id: int = None):
    query = db.query(Review)

    if expert_id:
        query = query.filter(Review.expert_id == expert_id)

    if project_id:
        query = query.filter(Review.project_id == project_id)

    return query.all()


def get_review_by_id(db: Session, review_id: int):
    return db.query(Review).filter(Review.id == review_id).first()


def update_review(db: Session, review_id: int, data: ReviewCreate):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return None

    review.rating = data.rating
    review.comment = data.comment

    db.commit()
    db.refresh(review)
    return review


def delete_review(db: Session, review_id: int):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        return False

    db.delete(review)
    db.commit()
    return True