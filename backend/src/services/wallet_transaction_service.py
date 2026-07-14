from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.wallet import Wallet
from backend.src.models.wallet_transaction import WalletTransaction
from backend.src.schemas.wallet_transaction import (
    WalletTransactionCreate,
    WalletTransactionFilter,
    WalletTransactionUpdate,
)


logger = logging.getLogger(
    "AITasker.WalletTransactionService"
)


class WalletTransactionService:
    # ======================================================
    # GET ALL
    # ======================================================

    def get_all(
        self,
        db: Session,
    ) -> list[WalletTransaction]:
        try:
            return (
                db.query(WalletTransaction)
                .order_by(
                    WalletTransaction.created_at.desc()
                )
                .all()
            )

        except Exception:
            logger.exception(
                "Không thể lấy danh sách giao dịch ví."
            )
            raise

    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        db: Session,
        transaction_id: UUID,
    ) -> WalletTransaction | None:
        try:
            return (
                db.query(WalletTransaction)
                .filter(
                    WalletTransaction.id
                    == transaction_id
                )
                .first()
            )

        except Exception:
            logger.exception(
                "Không thể lấy giao dịch ví %s.",
                transaction_id,
            )
            raise

    # ======================================================
    # GET BY WALLET
    # ======================================================

    def get_by_wallet(
        self,
        db: Session,
        wallet_id: UUID,
    ) -> list[WalletTransaction]:
        try:
            return (
                db.query(WalletTransaction)
                .filter(
                    WalletTransaction.wallet_id
                    == wallet_id
                )
                .order_by(
                    WalletTransaction.created_at.desc()
                )
                .all()
            )

        except Exception:
            logger.exception(
                "Không thể lấy lịch sử giao dịch của ví %s.",
                wallet_id,
            )
            raise

    # ======================================================
    # GET BY USER
    # ======================================================

    def get_by_user(
        self,
        db: Session,
        user_id: UUID,
    ) -> list[WalletTransaction]:
        try:
            return (
                db.query(WalletTransaction)
                .join(
                    Wallet,
                    Wallet.id
                    == WalletTransaction.wallet_id,
                )
                .filter(
                    Wallet.user_id == user_id
                )
                .order_by(
                    WalletTransaction.created_at.desc()
                )
                .all()
            )

        except Exception:
            logger.exception(
                "Không thể lấy lịch sử giao dịch của user %s.",
                user_id,
            )
            raise

    # ======================================================
    # FILTER TRANSACTIONS
    # ======================================================

    def filter_transactions(
        self,
        db: Session,
        filters: WalletTransactionFilter,
        wallet_id: UUID | None = None,
    ) -> list[WalletTransaction]:
        try:
            query = db.query(WalletTransaction)

            if wallet_id is not None:
                query = query.filter(
                    WalletTransaction.wallet_id
                    == wallet_id
                )

            if filters.transaction_type:
                query = query.filter(
                    WalletTransaction.transaction_type
                    == filters.transaction_type
                    .strip()
                    .upper()
                )

            if filters.status:
                query = query.filter(
                    WalletTransaction.status
                    == filters.status.strip().upper()
                )

            if filters.from_date:
                query = query.filter(
                    WalletTransaction.created_at
                    >= filters.from_date
                )

            if filters.to_date:
                query = query.filter(
                    WalletTransaction.created_at
                    <= filters.to_date
                )

            return (
                query.order_by(
                    WalletTransaction.created_at.desc()
                )
                .all()
            )

        except Exception:
            logger.exception(
                "Không thể lọc lịch sử giao dịch ví."
            )
            raise

    # ======================================================
    # VALIDATE WALLET
    # ======================================================

    def _get_wallet(
        self,
        db: Session,
        wallet_id: UUID,
    ) -> Wallet:
        wallet = (
            db.query(Wallet)
            .filter(Wallet.id == wallet_id)
            .first()
        )

        if wallet is None:
            raise ValueError(
                "Wallet not found."
            )

        return wallet

    # ======================================================
    # NORMALIZE TRANSACTION TYPE
    # ======================================================

    def _normalize_transaction_type(
        self,
        transaction_type: str,
    ) -> str:
        normalized = str(
            transaction_type or ""
        ).strip().upper()

        allowed_types = {
            "DEPOSIT",
            "WITHDRAW",
            "LOCK",
            "UNLOCK",
            "RELEASE",
            "TRANSFER_IN",
            "TRANSFER_OUT",
            "PAYMENT",
            "REFUND",
            "ESCROW_HOLD",
            "ESCROW_RELEASE",
        }

        if normalized not in allowed_types:
            raise ValueError(
                "Invalid wallet transaction type."
            )

        return normalized

    # ======================================================
    # CREATE MANUALLY
    # ======================================================

    def create(
        self,
        db: Session,
        data: WalletTransactionCreate,
    ) -> WalletTransaction:
        """
        Tạo bản ghi lịch sử giao dịch thủ công.

        Hàm này không tự thay đổi số dư Wallet.
        Việc thay đổi số dư phải được thực hiện trong
        wallet_service.py trước khi gọi record_transaction().
        """

        try:
            wallet = self._get_wallet(
                db=db,
                wallet_id=data.wallet_id,
            )

            transaction_type = (
                self._normalize_transaction_type(
                    data.transaction_type
                )
            )

            current_balance = Decimal(
                wallet.balance or 0
            )

            current_available = Decimal(
                wallet.available_balance or 0
            )

            current_locked = Decimal(
                wallet.locked_balance or 0
            )

            transaction = WalletTransaction(
                wallet_id=wallet.id,
                transaction_type=transaction_type,
                amount=data.amount,
                balance_before=current_balance,
                balance_after=current_balance,
                available_before=current_available,
                available_after=current_available,
                locked_before=current_locked,
                locked_after=current_locked,
                currency=wallet.currency,
                status="COMPLETED",
                description=(
                    data.description.strip()
                    if data.description
                    else None
                ),
                reference_type=(
                    data.reference_type.strip().upper()
                    if data.reference_type
                    else None
                ),
                reference_id=data.reference_id,
                created_at=datetime.utcnow(),
            )

            db.add(transaction)
            db.commit()
            db.refresh(transaction)

            return transaction

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể tạo giao dịch ví."
            )

            raise

    # ======================================================
    # RECORD TRANSACTION
    # ======================================================

    def record_transaction(
        self,
        db: Session,
        *,
        wallet: Wallet,
        transaction_type: str,
        amount: Decimal,
        balance_before: Decimal,
        balance_after: Decimal,
        available_before: Decimal,
        available_after: Decimal,
        locked_before: Decimal,
        locked_after: Decimal,
        status: str = "COMPLETED",
        description: str | None = None,
        reference_type: str | None = None,
        reference_id: UUID | None = None,
        commit: bool = False,
    ) -> WalletTransaction:
        """
        Ghi lịch sử giao dịch sau khi số dư ví thay đổi.

        Mặc định commit=False để Wallet và Transaction
        có thể nằm trong cùng một database transaction.
        """

        normalized_type = (
            self._normalize_transaction_type(
                transaction_type
            )
        )

        normalized_status = str(
            status or "COMPLETED"
        ).strip().upper()

        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type=normalized_type,
            amount=Decimal(amount),
            balance_before=Decimal(
                balance_before
            ),
            balance_after=Decimal(
                balance_after
            ),
            available_before=Decimal(
                available_before
            ),
            available_after=Decimal(
                available_after
            ),
            locked_before=Decimal(
                locked_before
            ),
            locked_after=Decimal(
                locked_after
            ),
            currency=wallet.currency,
            status=normalized_status,
            description=(
                description.strip()
                if description
                else None
            ),
            reference_type=(
                reference_type.strip().upper()
                if reference_type
                else None
            ),
            reference_id=reference_id,
            created_at=datetime.utcnow(),
        )

        db.add(transaction)

        if commit:
            db.commit()
            db.refresh(transaction)

        return transaction

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        db: Session,
        transaction_id: UUID,
        data: WalletTransactionUpdate,
    ) -> WalletTransaction | None:
        transaction = self.get_by_id(
            db=db,
            transaction_id=transaction_id,
        )

        if transaction is None:
            return None

        try:
            update_data = data.model_dump(
                exclude_unset=True
            )

            if (
                "description" in update_data
                and update_data["description"]
                is not None
            ):
                update_data["description"] = (
                    update_data["description"].strip()
                )

            if (
                "status" in update_data
                and update_data["status"]
                is not None
            ):
                update_data["status"] = (
                    update_data["status"]
                    .strip()
                    .upper()
                )

            for field_name, value in update_data.items():
                setattr(
                    transaction,
                    field_name,
                    value,
                )

            db.commit()
            db.refresh(transaction)

            return transaction

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật giao dịch ví %s.",
                transaction_id,
            )

            raise

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        db: Session,
        transaction_id: UUID,
    ) -> bool:
        transaction = self.get_by_id(
            db=db,
            transaction_id=transaction_id,
        )

        if transaction is None:
            return False

        try:
            if (
                str(transaction.status).upper()
                == "COMPLETED"
            ):
                raise ValueError(
                    "Completed wallet transaction cannot be deleted."
                )

            db.delete(transaction)
            db.commit()

            return True

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể xóa giao dịch ví %s.",
                transaction_id,
            )

            raise


wallet_transaction_service = (
    WalletTransactionService()
)