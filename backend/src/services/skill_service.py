from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.skill import Skill
from backend.src.schemas.skill import SkillCreate, SkillUpdate


class SkillService:

    # =====================================================
    # GET ALL
    # =====================================================

    def get_all(self, db: Session):
        return (
            db.query(Skill)
            .order_by(Skill.name.asc())
            .all()
        )

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        db: Session,
        skill_id: UUID,
    ):
        return (
            db.query(Skill)
            .filter(Skill.id == skill_id)
            .first()
        )

    # =====================================================
    # GET BY EXPERT
    # =====================================================

    def get_by_expert(
        self,
        db: Session,
        expert_id: UUID,
    ):
        return (
            db.query(Skill)
            .filter(Skill.expert_id == expert_id)
            .all()
        )

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        db: Session,
        data: SkillCreate,
    ):

        skill = Skill(
            expert_id=data.expert_id,
            name=data.name,
        )

        db.add(skill)
        db.commit()
        db.refresh(skill)

        return skill

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        db: Session,
        skill_id: UUID,
        data: SkillUpdate,
    ):

        skill = self.get_by_id(
            db,
            skill_id,
        )

        if skill is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(skill, key, value)

        db.commit()
        db.refresh(skill)

        return skill

    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        db: Session,
        skill_id: UUID,
    ):

        skill = self.get_by_id(
            db,
            skill_id,
        )

        if skill is None:
            return False

        db.delete(skill)
        db.commit()

        return True


skill_service = SkillService()