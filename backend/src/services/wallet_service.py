# backend/src/services/wallet_service.py

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.auth import User
from backend.src.models.wallet import Wallet
from backend.src.schemas.wallet import (
    WalletAmountRequest,
    WalletCreate,
    WalletTransferRequest,
    WalletUpdate,
)
from backend.src.services.wallet_transaction_service import (
    wallet_transaction_service,
)


logger = logging.getLogger("AITasker.WalletService")


class WalletService:
    # ======================================================
    # HELPERS
    # ======================================================

    @staticmethod
    def _to_decimal(value) -> Decimal:
        """
        Chuyển giá trị từ PostgreSQL/SQLAlchemy sang Decimal an toàn.
        """
        if value is None:
            return Decimal("0.00")

        if isinstance(value, Decimal):
            return value

        return Decimal(str(value))

    @staticmethod
    def _normalize_currency(value: str) -> str:
        currency = str(value or "VND").strip().upper()

        if not currency:
            return "VND"

        return currency

    @staticmethod
    def _normalize_status(value: str) -> str:
        normalized = str(value or "ACTIVE").strip().upper()

        allowed_statuses = {
            "ACTIVE",
            "SUSPENDED",
            "LOCKED",
            "CLOSED",
        }

        if normalized not in allowed_statuses:
            raise ValueError(
                "Invalid wallet status. "
                "Allowed values: ACTIVE, SUSPENDED, LOCKED, CLOSED."
            )

        return normalized

    def _ensure_wallet_active(
        self,
        wallet: Wallet,
    ) -> None:
        """
        Chỉ ví ACTIVE mới được thực hiện giao dịch.
        """
        wallet_status = str(
            wallet.status or ""
        ).strip().upper()

        if wallet_status != "ACTIVE":
            raise ValueError(
                f"Wallet is not active. Current status: {wallet_status}."
            )

    def _snapshot(
        self,
        wallet: Wallet,
    ) -> dict[str, Decimal]:
        """
        Chụp số dư trước hoặc sau giao dịch.
        """
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

    def _validate_balance_consistency(
        self,
        wallet: Wallet,
    ) -> None:
        """
        Bảo đảm:

        balance = available_balance + locked_balance
        """

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
                "Wallet balance is inconsistent: "
                "balance must equal "
                "available_balance + locked_balance."
            )

    def _record_transaction(
        self,
        db: Session,
        *,
        wallet: Wallet,
        transaction_type: str,
        amount: Decimal,
        before: dict[str, Decimal],
        description: str | None = None,
        reference_type: str | None = None,
        reference_id: UUID | None = None,
    ):
        """
        Lưu WalletTransaction nhưng chưa commit.

        Commit sẽ được thực hiện bởi hàm nghiệp vụ bên ngoài,
        giúp Wallet và WalletTransaction cùng rollback nếu lỗi.
        """

        after = self._snapshot(wallet)

        return wallet_transaction_service.record_transaction(
            db=db,
            wallet=wallet,
            transaction_type=transaction_type,
            amount=self._to_decimal(amount),
            balance_before=before["balance"],
            balance_after=after["balance"],
            available_before=before["available"],
            available_after=after["available"],
            locked_before=before["locked"],
            locked_after=after["locked"],
            status="COMPLETED",
            description=description,
            reference_type=reference_type,
            reference_id=reference_id,
            commit=False,
        )

    # ======================================================
    # GET ALL
    # ======================================================

    def get_all(
        self,
        db: Session,
    ) -> list[Wallet]:
        try:
            return (
                db.query(Wallet)
                .order_by(
                    Wallet.created_at.desc()
                )
                .all()
            )

        except Exception:
            logger.exception(
                "Không thể lấy danh sách ví."
            )
            raise

    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        db: Session,
        wallet_id: UUID,
    ) -> Wallet | None:
        try:
            return (
                db.query(Wallet)
                .filter(
                    Wallet.id == wallet_id
                )
                .first()
            )

        except Exception:
            logger.exception(
                "Không thể lấy ví %s.",
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
    ) -> Wallet | None:
        try:
            return (
                db.query(Wallet)
                .filter(
                    Wallet.user_id == user_id
                )
                .first()
            )

        except Exception:
            logger.exception(
                "Không thể lấy ví của user %s.",
                user_id,
            )
            raise

    # ======================================================
    # CREATE
    # ======================================================

    def create(
        self,
        db: Session,
        data: WalletCreate,
    ) -> Wallet:
        try:
            user = (
                db.query(User)
                .filter(
                    User.id == data.user_id
                )
                .first()
            )

            if user is None:
                raise ValueError(
                    "User not found."
                )

            existing_wallet = self.get_by_user(
                db=db,
                user_id=data.user_id,
            )

            if existing_wallet is not None:
                raise ValueError(
                    "Wallet already exists for this user."
                )

            wallet = Wallet(
                user_id=data.user_id,
                balance=self._to_decimal(
                    data.balance
                ),
                available_balance=self._to_decimal(
                    data.available_balance
                ),
                locked_balance=self._to_decimal(
                    data.locked_balance
                ),
                currency=self._normalize_currency(
                    data.currency
                ),
                status=self._normalize_status(
                    data.status
                ),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self._validate_balance_consistency(
                wallet
            )

            db.add(wallet)
            db.commit()
            db.refresh(wallet)

            logger.info(
                "Wallet %s created for user %s.",
                wallet.id,
                wallet.user_id,
            )

            return wallet

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể tạo ví."
            )

            raise

    # ======================================================
    # UPDATE
    # Chỉ cập nhật currency/status, không cập nhật số dư.
    # ======================================================

    def update(
        self,
        db: Session,
        wallet_id: UUID,
        data: WalletUpdate,
    ) -> Wallet | None:
        wallet = self.get_by_id(
            db=db,
            wallet_id=wallet_id,
        )

        if wallet is None:
            return None

        try:
            update_data = data.model_dump(
                exclude_unset=True
            )

            if "currency" in update_data:
                wallet.currency = (
                    self._normalize_currency(
                        update_data["currency"]
                    )
                )

            if "status" in update_data:
                wallet.status = (
                    self._normalize_status(
                        update_data["status"]
                    )
                )

            wallet.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(wallet)

            logger.info(
                "Wallet %s updated.",
                wallet.id,
            )

            return wallet

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật ví %s.",
                wallet_id,
            )

            raise

    # ======================================================
    # DEPOSIT
    # balance + amount
    # available_balance + amount
    # ======================================================

    def deposit(
        self,
        db: Session,
        wallet_id: UUID,
        data: WalletAmountRequest,
    ) -> Wallet:
        wallet = self.get_by_id(
            db=db,
            wallet_id=wallet_id,
        )

        if wallet is None:
            raise ValueError(
                "Wallet not found."
            )

        try:
            self._ensure_wallet_active(
                wallet
            )

            amount = self._to_decimal(
                data.amount
            )

            if amount <= Decimal("0"):
                raise ValueError(
                    "Deposit amount must be greater than zero."
                )

            before = self._snapshot(
                wallet
            )

            wallet.balance = (
                before["balance"]
                + amount
            )

            wallet.available_balance = (
                before["available"]
                + amount
            )

            wallet.locked_balance = (
                before["locked"]
            )

            wallet.updated_at = datetime.utcnow()

            self._validate_balance_consistency(
                wallet
            )

            self._record_transaction(
                db=db,
                wallet=wallet,
                transaction_type="DEPOSIT",
                amount=amount,
                before=before,
                description=(
                    data.description
                    or "Nạp tiền vào ví."
                ),
            )

            db.commit()
            db.refresh(wallet)

            logger.info(
                "Deposited %s %s into wallet %s.",
                amount,
                wallet.currency,
                wallet.id,
            )

            return wallet

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể nạp tiền vào ví %s.",
                wallet_id,
            )

            raise

    # ======================================================
    # WITHDRAW
    # balance - amount
    # available_balance - amount
    # ======================================================

    def withdraw(
        self,
        db: Session,
        wallet_id: UUID,
        data: WalletAmountRequest,
    ) -> Wallet:
        wallet = self.get_by_id(
            db=db,
            wallet_id=wallet_id,
        )

        if wallet is None:
            raise ValueError(
                "Wallet not found."
            )

        try:
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

            self._validate_balance_consistency(
                wallet
            )

            self._record_transaction(
                db=db,
                wallet=wallet,
                transaction_type="WITHDRAW",
                amount=amount,
                before=before,
                description=(
                    data.description
                    or "Rút tiền khỏi ví."
                ),
            )

            db.commit()
            db.refresh(wallet)

            logger.info(
                "Withdrew %s %s from wallet %s.",
                amount,
                wallet.currency,
                wallet.id,
            )

            return wallet

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể rút tiền từ ví %s.",
                wallet_id,
            )

            raise

    # ======================================================
    # LOCK BALANCE
    #
    # balance giữ nguyên
    # available_balance - amount
    # locked_balance + amount
    # ======================================================

    def lock_balance(
        self,
        db: Session,
        wallet_id: UUID,
        data: WalletAmountRequest,
    ) -> Wallet:
        wallet = self.get_by_id(
            db=db,
            wallet_id=wallet_id,
        )

        if wallet is None:
            raise ValueError(
                "Wallet not found."
            )

        try:
            self._ensure_wallet_active(
                wallet
            )

            amount = self._to_decimal(
                data.amount
            )

            if amount <= Decimal("0"):
                raise ValueError(
                    "Lock amount must be greater than zero."
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
            )

            wallet.available_balance = (
                before["available"]
                - amount
            )

            wallet.locked_balance = (
                before["locked"]
                + amount
            )

            wallet.updated_at = datetime.utcnow()

            self._validate_balance_consistency(
                wallet
            )

            self._record_transaction(
                db=db,
                wallet=wallet,
                transaction_type="LOCK",
                amount=amount,
                before=before,
                description=(
                    data.description
                    or "Khóa tiền trong ví."
                ),
            )

            db.commit()
            db.refresh(wallet)

            logger.info(
                "Locked %s %s in wallet %s.",
                amount,
                wallet.currency,
                wallet.id,
            )

            return wallet

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể khóa tiền trong ví %s.",
                wallet_id,
            )

            raise

    # ======================================================
    # RELEASE / UNLOCK BALANCE
    #
    # Đây là mở khóa trả lại tiền cho chính ví đó:
    # balance giữ nguyên
    # available_balance + amount
    # locked_balance - amount
    # ======================================================

    def release_balance(
        self,
        db: Session,
        wallet_id: UUID,
        data: WalletAmountRequest,
    ) -> Wallet:
        wallet = self.get_by_id(
            db=db,
            wallet_id=wallet_id,
        )

        if wallet is None:
            raise ValueError(
                "Wallet not found."
            )

        try:
            self._ensure_wallet_active(
                wallet
            )

            amount = self._to_decimal(
                data.amount
            )

            if amount <= Decimal("0"):
                raise ValueError(
                    "Release amount must be greater than zero."
                )

            before = self._snapshot(
                wallet
            )

            if before["locked"] < amount:
                raise ValueError(
                    "Locked balance is insufficient."
                )

            wallet.balance = (
                before["balance"]
            )

            wallet.available_balance = (
                before["available"]
                + amount
            )

            wallet.locked_balance = (
                before["locked"]
                - amount
            )

            wallet.updated_at = datetime.utcnow()

            self._validate_balance_consistency(
                wallet
            )

            self._record_transaction(
                db=db,
                wallet=wallet,
                transaction_type="RELEASE",
                amount=amount,
                before=before,
                description=(
                    data.description
                    or "Mở khóa tiền trong ví."
                ),
            )

            db.commit()
            db.refresh(wallet)

            logger.info(
                "Released %s %s in wallet %s.",
                amount,
                wallet.currency,
                wallet.id,
            )

            return wallet

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể mở khóa tiền trong ví %s.",
                wallet_id,
            )

            raise

    # ======================================================
    # TRANSFER
    #
    # Người gửi:
    #   balance -= amount
    #   available -= amount
    #
    # Người nhận:
    #   balance += amount
    #   available += amount
    #
    # Ghi 2 WalletTransaction trong cùng transaction.
    # ======================================================

    def transfer(
        self,
        db: Session,
        data: WalletTransferRequest,
    ) -> dict:
        try:
            if (
                data.from_user_id
                == data.to_user_id
            ):
                raise ValueError(
                    "Sender and receiver must be different users."
                )

            amount = self._to_decimal(
                data.amount
            )

            if amount <= Decimal("0"):
                raise ValueError(
                    "Transfer amount must be greater than zero."
                )

            sender = (
                db.query(Wallet)
                .filter(
                    Wallet.user_id
                    == data.from_user_id
                )
                .with_for_update()
                .first()
            )

            receiver = (
                db.query(Wallet)
                .filter(
                    Wallet.user_id
                    == data.to_user_id
                )
                .with_for_update()
                .first()
            )

            if sender is None:
                raise ValueError(
                    "Sender wallet not found."
                )

            if receiver is None:
                raise ValueError(
                    "Receiver wallet not found."
                )

            self._ensure_wallet_active(
                sender
            )

            self._ensure_wallet_active(
                receiver
            )

            sender_currency = (
                self._normalize_currency(
                    sender.currency
                )
            )

            receiver_currency = (
                self._normalize_currency(
                    receiver.currency
                )
            )

            if sender_currency != receiver_currency:
                raise ValueError(
                    "Wallet currencies must be the same."
                )

            sender_before = self._snapshot(
                sender
            )

            receiver_before = self._snapshot(
                receiver
            )

            if sender_before["available"] < amount:
                raise ValueError(
                    "Insufficient available balance."
                )

            sender.balance = (
                sender_before["balance"]
                - amount
            )

            sender.available_balance = (
                sender_before["available"]
                - amount
            )

            sender.locked_balance = (
                sender_before["locked"]
            )

            receiver.balance = (
                receiver_before["balance"]
                + amount
            )

            receiver.available_balance = (
                receiver_before["available"]
                + amount
            )

            receiver.locked_balance = (
                receiver_before["locked"]
            )

            now = datetime.utcnow()

            sender.updated_at = now
            receiver.updated_at = now

            self._validate_balance_consistency(
                sender
            )

            self._validate_balance_consistency(
                receiver
            )

            description = (
                data.description
                or (
                    f"Chuyển tiền từ user "
                    f"{data.from_user_id} "
                    f"đến user {data.to_user_id}."
                )
            )

            self._record_transaction(
                db=db,
                wallet=sender,
                transaction_type="TRANSFER_OUT",
                amount=amount,
                before=sender_before,
                description=description,
                reference_type="USER",
                reference_id=data.to_user_id,
            )

            self._record_transaction(
                db=db,
                wallet=receiver,
                transaction_type="TRANSFER_IN",
                amount=amount,
                before=receiver_before,
                description=description,
                reference_type="USER",
                reference_id=data.from_user_id,
            )

            db.commit()

            db.refresh(sender)
            db.refresh(receiver)

            logger.info(
                "Transferred %s %s from wallet %s to wallet %s.",
                amount,
                sender.currency,
                sender.id,
                receiver.id,
            )

            return {
                "sender": sender,
                "receiver": receiver,
                "amount": amount,
                "currency": sender.currency,
            }

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể chuyển tiền từ user %s đến user %s.",
                data.from_user_id,
                data.to_user_id,
            )

            raise

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        db: Session,
        wallet_id: UUID,
    ) -> bool:
        wallet = self.get_by_id(
            db=db,
            wallet_id=wallet_id,
        )

        if wallet is None:
            return False

        try:
            balance = self._to_decimal(
                wallet.balance
            )

            available = self._to_decimal(
                wallet.available_balance
            )

            locked = self._to_decimal(
                wallet.locked_balance
            )

            if balance != Decimal("0.00"):
                raise ValueError(
                    "Wallet still has balance."
                )

            if available != Decimal("0.00"):
                raise ValueError(
                    "Wallet still has available balance."
                )

            if locked != Decimal("0.00"):
                raise ValueError(
                    "Wallet still has locked balance."
                )

            db.delete(wallet)
            db.commit()

            logger.info(
                "Wallet %s deleted.",
                wallet_id,
            )

            return True

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể xóa ví %s.",
                wallet_id,
            )

            raise


wallet_service = WalletService()