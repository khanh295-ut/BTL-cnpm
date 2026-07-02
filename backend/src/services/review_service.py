from sqlalchemy.orm import Session
from backend.src.models.review import Review


class ReviewService:

    def create_review(self, db: Session, data):

        review = Review(
            project_id=data.project_id,
            expert_id=data.expert_id,
            rating=data.rating,
            comment=data.comment
        )

        db.add(review)
        db.commit()
        db.refresh(review)

        return review

    def list_reviews(self, db: Session):
        return db.query(Review).all()