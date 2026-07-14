# backend/src/presentation/routes/payment_routes.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.payment import (
    PaymentCreate,
    PaymentResponse,
    PaymentUpdate,
)
from backend.src.services.payment_service import payment_service


# ==========================================================
# ROUTER
# Prefix /payments đã được thêm trong all_routes.py.
# Prefix /api đã được thêm trong app.py.
# ==========================================================

router = APIRouter(
    tags=["Payments"],
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[PaymentResponse],
)
def get_all_payments(
    db: Session = Depends(get_db),
):
    return payment_service.get_all(db)


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
):
    payment = payment_service.get_by_id(
        db,
        payment_id,
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
):
    return payment_service.create(
        db,
        data,
    )


# ==========================================================
# UPDATE
# ==========================================================

@router.put(
    "/{payment_id}",
    response_model=PaymentResponse,
)
def update_payment(
    payment_id: UUID,
    data: PaymentUpdate,
    db: Session = Depends(get_db),
):
    payment = payment_service.update(
        db,
        payment_id,
        data,
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = payment_service.delete(
        db,
        payment_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return None