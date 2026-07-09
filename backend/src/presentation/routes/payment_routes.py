# backend/src/presentation/routes/payment_routes.py

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
# Nếu bạn đã có schemas/payment.py và services/payment_service.py, import tương ứng
# Nếu chưa có, bạn có thể tạo schema/service hoặc trả mock data tạm thời
try:
    from backend.src.schemas.payment import PaymentResponse, PaymentCreate
except Exception:
    # fallback minimal Pydantic models nếu chưa có file schemas
    from pydantic import BaseModel
    class PaymentResponse(BaseModel):
        id: UUID | None = None
        amount: float | None = 0
        currency: str | None = "VND"
        status: str | None = "PENDING"

    class PaymentCreate(BaseModel):
        amount: float
        currency: str | None = "VND"
        metadata: dict | None = None

try:
    from backend.src.services.payment_service import payment_service
except Exception:
    # fallback service stub nếu chưa có service thực thi
    class _StubService:
        def get_all(self, db):
            return []
        def get_by_id(self, db, payment_id):
            return None
        def create(self, db, data):
            return {"id": None, "amount": data.amount, "currency": data.currency, "status": "PENDING"}

    payment_service = _StubService()

router = APIRouter(
    prefix="/api/payments",
    tags=["Payments"],
)

@router.get("", response_model=list[PaymentResponse])
def get_all_payments(db: Session = Depends(get_db)):
    return payment_service.get_all(db)

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: UUID, db: Session = Depends(get_db)):
    payment = payment_service.get_by_id(db, payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return payment

@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(data: PaymentCreate, db: Session = Depends(get_db)):
    return payment_service.create(db, data)
