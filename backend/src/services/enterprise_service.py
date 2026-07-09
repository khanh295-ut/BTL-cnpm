from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.enterprise import Enterprise
from backend.src.schemas.enterprise import (
    EnterpriseCreate,
    EnterpriseUpdate,
)


class EnterpriseService:

    # =====================================================
    # GET ALL
    # =====================================================

    def get_all(
        self,
        db: Session,
    ):

        return (
            db.query(Enterprise)
            .order_by(Enterprise.created_at.desc())
            .all()
        )

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        db: Session,
        enterprise_id: UUID,
    ):

        return (
            db.query(Enterprise)
            .filter(Enterprise.id == enterprise_id)
            .first()
        )

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        db: Session,
        data: EnterpriseCreate,
    ) -> Enterprise:

        enterprise = Enterprise(

            name=data.name,

            email=data.email,

            description=data.description,

        )

        db.add(enterprise)

        db.commit()

        db.refresh(enterprise)

        return enterprise

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        db: Session,
        enterprise_id: UUID,
        data: EnterpriseUpdate,
    ):

        enterprise = self.get_by_id(
            db,
            enterprise_id,
        )

        if enterprise is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():

            setattr(
                enterprise,
                key,
                value,
            )

        db.commit()

        db.refresh(enterprise)

        return enterprise

    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        db: Session,
        enterprise_id: UUID,
    ) -> bool:

        enterprise = self.get_by_id(
            db,
            enterprise_id,
        )

        if enterprise is None:
            return False

        db.delete(enterprise)

        db.commit()

        return True


# =====================================================
# Singleton
# =====================================================

enterprise_service = EnterpriseService()