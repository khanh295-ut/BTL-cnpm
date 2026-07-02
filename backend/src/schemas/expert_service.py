from sqlalchemy.orm import Session
from backend.src.models.expert import Expert


class ExpertService:

    # =========================
    # GET ALL EXPERTS + FILTER
    # =========================
    def get_experts(self, db: Session, skill=None, min_price=None, max_price=None):

        query = db.query(Expert)

        if skill:
            query = query.filter(Expert.skills.any(name=skill))

        if min_price:
            query = query.filter(Expert.hourly_rate >= min_price)

        if max_price:
            query = query.filter(Expert.hourly_rate <= max_price)

        return query.all()


    # =========================
    # UPDATE PROFILE
    # =========================
    def update_expert(self, db: Session, expert, data):

        if data.full_name:
            expert.full_name = data.full_name

        if data.bio:
            expert.bio = data.bio

        if data.hourly_rate:
            expert.hourly_rate = data.hourly_rate

        db.commit()
        db.refresh(expert)

        return expert


    # =========================
    # DELETE EXPERT
    # =========================
    def delete_expert(self, db: Session, expert):

        db.delete(expert)
        db.commit()

        return True