from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.category import Category
from backend.src.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
)


class CategoryService:

    # =====================================================
    # GET ALL
    # =====================================================

    def get_all(
        self,
        db: Session,
    ):
        return (
            db.query(Category)
            .order_by(Category.name.asc())
            .all()
        )

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        db: Session,
        category_id: UUID,
    ):
        return (
            db.query(Category)
            .filter(Category.id == category_id)
            .first()
        )

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        db: Session,
        data: CategoryCreate,
    ) -> Category:

        category = Category(
            name=data.name,
            description=data.description,
        )

        db.add(category)
        db.commit()
        db.refresh(category)

        return category

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        db: Session,
        category_id: UUID,
        data: CategoryUpdate,
    ):

        category = self.get_by_id(
            db,
            category_id,
        )

        if category is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(category, key, value)

        db.commit()
        db.refresh(category)

        return category

    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        db: Session,
        category_id: UUID,
    ) -> bool:

        category = self.get_by_id(
            db,
            category_id,
        )

        if category is None:
            return False

        db.delete(category)
        db.commit()

        return True


# =====================================================
# Singleton Instance
# =====================================================

category_service = CategoryService()