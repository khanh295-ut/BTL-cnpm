from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.withdrawal import (
    WithdrawalApproveRequest,
    WithdrawalCreate,
    WithdrawalRejectRequest,
    WithdrawalResponse,
    WithdrawalStatusUpdate,
    WithdrawalUpdate,
)
from backend.src.services.withdrawal_service import (
    withdrawal_service,
)


router = APIRouter(
    tags=["Withdrawals"],
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[WithdrawalResponse],
)
def get_all_withdrawals(
    db: Session = Depends(get_db),
):
    return withdrawal_service.get_all(db)


# ==========================================================
# GET BY USER
#
# Route tĩnh phải đặt trước "/{withdrawal_id}".
# ==========================================================

@router.get(
    "/user/{user_id}",
    response_model=list[WithdrawalResponse],
)
def get_withdrawals_by_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    return withdrawal_service.get_by_user(
        db=db,
        user_id=user_id,
    )


# ==========================================================
# GET BY WALLET
# ==========================================================

@router.get(
    "/wallet/{wallet_id}",
    response_model=list[WithdrawalResponse],
)
def get_withdrawals_by_wallet(
    wallet_id: UUID,
    db: Session = Depends(get_db),
):
    return withdrawal_service.get_by_wallet(
        db=db,
        wallet_id=wallet_id,
    )


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "",
    response_model=WithdrawalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_withdrawal(
    data: WithdrawalCreate,
    db: Session = Depends(get_db),
):
    try:
        return withdrawal_service.create(
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
    "/{withdrawal_id}",
    response_model=WithdrawalResponse,
)
def get_withdrawal(
    withdrawal_id: UUID,
    db: Session = Depends(get_db),
):
    withdrawal = withdrawal_service.get_by_id(
        db=db,
        withdrawal_id=withdrawal_id,
    )

    if withdrawal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Withdrawal not found.",
        )

    return withdrawal


# ==========================================================
# UPDATE
# Chỉ áp dụng khi Withdrawal còn PENDING.
# ==========================================================

@router.put(
    "/{withdrawal_id}",
    response_model=WithdrawalResponse,
)
def update_withdrawal(
    withdrawal_id: UUID,
    data: WithdrawalUpdate,
    db: Session = Depends(get_db),
):
    try:
        withdrawal = withdrawal_service.update(
            db=db,
            withdrawal_id=withdrawal_id,
            data=data,
        )

        if withdrawal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Withdrawal not found.",
            )

        return withdrawal

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# APPROVE
# Admin duyệt yêu cầu rút tiền.
# Tiền được trừ khỏi Wallet tại bước này.
# ==========================================================

@router.patch(
    "/{withdrawal_id}/approve",
    response_model=WithdrawalResponse,
)
def approve_withdrawal(
    withdrawal_id: UUID,
    data: WithdrawalApproveRequest,
    db: Session = Depends(get_db),
):
    try:
        withdrawal = withdrawal_service.approve(
            db=db,
            withdrawal_id=withdrawal_id,
            data=data,
        )

        if withdrawal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Withdrawal not found.",
            )

        return withdrawal

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# REJECT
# ==========================================================

@router.patch(
    "/{withdrawal_id}/reject",
    response_model=WithdrawalResponse,
)
def reject_withdrawal(
    withdrawal_id: UUID,
    data: WithdrawalRejectRequest,
    db: Session = Depends(get_db),
):
    try:
        withdrawal = withdrawal_service.reject(
            db=db,
            withdrawal_id=withdrawal_id,
            data=data,
        )

        if withdrawal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Withdrawal not found.",
            )

        return withdrawal

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# CANCEL
# User hủy yêu cầu khi vẫn còn PENDING.
# ==========================================================

@router.patch(
    "/{withdrawal_id}/cancel",
    response_model=WithdrawalResponse,
)
def cancel_withdrawal(
    withdrawal_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        withdrawal = withdrawal_service.cancel(
            db=db,
            withdrawal_id=withdrawal_id,
        )

        if withdrawal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Withdrawal not found.",
            )

        return withdrawal

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# COMPLETE
# Admin xác nhận ngân hàng đã chuyển tiền thành công.
# Không trừ ví lần thứ hai.
# ==========================================================

@router.patch(
    "/{withdrawal_id}/complete",
    response_model=WithdrawalResponse,
)
def complete_withdrawal(
    withdrawal_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        withdrawal = withdrawal_service.complete(
            db=db,
            withdrawal_id=withdrawal_id,
        )

        if withdrawal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Withdrawal not found.",
            )

        return withdrawal

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# GENERIC STATUS UPDATE
# Có thể dùng khi frontend muốn một endpoint trạng thái chung.
# ==========================================================

@router.patch(
    "/{withdrawal_id}/status",
    response_model=WithdrawalResponse,
)
def update_withdrawal_status(
    withdrawal_id: UUID,
    data: WithdrawalStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        withdrawal = withdrawal_service.update_status(
            db=db,
            withdrawal_id=withdrawal_id,
            data=data,
        )

        if withdrawal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Withdrawal not found.",
            )

        return withdrawal

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# DELETE
# Không cho xóa yêu cầu APPROVED hoặc COMPLETED.
# ==========================================================

@router.delete(
    "/{withdrawal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_withdrawal(
    withdrawal_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        deleted = withdrawal_service.delete(
            db=db,
            withdrawal_id=withdrawal_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Withdrawal not found.",
            )

        return None

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc