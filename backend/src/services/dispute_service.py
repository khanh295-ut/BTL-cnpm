from __future__ import annotations

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.auth import User
from backend.src.models.contract import Contract
from backend.src.models.deliverable import Deliverable
from backend.src.models.dispute import Dispute
from backend.src.models.milestone import Milestone
from backend.src.models.payment import Payment
from backend.src.schemas.dispute import (
    DisputeAssignAdminRequest,
    DisputeCloseRequest,
    DisputeCreate,
    DisputeResolveRequest,
    DisputeStatusUpdate,
    DisputeUpdate,
)


logger = logging.getLogger("AITasker.DisputeService")


class DisputeService:
    # ======================================================
    # HELPERS
    # ======================================================

    @staticmethod
    def _normalize_status(value: str) -> str:
        normalized = str(value or "").strip().upper()

        allowed_statuses = {
            "OPEN",
            "UNDER_REVIEW",
            "RESOLVED_CLIENT",
            "RESOLVED_EXPERT",
            "RESOLVED_PARTIAL",
            "CANCELLED",
            "CLOSED",
        }

        if normalized not in allowed_statuses:
            raise ValueError("Invalid dispute status.")

        return normalized

    @staticmethod
    def _normalize_resolution_type(value: str) -> str:
        normalized = str(value or "").strip().upper()

        allowed_types = {
            "RESOLVED_CLIENT",
            "RESOLVED_EXPERT",
            "RESOLVED_PARTIAL",
        }

        if normalized not in allowed_types:
            raise ValueError("Invalid dispute resolution type.")

        return normalized

    def _get_contract(
        self,
        db: Session,
        contract_id: UUID,
    ) -> Contract:
        contract = (
            db.query(Contract)
            .filter(Contract.id == contract_id)
            .first()
        )

        if contract is None:
            raise ValueError("Contract not found.")

        return contract

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
            raise ValueError("User not found.")

        return user

    def _get_payment(
        self,
        db: Session,
        payment_id: UUID | None,
    ) -> Payment | None:
        if payment_id is None:
            return None

        payment = (
            db.query(Payment)
            .filter(Payment.id == payment_id)
            .first()
        )

        if payment is None:
            raise ValueError("Payment not found.")

        return payment

    def _get_milestone(
        self,
        db: Session,
        milestone_id: UUID | None,
    ) -> Milestone | None:
        if milestone_id is None:
            return None

        milestone = (
            db.query(Milestone)
            .filter(Milestone.id == milestone_id)
            .first()
        )

        if milestone is None:
            raise ValueError("Milestone not found.")

        return milestone

    def _get_deliverable(
        self,
        db: Session,
        deliverable_id: UUID | None,
    ) -> Deliverable | None:
        if deliverable_id is None:
            return None

        deliverable = (
            db.query(Deliverable)
            .filter(
                Deliverable.id == deliverable_id
            )
            .first()
        )

        if deliverable is None:
            raise ValueError("Deliverable not found.")

        return deliverable

    def _validate_references(
        self,
        *,
        contract: Contract,
        payment: Payment | None,
        milestone: Milestone | None,
        deliverable: Deliverable | None,
    ) -> None:
        if (
            payment is not None
            and payment.contract_id != contract.id
        ):
            raise ValueError(
                "Payment does not belong to this contract."
            )

        if (
            milestone is not None
            and milestone.contract_id != contract.id
        ):
            raise ValueError(
                "Milestone does not belong to this contract."
            )

        if (
            deliverable is not None
            and milestone is not None
            and deliverable.milestone_id != milestone.id
        ):
            raise ValueError(
                "Deliverable does not belong to this milestone."
            )

        if deliverable is not None and milestone is None:
            linked_milestone = getattr(
                deliverable,
                "milestone",
                None,
            )

            if (
                linked_milestone is not None
                and linked_milestone.contract_id
                != contract.id
            ):
                raise ValueError(
                    "Deliverable does not belong to this contract."
                )

    def _ensure_editable(
        self,
        dispute: Dispute,
    ) -> None:
        status_value = str(
            dispute.status or ""
        ).upper()

        if status_value in {
            "RESOLVED_CLIENT",
            "RESOLVED_EXPERT",
            "RESOLVED_PARTIAL",
            "CLOSED",
            "CANCELLED",
        }:
            raise ValueError(
                "Resolved, closed, or cancelled dispute cannot be edited."
            )

    # ======================================================
    # GET ALL
    # ======================================================

    def get_all(
        self,
        db: Session,
    ) -> list[Dispute]:
        return (
            db.query(Dispute)
            .order_by(Dispute.created_at.desc())
            .all()
        )

    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        db: Session,
        dispute_id: UUID,
    ) -> Dispute | None:
        return (
            db.query(Dispute)
            .filter(Dispute.id == dispute_id)
            .first()
        )

    # ======================================================
    # GET BY CONTRACT
    # ======================================================

    def get_by_contract(
        self,
        db: Session,
        contract_id: UUID,
    ) -> list[Dispute]:
        return (
            db.query(Dispute)
            .filter(
                Dispute.contract_id == contract_id
            )
            .order_by(Dispute.created_at.desc())
            .all()
        )

    # ======================================================
    # GET BY USER
    # ======================================================

    def get_by_user(
        self,
        db: Session,
        user_id: UUID,
    ) -> list[Dispute]:
        return (
            db.query(Dispute)
            .filter(
                Dispute.opened_by_user_id == user_id
            )
            .order_by(Dispute.created_at.desc())
            .all()
        )

    # ======================================================
    # GET BY ADMIN
    # ======================================================

    def get_by_admin(
        self,
        db: Session,
        admin_id: UUID,
    ) -> list[Dispute]:
        return (
            db.query(Dispute)
            .filter(
                Dispute.assigned_admin_id == admin_id
            )
            .order_by(Dispute.created_at.desc())
            .all()
        )

    # ======================================================
    # CREATE
    # ======================================================

    def create(
        self,
        db: Session,
        data: DisputeCreate,
    ) -> Dispute:
        try:
            contract = self._get_contract(
                db=db,
                contract_id=data.contract_id,
            )

            self._get_user(
                db=db,
                user_id=data.opened_by_user_id,
            )

            payment = self._get_payment(
                db=db,
                payment_id=data.payment_id,
            )

            milestone = self._get_milestone(
                db=db,
                milestone_id=data.milestone_id,
            )

            deliverable = self._get_deliverable(
                db=db,
                deliverable_id=data.deliverable_id,
            )

            self._validate_references(
                contract=contract,
                payment=payment,
                milestone=milestone,
                deliverable=deliverable,
            )

            existing_open_dispute = (
                db.query(Dispute)
                .filter(
                    Dispute.contract_id
                    == contract.id,
                    Dispute.status.in_(
                        [
                            "OPEN",
                            "UNDER_REVIEW",
                        ]
                    ),
                )
                .first()
            )

            if existing_open_dispute is not None:
                raise ValueError(
                    "An active dispute already exists for this contract."
                )

            now = datetime.utcnow()

            dispute = Dispute(
                contract_id=contract.id,
                opened_by_user_id=(
                    data.opened_by_user_id
                ),
                payment_id=data.payment_id,
                milestone_id=data.milestone_id,
                deliverable_id=data.deliverable_id,
                title=data.title.strip(),
                reason=data.reason.strip().upper(),
                description=data.description.strip(),
                evidence_url=(
                    data.evidence_url.strip()
                    if data.evidence_url
                    else None
                ),
                status="OPEN",
                opened_at=now,
                created_at=now,
                updated_at=now,
            )

            db.add(dispute)

            if hasattr(contract, "status"):
                contract.status = "DISPUTED"

            if payment is not None:
                payment.status = "DISPUTED"

                if hasattr(payment, "updated_at"):
                    payment.updated_at = now

            db.commit()
            db.refresh(dispute)

            logger.info(
                "Dispute %s created for contract %s.",
                dispute.id,
                contract.id,
            )

            return dispute

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể tạo tranh chấp."
            )

            raise

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        db: Session,
        dispute_id: UUID,
        data: DisputeUpdate,
    ) -> Dispute | None:
        dispute = self.get_by_id(
            db=db,
            dispute_id=dispute_id,
        )

        if dispute is None:
            return None

        try:
            self._ensure_editable(dispute)

            update_data = data.model_dump(
                exclude_unset=True
            )

            payment_id = update_data.get(
                "payment_id",
                dispute.payment_id,
            )

            milestone_id = update_data.get(
                "milestone_id",
                dispute.milestone_id,
            )

            deliverable_id = update_data.get(
                "deliverable_id",
                dispute.deliverable_id,
            )

            contract = self._get_contract(
                db=db,
                contract_id=dispute.contract_id,
            )

            payment = self._get_payment(
                db=db,
                payment_id=payment_id,
            )

            milestone = self._get_milestone(
                db=db,
                milestone_id=milestone_id,
            )

            deliverable = self._get_deliverable(
                db=db,
                deliverable_id=deliverable_id,
            )

            self._validate_references(
                contract=contract,
                payment=payment,
                milestone=milestone,
                deliverable=deliverable,
            )

            for field_name in (
                "title",
                "reason",
                "description",
                "evidence_url",
            ):
                if (
                    field_name in update_data
                    and update_data[field_name]
                    is not None
                ):
                    value = update_data[
                        field_name
                    ].strip()

                    if field_name == "reason":
                        value = value.upper()

                    update_data[field_name] = value

            for field_name, value in update_data.items():
                setattr(
                    dispute,
                    field_name,
                    value,
                )

            dispute.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(dispute)

            return dispute

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật tranh chấp %s.",
                dispute_id,
            )

            raise

    # ======================================================
    # ASSIGN ADMIN
    # ======================================================

    def assign_admin(
        self,
        db: Session,
        dispute_id: UUID,
        data: DisputeAssignAdminRequest,
    ) -> Dispute | None:
        dispute = self.get_by_id(
            db=db,
            dispute_id=dispute_id,
        )

        if dispute is None:
            return None

        try:
            self._ensure_editable(dispute)

            admin = self._get_user(
                db=db,
                user_id=data.assigned_admin_id,
            )

            dispute.assigned_admin_id = admin.id
            dispute.status = "UNDER_REVIEW"
            dispute.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(dispute)

            return dispute

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể gán admin cho tranh chấp %s.",
                dispute_id,
            )

            raise

    # ======================================================
    # UPDATE STATUS
    # ======================================================

    def update_status(
        self,
        db: Session,
        dispute_id: UUID,
        data: DisputeStatusUpdate,
    ) -> Dispute | None:
        dispute = self.get_by_id(
            db=db,
            dispute_id=dispute_id,
        )

        if dispute is None:
            return None

        normalized_status = self._normalize_status(
            data.status
        )

        if normalized_status.startswith(
            "RESOLVED_"
        ):
            raise ValueError(
                "Use the resolve endpoint to resolve a dispute."
            )

        try:
            current_status = str(
                dispute.status or ""
            ).upper()

            if current_status == "CLOSED":
                raise ValueError(
                    "Closed dispute status cannot be changed."
                )

            if (
                normalized_status
                == "UNDER_REVIEW"
                and dispute.assigned_admin_id is None
            ):
                raise ValueError(
                    "Assign an admin before moving dispute to UNDER_REVIEW."
                )

            dispute.status = normalized_status
            dispute.updated_at = datetime.utcnow()

            if normalized_status == "CANCELLED":
                dispute.closed_at = datetime.utcnow()

            db.commit()
            db.refresh(dispute)

            return dispute

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật trạng thái tranh chấp %s.",
                dispute_id,
            )

            raise

    # ======================================================
    # RESOLVE
    # ======================================================

    def resolve(
        self,
        db: Session,
        dispute_id: UUID,
        data: DisputeResolveRequest,
    ) -> Dispute | None:
        try:
            dispute = (
                db.query(Dispute)
                .filter(
                    Dispute.id == dispute_id
                )
                .with_for_update()
                .first()
            )

            if dispute is None:
                return None

            current_status = str(
                dispute.status or ""
            ).upper()

            if current_status not in {
                "OPEN",
                "UNDER_REVIEW",
            }:
                raise ValueError(
                    "Only open or under-review disputes can be resolved."
                )

            resolver = self._get_user(
                db=db,
                user_id=data.resolved_by_user_id,
            )

            resolution_type = (
                self._normalize_resolution_type(
                    data.resolution_type
                )
            )

            now = datetime.utcnow()

            dispute.resolved_by_user_id = resolver.id
            dispute.resolution_type = resolution_type
            dispute.resolution_note = (
                data.resolution_note.strip()
            )
            dispute.status = resolution_type
            dispute.resolved_at = now
            dispute.updated_at = now

            contract = self._get_contract(
                db=db,
                contract_id=dispute.contract_id,
            )

            payment = self._get_payment(
                db=db,
                payment_id=dispute.payment_id,
            )

            if resolution_type == "RESOLVED_CLIENT":
                if payment is not None:
                    payment.status = "REFUNDED"

                    if hasattr(
                        payment,
                        "updated_at",
                    ):
                        payment.updated_at = now

                if hasattr(contract, "status"):
                    contract.status = "CANCELLED"

            elif resolution_type == "RESOLVED_EXPERT":
                if payment is not None:
                    payment.status = "RELEASED"

                    if hasattr(
                        payment,
                        "updated_at",
                    ):
                        payment.updated_at = now

                if hasattr(contract, "status"):
                    contract.status = "COMPLETED"

            elif resolution_type == "RESOLVED_PARTIAL":
                if payment is not None:
                    payment.status = "PARTIALLY_RESOLVED"

                    if hasattr(
                        payment,
                        "updated_at",
                    ):
                        payment.updated_at = now

                if hasattr(contract, "status"):
                    contract.status = "IN_PROGRESS"

            db.commit()
            db.refresh(dispute)

            logger.info(
                "Dispute %s resolved as %s.",
                dispute.id,
                resolution_type,
            )

            return dispute

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể giải quyết tranh chấp %s.",
                dispute_id,
            )

            raise

    # ======================================================
    # CLOSE
    # ======================================================

    def close(
        self,
        db: Session,
        dispute_id: UUID,
        data: DisputeCloseRequest,
    ) -> Dispute | None:
        dispute = self.get_by_id(
            db=db,
            dispute_id=dispute_id,
        )

        if dispute is None:
            return None

        try:
            current_status = str(
                dispute.status or ""
            ).upper()

            allowed_statuses = {
                "RESOLVED_CLIENT",
                "RESOLVED_EXPERT",
                "RESOLVED_PARTIAL",
                "CANCELLED",
            }

            if current_status not in allowed_statuses:
                raise ValueError(
                    "Only resolved or cancelled disputes can be closed."
                )

            if data.resolution_note:
                dispute.resolution_note = (
                    data.resolution_note.strip()
                )

            dispute.status = "CLOSED"
            dispute.closed_at = datetime.utcnow()
            dispute.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(dispute)

            return dispute

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể đóng tranh chấp %s.",
                dispute_id,
            )

            raise

    # ======================================================
    # CANCEL
    # ======================================================

    def cancel(
        self,
        db: Session,
        dispute_id: UUID,
    ) -> Dispute | None:
        dispute = self.get_by_id(
            db=db,
            dispute_id=dispute_id,
        )

        if dispute is None:
            return None

        try:
            current_status = str(
                dispute.status or ""
            ).upper()

            if current_status not in {
                "OPEN",
                "UNDER_REVIEW",
            }:
                raise ValueError(
                    "Only open or under-review disputes can be cancelled."
                )

            now = datetime.utcnow()

            dispute.status = "CANCELLED"
            dispute.closed_at = now
            dispute.updated_at = now

            contract = self._get_contract(
                db=db,
                contract_id=dispute.contract_id,
            )

            if hasattr(contract, "status"):
                contract.status = "IN_PROGRESS"

            payment = self._get_payment(
                db=db,
                payment_id=dispute.payment_id,
            )

            if (
                payment is not None
                and str(
                    payment.status or ""
                ).upper()
                == "DISPUTED"
            ):
                payment.status = "PENDING"

                if hasattr(payment, "updated_at"):
                    payment.updated_at = now

            db.commit()
            db.refresh(dispute)

            return dispute

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể hủy tranh chấp %s.",
                dispute_id,
            )

            raise

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        db: Session,
        dispute_id: UUID,
    ) -> bool:
        dispute = self.get_by_id(
            db=db,
            dispute_id=dispute_id,
        )

        if dispute is None:
            return False

        try:
            current_status = str(
                dispute.status or ""
            ).upper()

            if current_status not in {
                "OPEN",
                "CANCELLED",
            }:
                raise ValueError(
                    "Only open or cancelled disputes can be deleted."
                )

            db.delete(dispute)
            db.commit()

            return True

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể xóa tranh chấp %s.",
                dispute_id,
            )

            raise


dispute_service = DisputeService()