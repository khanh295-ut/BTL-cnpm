from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.src.models.contract import Contract
from backend.src.models.escrow import Escrow
from backend.src.models.payment import Payment
from backend.src.models.wallet import Wallet
from backend.src.schemas.escrow import (
    EscrowCreate,
    EscrowFundRequest,
    EscrowRefundRequest,
    EscrowReleaseRequest,
    EscrowUpdate,
)
from backend.src.services.wallet_transaction_service import (
    wallet_transaction_service,
)


logger = logging.getLogger("AITasker.EscrowService")


class EscrowService:
    """
    Service quản lý toàn bộ vòng đời Escrow.

    Luồng chính:

        PENDING
            ↓ fund
        HELD
            ↓ release/refund
        PARTIALLY_RELEASED / PARTIALLY_REFUNDED
            ↓
        RELEASED / REFUNDED / COMPLETED

    Trong đó:

    - RELEASED:
        Toàn bộ tiền được giải ngân cho chuyên gia.

    - REFUNDED:
        Toàn bộ tiền được hoàn lại cho doanh nghiệp.

    - COMPLETED:
        Có cả giải ngân và hoàn tiền, remaining_amount = 0.
    """

    # ======================================================
    # CONSTANTS
    # ======================================================

    ACTIVE_DISTRIBUTION_STATUSES = {
        "HELD",
        "FUNDED",
        "PARTIALLY_RELEASED",
        "PARTIALLY_REFUNDED",
        "DISPUTED",
    }

    MANUAL_STATUSES = {
        "PENDING",
        "HELD",
        "DISPUTED",
        "CANCELLED",
    }

    FINAL_STATUSES = {
        "RELEASED",
        "REFUNDED",
        "COMPLETED",
        "CANCELLED",
    }

    # ======================================================
    # DECIMAL
    # ======================================================

    @staticmethod
    def _decimal(value) -> Decimal:
        if value is None:
            return Decimal("0.00")

        if isinstance(value, Decimal):
            return value

        return Decimal(str(value))

    # ======================================================
    # NORMALIZE
    # ======================================================

    @staticmethod
    def _normalize_currency(value: str | None) -> str:
        normalized = str(
            value or "VND"
        ).strip().upper()

        return normalized or "VND"

    @staticmethod
    def _normalize_status(value: str | None) -> str:
        return str(
            value or ""
        ).strip().upper()

    # ======================================================
    # GET CONTRACT
    # ======================================================

    def _get_contract(
        self,
        db: Session,
        contract_id: UUID,
        *,
        for_update: bool = False,
    ) -> Contract:
        query = (
            db.query(Contract)
            .filter(Contract.id == contract_id)
        )

        if for_update:
            query = query.with_for_update()

        contract = query.first()

        if contract is None:
            raise ValueError(
                "Contract not found."
            )

        return contract

    # ======================================================
    # GET PAYMENT
    # ======================================================

    def _get_payment(
        self,
        db: Session,
        payment_id: UUID | None,
        *,
        for_update: bool = False,
    ) -> Payment | None:
        if payment_id is None:
            return None

        query = (
            db.query(Payment)
            .filter(Payment.id == payment_id)
        )

        if for_update:
            query = query.with_for_update()

        payment = query.first()

        if payment is None:
            raise ValueError(
                "Payment not found."
            )

        return payment

    # ======================================================
    # GET WALLET
    # ======================================================

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

    # ======================================================
    # GET ESCROW FOR UPDATE
    # ======================================================

    def _get_escrow_for_update(
        self,
        db: Session,
        escrow_id: UUID,
    ) -> Escrow:
        escrow = (
            db.query(Escrow)
            .filter(Escrow.id == escrow_id)
            .with_for_update()
            .first()
        )

        if escrow is None:
            raise ValueError(
                "Escrow not found."
            )

        return escrow

    # ======================================================
    # WALLET SNAPSHOT
    # ======================================================

    def _wallet_snapshot(
        self,
        wallet: Wallet,
    ) -> dict[str, Decimal]:
        return {
            "balance": self._decimal(
                wallet.balance
            ),
            "available": self._decimal(
                wallet.available_balance
            ),
            "locked": self._decimal(
                wallet.locked_balance
            ),
        }

    # ======================================================
    # VALIDATE WALLET
    # ======================================================

    def _validate_wallet(
        self,
        wallet: Wallet,
    ) -> None:
        status = self._normalize_status(
            wallet.status
        )

        if status != "ACTIVE":
            raise ValueError(
                f"Wallet is not active. Current status: {status}."
            )

        snapshot = self._wallet_snapshot(
            wallet
        )

        if snapshot["balance"] < Decimal("0"):
            raise ValueError(
                "Wallet balance cannot be negative."
            )

        if snapshot["available"] < Decimal("0"):
            raise ValueError(
                "Wallet available balance cannot be negative."
            )

        if snapshot["locked"] < Decimal("0"):
            raise ValueError(
                "Wallet locked balance cannot be negative."
            )

        if (
            snapshot["balance"]
            != snapshot["available"]
            + snapshot["locked"]
        ):
            raise ValueError(
                "Wallet balance must equal "
                "available_balance + locked_balance."
            )

    # ======================================================
    # VALIDATE CREATE REFERENCES
    # ======================================================

    def _validate_create_references(
        self,
        *,
        contract: Contract,
        payment: Payment | None,
        payer_wallet: Wallet,
        receiver_wallet: Wallet,
        amount: Decimal,
        currency: str,
    ) -> None:
        if payer_wallet.id == receiver_wallet.id:
            raise ValueError(
                "Payer wallet and receiver wallet must be different."
            )

        payer_currency = self._normalize_currency(
            payer_wallet.currency
        )

        receiver_currency = self._normalize_currency(
            receiver_wallet.currency
        )

        if payer_currency != currency:
            raise ValueError(
                "Escrow currency must match payer wallet currency."
            )

        if receiver_currency != currency:
            raise ValueError(
                "Escrow currency must match receiver wallet currency."
            )

        if payment is not None:
            if payment.contract_id != contract.id:
                raise ValueError(
                    "Payment does not belong to this contract."
                )

            payment_currency = self._normalize_currency(
                payment.currency
            )

            if payment_currency != currency:
                raise ValueError(
                    "Escrow currency must match payment currency."
                )

        contract_total = self._decimal(
            getattr(
                contract,
                "total_amount",
                Decimal("0.00"),
            )
        )

        if contract_total > 0 and amount > contract_total:
            raise ValueError(
                "Escrow amount cannot exceed contract total amount."
            )

    # ======================================================
    # REMAINING AMOUNT
    # ======================================================

    def _remaining_amount(
        self,
        escrow: Escrow,
    ) -> Decimal:
        return (
            self._decimal(
                escrow.amount
            )
            - self._decimal(
                escrow.released_amount
            )
            - self._decimal(
                escrow.refunded_amount
            )
        )

    # ======================================================
    # VALIDATE DISTRIBUTION AMOUNT
    # ======================================================

    def _validate_distribution_amount(
        self,
        escrow: Escrow,
        amount,
    ) -> Decimal:
        normalized_amount = self._decimal(
            amount
        )

        if normalized_amount <= Decimal("0"):
            raise ValueError(
                "Amount must be greater than zero."
            )

        remaining = self._remaining_amount(
            escrow
        )

        if remaining <= Decimal("0"):
            raise ValueError(
                "Escrow has no remaining amount."
            )

        if normalized_amount > remaining:
            raise ValueError(
                "Amount exceeds escrow remaining amount."
            )

        return normalized_amount

    # ======================================================
    # DETERMINE FINAL STATUS
    # ======================================================

    def _determine_distribution_status(
        self,
        escrow: Escrow,
        *,
        operation: str,
    ) -> str:
        released = self._decimal(
            escrow.released_amount
        )

        refunded = self._decimal(
            escrow.refunded_amount
        )

        remaining = self._remaining_amount(
            escrow
        )

        if remaining > Decimal("0"):
            if operation == "RELEASE":
                return "PARTIALLY_RELEASED"

            return "PARTIALLY_REFUNDED"

        if released > Decimal("0") and refunded == Decimal("0"):
            return "RELEASED"

        if refunded > Decimal("0") and released == Decimal("0"):
            return "REFUNDED"

        return "COMPLETED"

    # ======================================================
    # APPLY PAYMENT STATUS
    # ======================================================

    def _sync_payment_status(
        self,
        payment: Payment | None,
        escrow_status: str,
        now: datetime,
    ) -> None:
        if payment is None:
            return

        status_mapping = {
            "HELD": "HELD",
            "DISPUTED": "DISPUTED",
            "PARTIALLY_RELEASED": "PARTIALLY_RELEASED",
            "PARTIALLY_REFUNDED": "PARTIALLY_REFUNDED",
            "RELEASED": "RELEASED",
            "REFUNDED": "REFUNDED",
            "COMPLETED": "COMPLETED",
            "CANCELLED": "CANCELLED",
        }

        payment.status = status_mapping.get(
            escrow_status,
            payment.status,
        )

        if hasattr(
            payment,
            "updated_at",
        ):
            payment.updated_at = now

    # ======================================================
    # APPLY CONTRACT STATUS
    # ======================================================

    def _sync_contract_status(
        self,
        contract: Contract,
        escrow_status: str,
        now: datetime,
    ) -> None:
        status_mapping = {
            "PENDING": "PENDING",
            "HELD": "ACTIVE",
            "DISPUTED": "DISPUTED",
            "PARTIALLY_RELEASED": "IN_PROGRESS",
            "PARTIALLY_REFUNDED": "IN_PROGRESS",
            "RELEASED": "COMPLETED",
            "COMPLETED": "COMPLETED",
            "REFUNDED": "CANCELLED",
            "CANCELLED": "CANCELLED",
        }

        if hasattr(
            contract,
            "status",
        ):
            contract.status = status_mapping.get(
                escrow_status,
                contract.status,
            )

        if hasattr(
            contract,
            "updated_at",
        ):
            contract.updated_at = now

    # ======================================================
    # RECORD WALLET TRANSACTION
    # ======================================================

    def _record_wallet_transaction(
        self,
        db: Session,
        *,
        wallet: Wallet,
        transaction_type: str,
        amount: Decimal,
        before: dict[str, Decimal],
        description: str,
        reference_type: str,
        reference_id: UUID,
    ) -> None:
        after = self._wallet_snapshot(
            wallet
        )

        wallet_transaction_service.record_transaction(
            db=db,
            wallet=wallet,
            transaction_type=transaction_type,
            amount=amount,
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
    ) -> list[Escrow]:
        return (
            db.query(Escrow)
            .order_by(
                Escrow.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        db: Session,
        escrow_id: UUID,
    ) -> Escrow | None:
        return (
            db.query(Escrow)
            .filter(Escrow.id == escrow_id)
            .first()
        )

    # ======================================================
    # GET BY CONTRACT
    # ======================================================

    def get_by_contract(
        self,
        db: Session,
        contract_id: UUID,
    ) -> Escrow | None:
        return (
            db.query(Escrow)
            .filter(
                Escrow.contract_id == contract_id
            )
            .first()
        )

    # ======================================================
    # GET BY PAYMENT
    # ======================================================

    def get_by_payment(
        self,
        db: Session,
        payment_id: UUID,
    ) -> Escrow | None:
        return (
            db.query(Escrow)
            .filter(
                Escrow.payment_id == payment_id
            )
            .first()
        )

    # ======================================================
    # GET BY WALLET
    # ======================================================

    def get_by_wallet(
        self,
        db: Session,
        wallet_id: UUID,
    ) -> list[Escrow]:
        return (
            db.query(Escrow)
            .filter(
                or_(
                    Escrow.payer_wallet_id
                    == wallet_id,
                    Escrow.receiver_wallet_id
                    == wallet_id,
                )
            )
            .order_by(
                Escrow.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # GET BY STATUS
    # ======================================================

    def get_by_status(
        self,
        db: Session,
        status: str,
    ) -> list[Escrow]:
        normalized_status = self._normalize_status(
            status
        )

        return (
            db.query(Escrow)
            .filter(
                Escrow.status
                == normalized_status
            )
            .order_by(
                Escrow.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # CREATE
    # ======================================================

    def create(
        self,
        db: Session,
        data: EscrowCreate,
    ) -> Escrow:
        try:
            contract = self._get_contract(
                db=db,
                contract_id=data.contract_id,
            )

            payment = self._get_payment(
                db=db,
                payment_id=data.payment_id,
            )

            payer_wallet = self._get_wallet(
                db=db,
                wallet_id=data.payer_wallet_id,
            )

            receiver_wallet = self._get_wallet(
                db=db,
                wallet_id=data.receiver_wallet_id,
            )

            existing = self.get_by_contract(
                db=db,
                contract_id=contract.id,
            )

            if existing is not None:
                raise ValueError(
                    "Escrow already exists for this contract."
                )

            amount = self._decimal(
                data.amount
            )

            if amount <= Decimal("0"):
                raise ValueError(
                    "Escrow amount must be greater than zero."
                )

            currency = self._normalize_currency(
                data.currency
            )

            self._validate_wallet(
                payer_wallet
            )

            self._validate_wallet(
                receiver_wallet
            )

            self._validate_create_references(
                contract=contract,
                payment=payment,
                payer_wallet=payer_wallet,
                receiver_wallet=receiver_wallet,
                amount=amount,
                currency=currency,
            )

            now = datetime.utcnow()

            escrow = Escrow(
                contract_id=contract.id,
                payment_id=(
                    payment.id
                    if payment is not None
                    else None
                ),
                payer_wallet_id=payer_wallet.id,
                receiver_wallet_id=receiver_wallet.id,
                amount=amount,
                released_amount=Decimal("0.00"),
                refunded_amount=Decimal("0.00"),
                currency=currency,
                status="PENDING",
                note=(
                    data.note.strip()
                    if data.note
                    else None
                ),
                created_at=now,
                updated_at=now,
            )

            db.add(escrow)
            db.commit()
            db.refresh(escrow)

            logger.info(
                "Escrow %s created for contract %s.",
                escrow.id,
                escrow.contract_id,
            )

            return escrow

        except Exception:
            db.rollback()

            logger.exception(
                "Cannot create escrow."
            )

            raise

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        db: Session,
        escrow_id: UUID,
        data: EscrowUpdate,
    ) -> Escrow | None:
        escrow = self.get_by_id(
            db=db,
            escrow_id=escrow_id,
        )

        if escrow is None:
            return None

        try:
            if self._normalize_status(
                escrow.status
            ) != "PENDING":
                raise ValueError(
                    "Only pending escrow can be updated."
                )

            update_data = data.model_dump(
                exclude_unset=True
            )

            payment_id = update_data.get(
                "payment_id",
                escrow.payment_id,
            )

            payer_wallet_id = update_data.get(
                "payer_wallet_id",
                escrow.payer_wallet_id,
            )

            receiver_wallet_id = update_data.get(
                "receiver_wallet_id",
                escrow.receiver_wallet_id,
            )

            amount = self._decimal(
                update_data.get(
                    "amount",
                    escrow.amount,
                )
            )

            currency = self._normalize_currency(
                update_data.get(
                    "currency",
                    escrow.currency,
                )
            )

            contract = self._get_contract(
                db=db,
                contract_id=escrow.contract_id,
            )

            payment = self._get_payment(
                db=db,
                payment_id=payment_id,
            )

            payer_wallet = self._get_wallet(
                db=db,
                wallet_id=payer_wallet_id,
            )

            receiver_wallet = self._get_wallet(
                db=db,
                wallet_id=receiver_wallet_id,
            )

            self._validate_wallet(
                payer_wallet
            )

            self._validate_wallet(
                receiver_wallet
            )

            self._validate_create_references(
                contract=contract,
                payment=payment,
                payer_wallet=payer_wallet,
                receiver_wallet=receiver_wallet,
                amount=amount,
                currency=currency,
            )

            escrow.payment_id = payment_id
            escrow.payer_wallet_id = payer_wallet_id
            escrow.receiver_wallet_id = receiver_wallet_id
            escrow.amount = amount
            escrow.currency = currency

            if "note" in update_data:
                escrow.note = (
                    update_data["note"].strip()
                    if update_data["note"]
                    else None
                )

            escrow.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(escrow)

            return escrow

        except Exception:
            db.rollback()

            logger.exception(
                "Cannot update escrow %s.",
                escrow_id,
            )

            raise

    # ======================================================
    # FUND
    # ======================================================

    def fund(
        self,
        db: Session,
        escrow_id: UUID,
        data: EscrowFundRequest,
    ) -> Escrow:
        try:
            escrow = self._get_escrow_for_update(
                db=db,
                escrow_id=escrow_id,
            )

            if self._normalize_status(
                escrow.status
            ) != "PENDING":
                raise ValueError(
                    "Only pending escrow can be funded."
                )

            payer_wallet = self._get_wallet(
                db=db,
                wallet_id=escrow.payer_wallet_id,
                for_update=True,
            )

            self._validate_wallet(
                payer_wallet
            )

            amount = self._decimal(
                escrow.amount
            )

            before = self._wallet_snapshot(
                payer_wallet
            )

            if before["available"] < amount:
                raise ValueError(
                    "Insufficient available wallet balance."
                )

            payer_wallet.available_balance = (
                before["available"]
                - amount
            )

            payer_wallet.locked_balance = (
                before["locked"]
                + amount
            )

            payer_wallet.balance = (
                before["balance"]
            )

            now = datetime.utcnow()

            payer_wallet.updated_at = now

            self._validate_wallet(
                payer_wallet
            )

            escrow.status = "HELD"
            escrow.funded_at = now
            escrow.updated_at = now

            if data.note:
                escrow.note = data.note.strip()

            payment = self._get_payment(
                db=db,
                payment_id=escrow.payment_id,
                for_update=True,
            )

            contract = self._get_contract(
                db=db,
                contract_id=escrow.contract_id,
                for_update=True,
            )

            self._sync_payment_status(
                payment=payment,
                escrow_status="HELD",
                now=now,
            )

            self._sync_contract_status(
                contract=contract,
                escrow_status="HELD",
                now=now,
            )

            self._record_wallet_transaction(
                db=db,
                wallet=payer_wallet,
                transaction_type="ESCROW_HOLD",
                amount=amount,
                before=before,
                description=(
                    data.note.strip()
                    if data.note
                    else f"Ký quỹ Escrow {escrow.id}."
                ),
                reference_type="ESCROW",
                reference_id=escrow.id,
            )

            db.commit()
            db.refresh(escrow)

            logger.info(
                "Escrow %s funded with %s %s.",
                escrow.id,
                amount,
                escrow.currency,
            )

            return escrow

        except Exception:
            db.rollback()

            logger.exception(
                "Cannot fund escrow %s.",
                escrow_id,
            )

            raise

    # ======================================================
    # RELEASE
    # ======================================================

    def release(
        self,
        db: Session,
        escrow_id: UUID,
        data: EscrowReleaseRequest,
    ) -> Escrow:
        try:
            escrow = self._get_escrow_for_update(
                db=db,
                escrow_id=escrow_id,
            )

            current_status = self._normalize_status(
                escrow.status
            )

            if current_status not in self.ACTIVE_DISTRIBUTION_STATUSES:
                raise ValueError(
                    "Escrow is not available for release."
                )

            amount = self._validate_distribution_amount(
                escrow=escrow,
                amount=data.amount,
            )

            payer_wallet = self._get_wallet(
                db=db,
                wallet_id=escrow.payer_wallet_id,
                for_update=True,
            )

            receiver_wallet = self._get_wallet(
                db=db,
                wallet_id=escrow.receiver_wallet_id,
                for_update=True,
            )

            self._validate_wallet(
                payer_wallet
            )

            self._validate_wallet(
                receiver_wallet
            )

            payer_before = self._wallet_snapshot(
                payer_wallet
            )

            receiver_before = self._wallet_snapshot(
                receiver_wallet
            )

            if payer_before["locked"] < amount:
                raise ValueError(
                    "Payer locked balance is insufficient."
                )

            payer_wallet.balance = (
                payer_before["balance"]
                - amount
            )

            payer_wallet.available_balance = (
                payer_before["available"]
            )

            payer_wallet.locked_balance = (
                payer_before["locked"]
                - amount
            )

            receiver_wallet.balance = (
                receiver_before["balance"]
                + amount
            )

            receiver_wallet.available_balance = (
                receiver_before["available"]
                + amount
            )

            receiver_wallet.locked_balance = (
                receiver_before["locked"]
            )

            now = datetime.utcnow()

            payer_wallet.updated_at = now
            receiver_wallet.updated_at = now

            self._validate_wallet(
                payer_wallet
            )

            self._validate_wallet(
                receiver_wallet
            )

            escrow.released_amount = (
                self._decimal(
                    escrow.released_amount
                )
                + amount
            )

            escrow.status = self._determine_distribution_status(
                escrow=escrow,
                operation="RELEASE",
            )

            if escrow.status in {
                "RELEASED",
                "COMPLETED",
            }:
                escrow.released_at = now

            escrow.updated_at = now

            payment = self._get_payment(
                db=db,
                payment_id=escrow.payment_id,
                for_update=True,
            )

            contract = self._get_contract(
                db=db,
                contract_id=escrow.contract_id,
                for_update=True,
            )

            self._sync_payment_status(
                payment=payment,
                escrow_status=escrow.status,
                now=now,
            )

            self._sync_contract_status(
                contract=contract,
                escrow_status=escrow.status,
                now=now,
            )

            description = (
                data.note.strip()
                if data.note
                else f"Giải ngân Escrow {escrow.id}."
            )

            reference_type = str(
                data.reference_type
                or "ESCROW"
            ).strip().upper()

            reference_id = (
                data.reference_id
                or escrow.id
            )

            self._record_wallet_transaction(
                db=db,
                wallet=payer_wallet,
                transaction_type="ESCROW_RELEASE",
                amount=amount,
                before=payer_before,
                description=description,
                reference_type=reference_type,
                reference_id=reference_id,
            )

            self._record_wallet_transaction(
                db=db,
                wallet=receiver_wallet,
                transaction_type="TRANSFER_IN",
                amount=amount,
                before=receiver_before,
                description=description,
                reference_type=reference_type,
                reference_id=reference_id,
            )

            db.commit()
            db.refresh(escrow)

            logger.info(
                "Released %s %s from escrow %s.",
                amount,
                escrow.currency,
                escrow.id,
            )

            return escrow

        except Exception:
            db.rollback()

            logger.exception(
                "Cannot release escrow %s.",
                escrow_id,
            )

            raise

    # ======================================================
    # PARTIAL RELEASE
    # ======================================================

    def partial_release(
        self,
        db: Session,
        escrow_id: UUID,
        data: EscrowReleaseRequest,
    ) -> Escrow:
        return self.release(
            db=db,
            escrow_id=escrow_id,
            data=data,
        )

    # ======================================================
    # RELEASE ALL
    # ======================================================

    def release_all(
        self,
        db: Session,
        escrow_id: UUID,
        note: str | None = None,
    ) -> Escrow:
        escrow = self.get_by_id(
            db=db,
            escrow_id=escrow_id,
        )

        if escrow is None:
            raise ValueError(
                "Escrow not found."
            )

        remaining = self._remaining_amount(
            escrow
        )

        if remaining <= Decimal("0"):
            raise ValueError(
                "Escrow has no remaining amount."
            )

        request = EscrowReleaseRequest(
            amount=remaining,
            note=note,
            reference_type="ESCROW",
            reference_id=escrow.id,
        )

        return self.release(
            db=db,
            escrow_id=escrow_id,
            data=request,
        )

    # ======================================================
    # REFUND
    # ======================================================

    def refund(
        self,
        db: Session,
        escrow_id: UUID,
        data: EscrowRefundRequest,
    ) -> Escrow:
        try:
            escrow = self._get_escrow_for_update(
                db=db,
                escrow_id=escrow_id,
            )

            current_status = self._normalize_status(
                escrow.status
            )

            if current_status not in self.ACTIVE_DISTRIBUTION_STATUSES:
                raise ValueError(
                    "Escrow is not available for refund."
                )

            amount = self._validate_distribution_amount(
                escrow=escrow,
                amount=data.amount,
            )

            payer_wallet = self._get_wallet(
                db=db,
                wallet_id=escrow.payer_wallet_id,
                for_update=True,
            )

            self._validate_wallet(
                payer_wallet
            )

            before = self._wallet_snapshot(
                payer_wallet
            )

            if before["locked"] < amount:
                raise ValueError(
                    "Payer locked balance is insufficient."
                )

            payer_wallet.balance = (
                before["balance"]
            )

            payer_wallet.available_balance = (
                before["available"]
                + amount
            )

            payer_wallet.locked_balance = (
                before["locked"]
                - amount
            )

            now = datetime.utcnow()

            payer_wallet.updated_at = now

            self._validate_wallet(
                payer_wallet
            )

            escrow.refunded_amount = (
                self._decimal(
                    escrow.refunded_amount
                )
                + amount
            )

            escrow.status = self._determine_distribution_status(
                escrow=escrow,
                operation="REFUND",
            )

            if escrow.status in {
                "REFUNDED",
                "COMPLETED",
            }:
                escrow.refunded_at = now

            escrow.updated_at = now

            payment = self._get_payment(
                db=db,
                payment_id=escrow.payment_id,
                for_update=True,
            )

            contract = self._get_contract(
                db=db,
                contract_id=escrow.contract_id,
                for_update=True,
            )

            self._sync_payment_status(
                payment=payment,
                escrow_status=escrow.status,
                now=now,
            )

            self._sync_contract_status(
                contract=contract,
                escrow_status=escrow.status,
                now=now,
            )

            description = (
                data.note.strip()
                if data.note
                else f"Hoàn tiền Escrow {escrow.id}."
            )

            reference_type = str(
                data.reference_type
                or "ESCROW"
            ).strip().upper()

            reference_id = (
                data.reference_id
                or escrow.id
            )

            self._record_wallet_transaction(
                db=db,
                wallet=payer_wallet,
                transaction_type="REFUND",
                amount=amount,
                before=before,
                description=description,
                reference_type=reference_type,
                reference_id=reference_id,
            )

            db.commit()
            db.refresh(escrow)

            logger.info(
                "Refunded %s %s from escrow %s.",
                amount,
                escrow.currency,
                escrow.id,
            )

            return escrow

        except Exception:
            db.rollback()

            logger.exception(
                "Cannot refund escrow %s.",
                escrow_id,
            )

            raise

    # ======================================================
    # PARTIAL REFUND
    # ======================================================

    def partial_refund(
        self,
        db: Session,
        escrow_id: UUID,
        data: EscrowRefundRequest,
    ) -> Escrow:
        return self.refund(
            db=db,
            escrow_id=escrow_id,
            data=data,
        )

    # ======================================================
    # REFUND ALL
    # ======================================================

    def refund_all(
        self,
        db: Session,
        escrow_id: UUID,
        note: str | None = None,
    ) -> Escrow:
        escrow = self.get_by_id(
            db=db,
            escrow_id=escrow_id,
        )

        if escrow is None:
            raise ValueError(
                "Escrow not found."
            )

        remaining = self._remaining_amount(
            escrow
        )

        if remaining <= Decimal("0"):
            raise ValueError(
                "Escrow has no remaining amount."
            )

        request = EscrowRefundRequest(
            amount=remaining,
            note=note,
            reference_type="ESCROW",
            reference_id=escrow.id,
        )

        return self.refund(
            db=db,
            escrow_id=escrow_id,
            data=request,
        )

    # ======================================================
    # UPDATE STATUS
    # ======================================================

    def update_status(
        self,
        db: Session,
        escrow_id: UUID,
        status: str,
        note: str | None = None,
    ) -> Escrow:
        escrow = self.get_by_id(
            db=db,
            escrow_id=escrow_id,
        )

        if escrow is None:
            raise ValueError(
                "Escrow not found."
            )

        try:
            normalized_status = self._normalize_status(
                status
            )

            if normalized_status not in self.MANUAL_STATUSES:
                raise ValueError(
                    "Manual status may only be "
                    "PENDING, HELD, DISPUTED, or CANCELLED."
                )

            current_status = self._normalize_status(
                escrow.status
            )

            if current_status in {
                "RELEASED",
                "REFUNDED",
                "COMPLETED",
            }:
                raise ValueError(
                    "Completed escrow status cannot be changed."
                )

            remaining = self._remaining_amount(
                escrow
            )

            if (
                normalized_status == "CANCELLED"
                and self._decimal(
                    escrow.amount
                )
                != remaining
            ):
                raise ValueError(
                    "Escrow with distributed funds cannot be cancelled."
                )

            if (
                normalized_status == "PENDING"
                and escrow.funded_at is not None
            ):
                raise ValueError(
                    "Funded escrow cannot return to PENDING."
                )

            now = datetime.utcnow()

            escrow.status = normalized_status
            escrow.updated_at = now

            if note:
                escrow.note = note.strip()

            payment = self._get_payment(
                db=db,
                payment_id=escrow.payment_id,
            )

            contract = self._get_contract(
                db=db,
                contract_id=escrow.contract_id,
            )

            self._sync_payment_status(
                payment=payment,
                escrow_status=normalized_status,
                now=now,
            )

            self._sync_contract_status(
                contract=contract,
                escrow_status=normalized_status,
                now=now,
            )

            db.commit()
            db.refresh(escrow)

            return escrow

        except Exception:
            db.rollback()

            logger.exception(
                "Cannot update escrow status %s.",
                escrow_id,
            )

            raise

    # ======================================================
    # SUMMARY
    # ======================================================

    def summary(
        self,
        db: Session,
    ) -> dict:
        escrows = db.query(Escrow).all()

        total_amount = Decimal("0.00")
        total_released = Decimal("0.00")
        total_refunded = Decimal("0.00")

        pending_count = 0
        held_count = 0
        released_count = 0
        refunded_count = 0
        disputed_count = 0

        for escrow in escrows:
            total_amount += self._decimal(
                escrow.amount
            )

            total_released += self._decimal(
                escrow.released_amount
            )

            total_refunded += self._decimal(
                escrow.refunded_amount
            )

            status = self._normalize_status(
                escrow.status
            )

            if status == "PENDING":
                pending_count += 1

            elif status in {
                "FUNDED",
                "HELD",
            }:
                held_count += 1

            elif status in {
                "PARTIALLY_RELEASED",
                "RELEASED",
                "COMPLETED",
            }:
                released_count += 1

            elif status in {
                "PARTIALLY_REFUNDED",
                "REFUNDED",
            }:
                refunded_count += 1

            elif status == "DISPUTED":
                disputed_count += 1

        return {
            "total_amount": total_amount,
            "total_released": total_released,
            "total_refunded": total_refunded,
            "total_remaining": (
                total_amount
                - total_released
                - total_refunded
            ),
            "pending_count": pending_count,
            "held_count": held_count,
            "released_count": released_count,
            "refunded_count": refunded_count,
            "disputed_count": disputed_count,
        }

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        db: Session,
        escrow_id: UUID,
    ) -> bool:
        escrow = self.get_by_id(
            db=db,
            escrow_id=escrow_id,
        )

        if escrow is None:
            return False

        try:
            current_status = self._normalize_status(
                escrow.status
            )

            if current_status not in {
                "PENDING",
                "CANCELLED",
            }:
                raise ValueError(
                    "Only pending or cancelled escrow can be deleted."
                )

            if (
                self._decimal(
                    escrow.released_amount
                )
                > Decimal("0")
                or self._decimal(
                    escrow.refunded_amount
                )
                > Decimal("0")
            ):
                raise ValueError(
                    "Escrow with distributed funds cannot be deleted."
                )

            db.delete(escrow)
            db.commit()

            return True

        except Exception:
            db.rollback()

            logger.exception(
                "Cannot delete escrow %s.",
                escrow_id,
            )

            raise


escrow_service = EscrowService()