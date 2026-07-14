from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.auth import User
from backend.src.models.wallet import Wallet
from backend.src.models.withdrawal import Withdrawal
from backend.src.schemas.withdrawal import (
    WithdrawalApproveRequest,
    WithdrawalCreate,
    WithdrawalRejectRequest,
    WithdrawalStatusUpdate,
    WithdrawalUpdate,
)
from backend.src.services.wallet_transaction_service import (
    wallet_transaction_service,
)


logger = logging.getLogger("AITasker.WithdrawalService")


class WithdrawalService:
    # ======================================================
    # HELPERS
    # ======================================================

    @staticmethod
    def _to_decimal(value) -> Decimal:
        if value is None:
            return Decimal("0.00")

        if isinstance(value, Decimal):
            return value

        return Decimal(str(value))

    @staticmethod
    def _normalize_status(value: str) -> str:
        normalized = str(value or "").strip().upper()

        allowed_statuses = {
            "PENDING",
            "APPROVED",
            "REJECTED",
            "COMPLETED",
            "CANCELLED",
        }

        if normalized not in allowed_statuses:
            raise ValueError(
                "Invalid withdrawal status."
            )

        return normalized

    def _get_wallet(
        self,
        db: Session,
        wallet_id: UUID,
        *,
        for_update: bool = False,
    ) -> Wallet:
        query = (
            db.query(Wallet)
            .filter(Wallet.id == wallet_id)
        )

        if for_update:
            query = query.with_for_update()

        wallet = query.first()

        if wallet is None:
            raise ValueError(
                "Wallet not found."
            )

        return wallet

    def _get_user(
        self,
        db: Session,
        user_id: UUID,
    ) -> User:
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:
            raise ValueError(
                "User not found."
            )

        return user

    def _validate_wallet_owner(
        self,
        wallet: Wallet,
        user_id: UUID,
    ) -> None:
        if wallet.user_id != user_id:
            raise ValueError(
                "Wallet does not belong to this user."
            )

    def _ensure_wallet_active(
        self,
        wallet: Wallet,
    ) -> None:
        wallet_status = str(
            wallet.status or ""
        ).strip().upper()

        if wallet_status != "ACTIVE":
            raise ValueError(
                "Wallet is not active."
            )

    def _snapshot(
        self,
        wallet: Wallet,
    ) -> dict[str, Decimal]:
        return {
            "balance": self._to_decimal(
                wallet.balance
            ),
            "available": self._to_decimal(
                wallet.available_balance
            ),
            "locked": self._to_decimal(
                wallet.locked_balance
            ),
        }

    def _validate_wallet_consistency(
        self,
        wallet: Wallet,
    ) -> None:
        balance = self._to_decimal(
            wallet.balance
        )

        available = self._to_decimal(
            wallet.available_balance
        )

        locked = self._to_decimal(
            wallet.locked_balance
        )

        if balance < Decimal("0"):
            raise ValueError(
                "Wallet balance cannot be negative."
            )

        if available < Decimal("0"):
            raise ValueError(
                "Available balance cannot be negative."
            )

        if locked < Decimal("0"):
            raise ValueError(
                "Locked balance cannot be negative."
            )

        if balance != available + locked:
            raise ValueError(
                "Wallet balance is inconsistent."
            )

    # ======================================================
    # GET ALL
    # ======================================================

    def get_all(
        self,
        db: Session,
    ) -> list[Withdrawal]:
        try:
            return (
                db.query(Withdrawal)
                .order_by(
                    Withdrawal.created_at.desc()
                )
                .all()
            )

        except Exception:
            logger.exception(
                "Không thể lấy danh sách yêu cầu rút tiền."
            )
            raise

    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        db: Session,
        withdrawal_id: UUID,
    ) -> Withdrawal | None:
        try:
            return (
                db.query(Withdrawal)
                .filter(
                    Withdrawal.id
                    == withdrawal_id
                )
                .first()
            )

        except Exception:
            logger.exception(
                "Không thể lấy yêu cầu rút tiền %s.",
                withdrawal_id,
            )
            raise

    # ======================================================
    # GET BY USER
    # ======================================================

    def get_by_user(
        self,
        db: Session,
        user_id: UUID,
    ) -> list[Withdrawal]:
        try:
            return (
                db.query(Withdrawal)
                .filter(
                    Withdrawal.user_id
                    == user_id
                )
                .order_by(
                    Withdrawal.created_at.desc()
                )
                .all()
            )

        except Exception:
            logger.exception(
                "Không thể lấy yêu cầu rút tiền của user %s.",
                user_id,
            )
            raise

    # ======================================================
    # GET BY WALLET
    # ======================================================

    def get_by_wallet(
        self,
        db: Session,
        wallet_id: UUID,
    ) -> list[Withdrawal]:
        try:
            return (
                db.query(Withdrawal)
                .filter(
                    Withdrawal.wallet_id
                    == wallet_id
                )
                .order_by(
                    Withdrawal.created_at.desc()
                )
                .all()
            )

        except Exception:
            logger.exception(
                "Không thể lấy yêu cầu rút tiền của ví %s.",
                wallet_id,
            )
            raise

    # ======================================================
    # CREATE
    # ======================================================

    def create(
        self,
        db: Session,
        data: WithdrawalCreate,
    ) -> Withdrawal:
        try:
            self._get_user(
                db=db,
                user_id=data.user_id,
            )

            wallet = self._get_wallet(
                db=db,
                wallet_id=data.wallet_id,
                for_update=True,
            )

            self._validate_wallet_owner(
                wallet=wallet,
                user_id=data.user_id,
            )

            self._ensure_wallet_active(
                wallet
            )

            amount = self._to_decimal(
                data.amount
            )

            if amount <= Decimal("0"):
                raise ValueError(
                    "Withdrawal amount must be greater than zero."
                )

            available_balance = self._to_decimal(
                wallet.available_balance
            )

            if available_balance < amount:
                raise ValueError(
                    "Insufficient available balance."
                )

            currency = str(
                data.currency or wallet.currency
            ).strip().upper()

            wallet_currency = str(
                wallet.currency or "VND"
            ).strip().upper()

            if currency != wallet_currency:
                raise ValueError(
                    "Withdrawal currency must match wallet currency."
                )

            pending_exists = (
                db.query(Withdrawal)
                .filter(
                    Withdrawal.wallet_id
                    == wallet.id,
                    Withdrawal.status
                    == "PENDING",
                )
                .first()
            )

            if pending_exists is not None:
                raise ValueError(
                    "This wallet already has a pending withdrawal."
                )

            withdrawal = Withdrawal(
                wallet_id=wallet.id,
                user_id=data.user_id,
                amount=amount,
                currency=wallet_currency,
                bank_name=data.bank_name.strip(),
                account_name=data.account_name.strip(),
                account_number=data.account_number.strip(),
                status="PENDING",
                note=(
                    data.note.strip()
                    if data.note
                    else None
                ),
                rejection_reason=None,
                requested_at=datetime.utcnow(),
                processed_at=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db.add(withdrawal)
            db.commit()
            db.refresh(withdrawal)

            logger.info(
                "Withdrawal %s created for wallet %s.",
                withdrawal.id,
                wallet.id,
            )

            return withdrawal

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể tạo yêu cầu rút tiền."
            )

            raise

    # ======================================================
    # UPDATE
    # Chỉ được cập nhật khi còn PENDING.
    # ======================================================

    def update(
        self,
        db: Session,
        withdrawal_id: UUID,
        data: WithdrawalUpdate,
    ) -> Withdrawal | None:
        withdrawal = self.get_by_id(
            db=db,
            withdrawal_id=withdrawal_id,
        )

        if withdrawal is None:
            return None

        try:
            if str(
                withdrawal.status or ""
            ).upper() != "PENDING":
                raise ValueError(
                    "Only pending withdrawals can be updated."
                )

            update_data = data.model_dump(
                exclude_unset=True
            )

            if "amount" in update_data:
                amount = self._to_decimal(
                    update_data["amount"]
                )

                if amount <= Decimal("0"):
                    raise ValueError(
                        "Withdrawal amount must be greater than zero."
                    )

                wallet = self._get_wallet(
                    db=db,
                    wallet_id=withdrawal.wallet_id,
                )

                if (
                    self._to_decimal(
                        wallet.available_balance
                    )
                    < amount
                ):
                    raise ValueError(
                        "Insufficient available balance."
                    )

                update_data["amount"] = amount

            if "currency" in update_data:
                wallet = self._get_wallet(
                    db=db,
                    wallet_id=withdrawal.wallet_id,
                )

                currency = str(
                    update_data["currency"]
                ).strip().upper()

                if currency != str(
                    wallet.currency
                ).strip().upper():
                    raise ValueError(
                        "Withdrawal currency must match wallet currency."
                    )

                update_data["currency"] = currency

            for field_name in (
                "bank_name",
                "account_name",
                "account_number",
                "note",
            ):
                if (
                    field_name in update_data
                    and update_data[field_name]
                    is not None
                ):
                    update_data[field_name] = (
                        update_data[field_name].strip()
                    )

            for field_name, value in update_data.items():
                setattr(
                    withdrawal,
                    field_name,
                    value,
                )

            withdrawal.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(withdrawal)

            return withdrawal

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật yêu cầu rút tiền %s.",
                withdrawal_id,
            )

            raise

    # ======================================================
    # APPROVE
    #
    # Khi duyệt:
    # - Trừ balance
    # - Trừ available_balance
    # - Ghi WalletTransaction WITHDRAW
    # - Chuyển Withdrawal thành APPROVED
    # ======================================================

    def approve(
        self,
        db: Session,
        withdrawal_id: UUID,
        data: WithdrawalApproveRequest,
    ) -> Withdrawal | None:
        try:
            withdrawal = (
                db.query(Withdrawal)
                .filter(
                    Withdrawal.id
                    == withdrawal_id
                )
                .with_for_update()
                .first()
            )

            if withdrawal is None:
                return None

            if str(
                withdrawal.status or ""
            ).upper() != "PENDING":
                raise ValueError(
                    "Only pending withdrawals can be approved."
                )

            wallet = self._get_wallet(
                db=db,
                wallet_id=withdrawal.wallet_id,
                for_update=True,
            )

            self._ensure_wallet_active(
                wallet
            )

            amount = self._to_decimal(
                withdrawal.amount
            )

            before = self._snapshot(
                wallet
            )

            if before["available"] < amount:
                raise ValueError(
                    "Insufficient available balance."
                )

            wallet.balance = (
                before["balance"]
                - amount
            )

            wallet.available_balance = (
                before["available"]
                - amount
            )

            wallet.locked_balance = (
                before["locked"]
            )

            wallet.updated_at = datetime.utcnow()

            self._validate_wallet_consistency(
                wallet
            )

            wallet_transaction_service.record_transaction(
                db=db,
                wallet=wallet,
                transaction_type="WITHDRAW",
                amount=amount,
                balance_before=before["balance"],
                balance_after=self._to_decimal(
                    wallet.balance
                ),
                available_before=before["available"],
                available_after=self._to_decimal(
                    wallet.available_balance
                ),
                locked_before=before["locked"],
                locked_after=self._to_decimal(
                    wallet.locked_balance
                ),
                status="COMPLETED",
                description=(
                    data.note
                    or (
                        f"Rút tiền theo yêu cầu "
                        f"{withdrawal.id}."
                    )
                ),
                reference_type="WITHDRAWAL",
                reference_id=withdrawal.id,
                commit=False,
            )

            withdrawal.status = "APPROVED"
            withdrawal.processed_at = datetime.utcnow()
            withdrawal.updated_at = datetime.utcnow()

            if data.note:
                withdrawal.note = data.note.strip()

            db.commit()
            db.refresh(withdrawal)

            logger.info(
                "Withdrawal %s approved.",
                withdrawal.id,
            )

            return withdrawal

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể duyệt yêu cầu rút tiền %s.",
                withdrawal_id,
            )

            raise

    # ======================================================
    # REJECT
    # ======================================================

    def reject(
        self,
        db: Session,
        withdrawal_id: UUID,
        data: WithdrawalRejectRequest,
    ) -> Withdrawal | None:
        withdrawal = self.get_by_id(
            db=db,
            withdrawal_id=withdrawal_id,
        )

        if withdrawal is None:
            return None

        try:
            if str(
                withdrawal.status or ""
            ).upper() != "PENDING":
                raise ValueError(
                    "Only pending withdrawals can be rejected."
                )

            withdrawal.status = "REJECTED"
            withdrawal.rejection_reason = (
                data.rejection_reason.strip()
            )
            withdrawal.processed_at = datetime.utcnow()
            withdrawal.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(withdrawal)

            logger.info(
                "Withdrawal %s rejected.",
                withdrawal.id,
            )

            return withdrawal

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể từ chối yêu cầu rút tiền %s.",
                withdrawal_id,
            )

            raise

    # ======================================================
    # CANCEL
    # ======================================================

    def cancel(
        self,
        db: Session,
        withdrawal_id: UUID,
    ) -> Withdrawal | None:
        withdrawal = self.get_by_id(
            db=db,
            withdrawal_id=withdrawal_id,
        )

        if withdrawal is None:
            return None

        try:
            if str(
                withdrawal.status or ""
            ).upper() != "PENDING":
                raise ValueError(
                    "Only pending withdrawals can be cancelled."
                )

            withdrawal.status = "CANCELLED"
            withdrawal.processed_at = datetime.utcnow()
            withdrawal.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(withdrawal)

            return withdrawal

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể hủy yêu cầu rút tiền %s.",
                withdrawal_id,
            )

            raise

    # ======================================================
    # COMPLETE
    #
    # Dùng khi Admin xác nhận ngân hàng đã chuyển tiền.
    # Không trừ ví lần nữa vì tiền đã được trừ lúc APPROVED.
    # ======================================================

    def complete(
        self,
        db: Session,
        withdrawal_id: UUID,
    ) -> Withdrawal | None:
        withdrawal = self.get_by_id(
            db=db,
            withdrawal_id=withdrawal_id,
        )

        if withdrawal is None:
            return None

        try:
            if str(
                withdrawal.status or ""
            ).upper() != "APPROVED":
                raise ValueError(
                    "Only approved withdrawals can be completed."
                )

            withdrawal.status = "COMPLETED"
            withdrawal.processed_at = datetime.utcnow()
            withdrawal.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(withdrawal)

            return withdrawal

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể hoàn tất yêu cầu rút tiền %s.",
                withdrawal_id,
            )

            raise

    # ======================================================
    # GENERIC STATUS UPDATE
    # ======================================================

    def update_status(
        self,
        db: Session,
        withdrawal_id: UUID,
        data: WithdrawalStatusUpdate,
    ) -> Withdrawal | None:
        normalized_status = self._normalize_status(
            data.status
        )

        if normalized_status == "APPROVED":
            return self.approve(
                db=db,
                withdrawal_id=withdrawal_id,
                data=WithdrawalApproveRequest(
                    note=None,
                ),
            )

        if normalized_status == "REJECTED":
            return self.reject(
                db=db,
                withdrawal_id=withdrawal_id,
                data=WithdrawalRejectRequest(
                    rejection_reason=(
                        data.rejection_reason
                        or "Withdrawal rejected."
                    ),
                ),
            )

        if normalized_status == "CANCELLED":
            return self.cancel(
                db=db,
                withdrawal_id=withdrawal_id,
            )

        if normalized_status == "COMPLETED":
            return self.complete(
                db=db,
                withdrawal_id=withdrawal_id,
            )

        withdrawal = self.get_by_id(
            db=db,
            withdrawal_id=withdrawal_id,
        )

        if withdrawal is None:
            return None

        if normalized_status != "PENDING":
            raise ValueError(
                "Unsupported withdrawal status transition."
            )

        return withdrawal

    # ======================================================
    # DELETE
    # Chỉ cho phép xóa yêu cầu PENDING/CANCELLED/REJECTED.
    # ======================================================

    def delete(
        self,
        db: Session,
        withdrawal_id: UUID,
    ) -> bool:
        withdrawal = self.get_by_id(
            db=db,
            withdrawal_id=withdrawal_id,
        )

        if withdrawal is None:
            return False

        try:
            current_status = str(
                withdrawal.status or ""
            ).upper()

            if current_status in {
                "APPROVED",
                "COMPLETED",
            }:
                raise ValueError(
                    "Approved or completed withdrawal cannot be deleted."
                )

            db.delete(withdrawal)
            db.commit()

            return True

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể xóa yêu cầu rút tiền %s.",
                withdrawal_id,
            )

            raise


withdrawal_service = WithdrawalService()