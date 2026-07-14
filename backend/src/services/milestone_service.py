from __future__ import annotations

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.contract import Contract
from backend.src.models.milestone import Milestone
from backend.src.schemas.milestone import (
    MilestoneCreate,
    MilestoneUpdate,
)


logger = logging.getLogger("AITasker.MilestoneService")


class MilestoneService:
    # ======================================================
    # GET ALL
    # ======================================================

    def get_all(
        self,
        db: Session,
    ) -> list[Milestone]:
        try:
            return (
                db.query(Milestone)
                .order_by(Milestone.created_at.desc())
                .all()
            )
        except Exception:
            logger.exception(
                "Không thể lấy danh sách milestone."
            )
            raise

    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        db: Session,
        milestone_id: UUID,
    ) -> Milestone | None:
        try:
            return (
                db.query(Milestone)
                .filter(Milestone.id == milestone_id)
                .first()
            )
        except Exception:
            logger.exception(
                "Không thể lấy milestone %s.",
                milestone_id,
            )
            raise

    # ======================================================
    # GET BY CONTRACT
    # ======================================================

    def get_by_contract(
        self,
        db: Session,
        contract_id: UUID,
    ) -> list[Milestone]:
        try:
            return (
                db.query(Milestone)
                .filter(
                    Milestone.contract_id == contract_id
                )
                .order_by(
                    Milestone.deadline.asc(),
                    Milestone.created_at.asc(),
                )
                .all()
            )
        except Exception:
            logger.exception(
                "Không thể lấy milestone của contract %s.",
                contract_id,
            )
            raise

    # ======================================================
    # VALIDATE CONTRACT
    # ======================================================

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
            raise ValueError(
                "Contract not found."
            )

        return contract

    # ======================================================
    # NORMALIZE STATUS
    # ======================================================

    def _normalize_status(
        self,
        status_value: str,
    ) -> str:
        normalized_status = str(
            status_value or ""
        ).strip().upper()

        allowed_statuses = {
            "PENDING",
            "IN_PROGRESS",
            "SUBMITTED",
            "APPROVED",
            "REJECTED",
            "CANCELLED",
        }

        if normalized_status not in allowed_statuses:
            raise ValueError(
                "Invalid milestone status."
            )

        return normalized_status

    # ======================================================
    # VALIDATE TOTAL AMOUNT
    # ======================================================

    def _validate_total_amount(
        self,
        db: Session,
        contract: Contract,
        new_amount,
        exclude_milestone_id: UUID | None = None,
    ) -> None:
        query = db.query(Milestone).filter(
            Milestone.contract_id == contract.id
        )

        if exclude_milestone_id is not None:
            query = query.filter(
                Milestone.id != exclude_milestone_id
            )

        existing_total = sum(
            milestone.amount or 0
            for milestone in query.all()
        )

        future_total = existing_total + new_amount

        if future_total > contract.total_amount:
            raise ValueError(
                "Total milestone amount cannot exceed contract total amount."
            )

    # ======================================================
    # CREATE
    # ======================================================

    def create(
        self,
        db: Session,
        data: MilestoneCreate,
    ) -> Milestone:
        try:
            contract = self._get_contract(
                db=db,
                contract_id=data.contract_id,
            )

            normalized_status = (
                self._normalize_status(
                    data.status
                )
            )

            self._validate_total_amount(
                db=db,
                contract=contract,
                new_amount=data.amount,
            )

            milestone = Milestone(
                contract_id=data.contract_id,
                title=data.title.strip(),
                description=(
                    data.description.strip()
                    if data.description
                    else None
                ),
                amount=data.amount,
                deadline=data.deadline,
                status=normalized_status,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db.add(milestone)
            db.commit()
            db.refresh(milestone)

            return milestone

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể tạo milestone."
            )

            raise

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        db: Session,
        milestone_id: UUID,
        data: MilestoneUpdate,
    ) -> Milestone | None:
        milestone = self.get_by_id(
            db=db,
            milestone_id=milestone_id,
        )

        if milestone is None:
            return None

        try:
            update_data = data.model_dump(
                exclude_unset=True
            )

            if "status" in update_data:
                update_data["status"] = (
                    self._normalize_status(
                        update_data["status"]
                    )
                )

            if "amount" in update_data:
                contract = self._get_contract(
                    db=db,
                    contract_id=milestone.contract_id,
                )

                self._validate_total_amount(
                    db=db,
                    contract=contract,
                    new_amount=update_data["amount"],
                    exclude_milestone_id=milestone.id,
                )

            if "title" in update_data:
                update_data["title"] = (
                    update_data["title"].strip()
                )

            if (
                "description" in update_data
                and update_data["description"] is not None
            ):
                update_data["description"] = (
                    update_data["description"].strip()
                )

            for field_name, value in update_data.items():
                setattr(
                    milestone,
                    field_name,
                    value,
                )

            milestone.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(milestone)

            return milestone

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật milestone %s.",
                milestone_id,
            )

            raise

    # ======================================================
    # UPDATE STATUS
    # ======================================================

    def update_status(
        self,
        db: Session,
        milestone_id: UUID,
        status: str,
    ) -> Milestone | None:
        milestone = self.get_by_id(
            db=db,
            milestone_id=milestone_id,
        )

        if milestone is None:
            return None

        try:
            milestone.status = (
                self._normalize_status(status)
            )

            milestone.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(milestone)

            return milestone

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật trạng thái milestone %s.",
                milestone_id,
            )

            raise

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        db: Session,
        milestone_id: UUID,
    ) -> bool:
        milestone = self.get_by_id(
            db=db,
            milestone_id=milestone_id,
        )

        if milestone is None:
            return False

        try:
            db.delete(milestone)
            db.commit()

            return True

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể xóa milestone %s.",
                milestone_id,
            )

            raise


milestone_service = MilestoneService()