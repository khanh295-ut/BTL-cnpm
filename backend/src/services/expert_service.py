from uuid import UUID

from sqlalchemy.orm import Session, selectinload

from backend.src.models.expert import Expert
from backend.src.models.skill import Skill

from backend.src.schemas.expert import (
    ExpertCreate,
    ExpertUpdate,
)


class ExpertService:


    # =====================================================
    # GET ALL
    # =====================================================

    def get_all(
        self,
        db: Session
    ):

        return (
            db.query(Expert)
            .options(
                selectinload(
                    Expert.skills
                )
            )
            .order_by(
                Expert.created_at.desc()
            )
            .all()
        )


    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        db: Session,
        expert_id: UUID
    ):

        return (
            db.query(Expert)
            .options(
                selectinload(
                    Expert.skills
                )
            )
            .filter(
                Expert.id == expert_id
            )
            .first()
        )


    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        db: Session,
        data: ExpertCreate
    ) -> Expert:


        try:

            # tạo Expert
            expert = Expert(
                full_name=data.full_name,
                title=data.title,
                bio=data.bio,
                hourly_rate=data.hourly_rate,
                location=data.location,
            )


            db.add(expert)

            # lấy id sau khi insert
            db.flush()


            # tạo Skill
            for item in data.skills:

                skill = Skill(
                    expert_id=expert.id,
                    name=item.name,
                )

                db.add(skill)


            db.commit()


            return self.get_by_id(
                db,
                expert.id
            )


        except Exception:

            db.rollback()
            raise



    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        db: Session,
        expert_id: UUID,
        data: ExpertUpdate
    ):


        expert = self.get_by_id(
            db,
            expert_id
        )


        if expert is None:
            return None


        try:

            # update thông tin cơ bản
            update_data = data.model_dump(
                exclude_unset=True,
                exclude={
                    "skills"
                }
            )


            for key, value in update_data.items():

                setattr(
                    expert,
                    key,
                    value
                )



            # update skill
            if data.skills is not None:


                # xóa skill hiện tại
                expert.skills.clear()


                # thêm skill mới
                for item in data.skills:

                    expert.skills.append(
                        Skill(
                            name=item.name
                        )
                    )


            db.commit()


            return self.get_by_id(
                db,
                expert.id
            )


        except Exception:

            db.rollback()
            raise



    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        db: Session,
        expert_id: UUID
    ) -> bool:


        expert = self.get_by_id(
            db,
            expert_id
        )


        if expert is None:
            return False


        try:

            db.delete(expert)

            db.commit()

            return True


        except Exception:

            db.rollback()
            raise



# =====================================================
# Singleton
# =====================================================

expert_service = ExpertService()