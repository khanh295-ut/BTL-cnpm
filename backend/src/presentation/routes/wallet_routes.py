from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.wallet import (
    WalletAmountRequest,
    WalletCreate,
    WalletResponse,
    WalletTransferRequest,
    WalletUpdate,
)
from backend.src.services.wallet_service import wallet_service


router = APIRouter(
    tags=["Wallets"],
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[WalletResponse],
)
def get_all_wallets(
    db: Session = Depends(get_db),
):
    return wallet_service.get_all(db)


# ==========================================================
# GET BY USER
#
# Route tĩnh phải đặt trước "/{wallet_id}" để tránh FastAPI
# hiểu "user" là wallet_id.
# ==========================================================

@router.get(
    "/user/{user_id}",
    response_model=WalletResponse,
)
def get_wallet_by_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    wallet = wallet_service.get_by_user(
        db=db,
        user_id=user_id,
    )

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found.",
        )

    return wallet


# ==========================================================
# TRANSFER
#
# Phải đặt trước "/{wallet_id}" để tránh xung đột route.
# ==========================================================

@router.post(
    "/transfer",
)
def transfer_money(
    data: WalletTransferRequest,
    db: Session = Depends(get_db),
):
    try:
        result = wallet_service.transfer(
            db=db,
            data=data,
        )

        return {
            "message": "Transfer completed successfully.",
            "amount": result["amount"],
            "sender": WalletResponse.model_validate(
                result["sender"]
            ),
            "receiver": WalletResponse.model_validate(
                result["receiver"]
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{wallet_id}",
    response_model=WalletResponse,
)
def get_wallet(
    wallet_id: UUID,
    db: Session = Depends(get_db),
):
    wallet = wallet_service.get_by_id(
        db=db,
        wallet_id=wallet_id,
    )

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found.",
        )

    return wallet


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "",
    response_model=WalletResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_wallet(
    data: WalletCreate,
    db: Session = Depends(get_db),
):
    try:
        return wallet_service.create(
            db=db,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# UPDATE
# ==========================================================

@router.put(
    "/{wallet_id}",
    response_model=WalletResponse,
)
def update_wallet(
    wallet_id: UUID,
    data: WalletUpdate,
    db: Session = Depends(get_db),
):
    wallet = wallet_service.update(
        db=db,
        wallet_id=wallet_id,
        data=data,
    )

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found.",
        )

    return wallet


# ==========================================================
# DEPOSIT
# ==========================================================

@router.patch(
    "/{wallet_id}/deposit",
    response_model=WalletResponse,
)
def deposit_money(
    wallet_id: UUID,
    data: WalletAmountRequest,
    db: Session = Depends(get_db),
):
    try:
        return wallet_service.deposit(
            db=db,
            wallet_id=wallet_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# WITHDRAW
# ==========================================================

@router.patch(
    "/{wallet_id}/withdraw",
    response_model=WalletResponse,
)
def withdraw_money(
    wallet_id: UUID,
    data: WalletAmountRequest,
    db: Session = Depends(get_db),
):
    try:
        return wallet_service.withdraw(
            db=db,
            wallet_id=wallet_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# LOCK BALANCE
# ==========================================================

@router.patch(
    "/{wallet_id}/lock",
    response_model=WalletResponse,
)
def lock_wallet_balance(
    wallet_id: UUID,
    data: WalletAmountRequest,
    db: Session = Depends(get_db),
):
    try:
        return wallet_service.lock_balance(
            db=db,
            wallet_id=wallet_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# RELEASE LOCKED BALANCE
# ==========================================================

@router.patch(
    "/{wallet_id}/release",
    response_model=WalletResponse,
)
def release_wallet_balance(
    wallet_id: UUID,
    data: WalletAmountRequest,
    db: Session = Depends(get_db),
):
    try:
        return wallet_service.release_balance(
            db=db,
            wallet_id=wallet_id,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{wallet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_wallet(
    wallet_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        deleted = wallet_service.delete(
            db=db,
            wallet_id=wallet_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found.",
            )

        return None

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc