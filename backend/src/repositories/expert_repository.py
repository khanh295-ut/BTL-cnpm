from sqlalchemy.orm import Session

from backend.src.models.expert import Expert


class ExpertRepository:


    def create(
        self,
        db: Session,
        expert: Expert
    ):

        db.add(expert)
        db.commit()
        db.refresh(expert)

        return expert



    def get_all(
        self,
        db: Session
    ):

        return db.query(Expert).all()



    def get_by_id(
        self,
        db: Session,
        expert_id
    ):

        return (
            db.query(Expert)
            .filter(
                Expert.id == expert_id
            )
            .first()
        )



    def update(
        self,
        db: Session,
        expert,
        data
    ):

        for key,value in data.items():

            setattr(
                expert,
                key,
                value
            )


        db.commit()
        db.refresh(expert)

        return expert



    def delete(
        self,
        db: Session,
        expert
    ):

        db.delete(expert)
        db.commit()