# backend/src/services/payment_service.py

from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.payment import Payment
from backend.src.schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
)


class PaymentService:
    """
    Service xử lý nghiệp vụ thanh toán.

    Các phương thức:
    - get_all
    - get_by_id
    - create
    - update
    - delete
    """

    # ==========================================================
    # GET ALL
    # ==========================================================

    def get_all(
        self,
        db: Session,
    ) -> list[Payment]:
        return (
            db.query(Payment)
            .order_by(Payment.created_at.desc())
            .all()
        )

    # ==========================================================
    # GET BY ID
    # ==========================================================

    def get_by_id(
        self,
        db: Session,
        payment_id: UUID,
    ) -> Payment | None:
        return (
            db.query(Payment)
            .filter(Payment.id == payment_id)
            .first()
        )

    # ==========================================================
    # CREATE
    # ==========================================================

    def create(
        self,
        db: Session,
        data: PaymentCreate,
    ) -> Payment:
        payload = data.model_dump()

        payment = Payment(**payload)

        try:
            db.add(payment)
            db.commit()
            db.refresh(payment)

            return payment

        except Exception:
            db.rollback()
            raise

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(
        self,
        db: Session,
        payment_id: UUID,
        data: PaymentUpdate,
    ) -> Payment | None:
        payment = self.get_by_id(
            db,
            payment_id,
        )

        if payment is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True,
        )

        for field, value in update_data.items():
            setattr(
                payment,
                field,
                value,
            )

        try:
            db.commit()
            db.refresh(payment)

            return payment

        except Exception:
            db.rollback()
            raise

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete(
        self,
        db: Session,
        payment_id: UUID,
    ) -> bool:
        payment = self.get_by_id(
            db,
            payment_id,
        )

        if payment is None:
            return False

        try:
            db.delete(payment)
            db.commit()

            return True

        except Exception:
            db.rollback()
            raise


payment_service = PaymentService()