from sqlalchemy.orm import Session
from backend.src.models.expert import Expert


class ExpertService:

    def create_expert(self, db: Session, data):

        expert = Expert(
            name=data.name,
            skills=data.skills,
            experience=data.experience,
            description=data.description
        )

        db.add(expert)
        db.commit()
        db.refresh(expert)

        return expert

    def list_experts(self, db: Session):

        return db.query(Expert).all()

    def search_experts(self, db: Session, keyword: str):

        return db.query(Expert).filter(
            Expert.name.contains(keyword)
        ).all()