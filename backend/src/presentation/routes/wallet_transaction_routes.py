from datetime import datetime
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
from backend.src.schemas.wallet_transaction import (
    WalletTransactionCreate,
    WalletTransactionFilter,
    WalletTransactionResponse,
    WalletTransactionUpdate,
)
from backend.src.services.wallet_transaction_service import (
    wallet_transaction_service,
)


router = APIRouter(
    tags=["Wallet Transactions"],
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[WalletTransactionResponse],
)
def get_all_wallet_transactions(
    db: Session = Depends(get_db),
):
    return wallet_transaction_service.get_all(db)


# ==========================================================
# FILTER TRANSACTIONS
#
# Route tĩnh phải đặt trước "/{transaction_id}"
# để tránh FastAPI hiểu "filter" là UUID.
# ==========================================================

@router.get(
    "/filter",
    response_model=list[WalletTransactionResponse],
)
def filter_wallet_transactions(
    wallet_id: UUID | None = Query(
        default=None,
        description="Lọc theo wallet_id",
    ),
    transaction_type: str | None = Query(
        default=None,
        description="DEPOSIT, WITHDRAW, LOCK, RELEASE...",
    ),
    transaction_status: str | None = Query(
        default=None,
        alias="status",
        description="COMPLETED, PENDING, FAILED...",
    ),
    from_date: datetime | None = Query(
        default=None,
    ),
    to_date: datetime | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
):
    filters = WalletTransactionFilter(
        transaction_type=transaction_type,
        status=transaction_status,
        from_date=from_date,
        to_date=to_date,
    )

    return wallet_transaction_service.filter_transactions(
        db=db,
        filters=filters,
        wallet_id=wallet_id,
    )


# ==========================================================
# GET BY WALLET
# ==========================================================

@router.get(
    "/wallet/{wallet_id}",
    response_model=list[WalletTransactionResponse],
)
def get_transactions_by_wallet(
    wallet_id: UUID,
    db: Session = Depends(get_db),
):
    return wallet_transaction_service.get_by_wallet(
        db=db,
        wallet_id=wallet_id,
    )


# ==========================================================
# GET BY USER
# ==========================================================

@router.get(
    "/user/{user_id}",
    response_model=list[WalletTransactionResponse],
)
def get_transactions_by_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    return wallet_transaction_service.get_by_user(
        db=db,
        user_id=user_id,
    )


# ==========================================================
# CREATE MANUALLY
#
# Lưu ý:
# Endpoint này chỉ tạo lịch sử giao dịch,
# không tự thay đổi số dư Wallet.
# ==========================================================

@router.post(
    "",
    response_model=WalletTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_wallet_transaction(
    data: WalletTransactionCreate,
    db: Session = Depends(get_db),
):
    try:
        return wallet_transaction_service.create(
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
    "/{transaction_id}",
    response_model=WalletTransactionResponse,
)
def get_wallet_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
):
    transaction = wallet_transaction_service.get_by_id(
        db=db,
        transaction_id=transaction_id,
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet transaction not found.",
        )

    return transaction


# ==========================================================
# UPDATE
# ==========================================================

@router.put(
    "/{transaction_id}",
    response_model=WalletTransactionResponse,
)
def update_wallet_transaction(
    transaction_id: UUID,
    data: WalletTransactionUpdate,
    db: Session = Depends(get_db),
):
    try:
        transaction = wallet_transaction_service.update(
            db=db,
            transaction_id=transaction_id,
            data=data,
        )

        if transaction is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet transaction not found.",
            )

        return transaction

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_wallet_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        deleted = wallet_transaction_service.delete(
            db=db,
            transaction_id=transaction_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet transaction not found.",
            )

        return None

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc