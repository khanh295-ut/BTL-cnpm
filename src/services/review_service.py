from sqlalchemy.orm import Session
from src.models.review import Review
from src.models.project import Project


def create_review(db: Session, data):
    # check project tồn tại
    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        return None

    # chỉ cho review khi project DONE (nếu bạn muốn chuẩn đồ án)
    # if project.status != "DONE":
    #     return None

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


def get_reviews(db: Session):
    return db.query(Review).all()