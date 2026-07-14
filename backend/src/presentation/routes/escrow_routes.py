from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.escrow import (
    EscrowCreate,
    EscrowFundRequest,
    EscrowRefundRequest,
    EscrowReleaseRequest,
    EscrowResponse,
    EscrowStatusUpdate,
    EscrowSummaryResponse,
    EscrowUpdate,
)
from backend.src.services.escrow_service import (
    escrow_service,
)


router = APIRouter(
    tags=["Escrows"],
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[EscrowResponse],
)
def get_all_escrows(
    db: Session = Depends(get_db),
):
    return escrow_service.get_all(db)


# ==========================================================
# SUMMARY
#
# Route tĩnh phải đặt trước "/{escrow_id}" để tránh xung đột.
# ==========================================================

@router.get(
    "/summary",
    response_model=EscrowSummaryResponse,
)
def get_escrow_summary(
    db: Session = Depends(get_db),
):
    return escrow_service.summary(db)


# ==========================================================
# GET BY CONTRACT
# ==========================================================

@router.get(
    "/contract/{contract_id}",
    response_model=EscrowResponse,
)
def get_escrow_by_contract(
    contract_id: UUID,
    db: Session = Depends(get_db),
):
    escrow = escrow_service.get_by_contract(
        db=db,
        contract_id=contract_id,
    )

    if escrow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escrow not found.",
        )

    return escrow


# ==========================================================
# GET BY PAYMENT
# ==========================================================

@router.get(
    "/payment/{payment_id}",
    response_model=EscrowResponse,
)
def get_escrow_by_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
):
    escrow = escrow_service.get_by_payment(
        db=db,
        payment_id=payment_id,
    )

    if escrow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escrow not found.",
        )

    return escrow


# ==========================================================
# GET BY WALLET
# ==========================================================

@router.get(
    "/wallet/{wallet_id}",
    response_model=list[EscrowResponse],
)
def get_escrows_by_wallet(
    wallet_id: UUID,
    db: Session = Depends(get_db),
):
    return escrow_service.get_by_wallet(
        db=db,
        wallet_id=wallet_id,
    )


# ==========================================================
# GET BY STATUS
# ==========================================================

@router.get(
    "/status/{status_value}",
    response_model=list[EscrowResponse],
)
def get_escrows_by_status(
    status_value: str,
    db: Session = Depends(get_db),
):
    return escrow_service.get_by_status(
        db=db,
        status=status_value,
    )


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "",
    response_model=EscrowResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_escrow(
    data: EscrowCreate,
    db: Session = Depends(get_db),
):
    try:
        return escrow_service.create(
            db=db,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{escrow_id}",
    response_model=EscrowResponse,
)
def get_escrow(
    escrow_id: UUID,
    db: Session = Depends(get_db),
):
    escrow = escrow_service.get_by_id(
        db=db,
        escrow_id=escrow_id,
    )

    if escrow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Escrow not found.",
        )

    return escrow


# ==========================================================
# UPDATE
# Chỉ cho phép cập nhật khi Escrow còn PENDING.
# ==========================================================

@router.put(
    "/{escrow_id}",
    response_model=EscrowResponse,
)
def update_escrow(
    escrow_id: UUID,
    data: EscrowUpdate,
    db: Session = Depends(get_db),
):
    try:
        escrow = escrow_service.update(
            db=db,
            escrow_id=escrow_id,
            data=data,
        )

        if escrow is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Escrow not found.",
            )

        return escrow

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# FUND
# Doanh nghiệp chuyển tiền từ available_balance sang
# locked_balance để giữ tiền trong Escrow.
# ==========================================================

@router.patch(
    "/{escrow_id}/fund",
    response_model=EscrowResponse,
)
def fund_escrow(
    escrow_id: UUID,
    data: EscrowFundRequest,
    db: Session = Depends(get_db),
):
    try:
        return escrow_service.fund(
            db=db,
            escrow_id=escrow_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# RELEASE PARTIAL
# Giải ngân một phần cho ví chuyên gia.
# ==========================================================

@router.patch(
    "/{escrow_id}/release",
    response_model=EscrowResponse,
)
def release_escrow(
    escrow_id: UUID,
    data: EscrowReleaseRequest,
    db: Session = Depends(get_db),
):
    try:
        return escrow_service.release(
            db=db,
            escrow_id=escrow_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# RELEASE ALL
# Giải ngân toàn bộ số tiền còn lại.
# ==========================================================

@router.patch(
    "/{escrow_id}/release-all",
    response_model=EscrowResponse,
)
def release_all_escrow(
    escrow_id: UUID,
    note: str | None = Query(
        default=None,
        max_length=5000,
    ),
    db: Session = Depends(get_db),
):
    try:
        return escrow_service.release_all(
            db=db,
            escrow_id=escrow_id,
            note=note,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# REFUND PARTIAL
# Hoàn một phần số tiền còn lại cho doanh nghiệp.
# ==========================================================

@router.patch(
    "/{escrow_id}/refund",
    response_model=EscrowResponse,
)
def refund_escrow(
    escrow_id: UUID,
    data: EscrowRefundRequest,
    db: Session = Depends(get_db),
):
    try:
        return escrow_service.refund(
            db=db,
            escrow_id=escrow_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# REFUND ALL
# Hoàn toàn bộ số tiền còn lại cho doanh nghiệp.
# ==========================================================

@router.patch(
    "/{escrow_id}/refund-all",
    response_model=EscrowResponse,
)
def refund_all_escrow(
    escrow_id: UUID,
    note: str | None = Query(
        default=None,
        max_length=5000,
    ),
    db: Session = Depends(get_db),
):
    try:
        return escrow_service.refund_all(
            db=db,
            escrow_id=escrow_id,
            note=note,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# UPDATE STATUS
# Chủ yếu dùng cho DISPUTED hoặc CANCELLED.
# Không dùng endpoint này để RELEASE hoặc REFUND tiền.
# ==========================================================

@router.patch(
    "/{escrow_id}/status",
    response_model=EscrowResponse,
)
def update_escrow_status(
    escrow_id: UUID,
    data: EscrowStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        return escrow_service.update_status(
            db=db,
            escrow_id=escrow_id,
            status=data.status,
            note=data.note,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# DELETE
# Chỉ cho phép xóa PENDING hoặc CANCELLED.
# ==========================================================

@router.delete(
    "/{escrow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_escrow(
    escrow_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        deleted = escrow_service.delete(
            db=db,
            escrow_id=escrow_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Escrow not found.",
            )

        return None

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc