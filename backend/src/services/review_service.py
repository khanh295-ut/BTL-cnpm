from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.review import Review
from backend.src.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
)


class ReviewService:

    # =====================================================
    # GET ALL
    # =====================================================

    def get_all(
        self,
        db: Session,
    ):

        return (
            db.query(Review)
            .all()
        )

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        db: Session,
        review_id: UUID,
    ):

        return (
            db.query(Review)
            .filter(
                Review.id == review_id
            )
            .first()
        )

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        db: Session,
        data: ReviewCreate,
    ) -> Review:

        review = Review(

            project_id=data.project_id,

            expert_id=data.expert_id,

            rating=data.rating,

            comment=data.comment,

        )

        db.add(review)

        db.commit()

        db.refresh(review)

        return review

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        db: Session,
        review_id: UUID,
        data: ReviewUpdate,
    ):

        review = self.get_by_id(
            db,
            review_id,
        )

        if review is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():

            setattr(
                review,
                key,
                value,
            )

        db.commit()

        db.refresh(review)

        return review

    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        db: Session,
        review_id: UUID,
    ) -> bool:

        review = self.get_by_id(
            db,
            review_id,
        )

        if review is None:
            return False

        db.delete(review)

        db.commit()

        return True


review_service = ReviewService()