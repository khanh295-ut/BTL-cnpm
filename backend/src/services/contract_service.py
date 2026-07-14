# backend/src/services/contract_service.py

from __future__ import annotations

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.contract import Contract
from backend.src.models.expert import Expert
from backend.src.models.project import Project
from backend.src.schemas.contract import (
    ContractCreate,
    ContractUpdate,
)


logger = logging.getLogger(
    "AITasker.ContractService"
)


class ContractService:
    # ======================================================
    # GET ALL
    # ======================================================

    def get_all(
        self,
        db: Session,
    ) -> list[Contract]:
        return (
            db.query(Contract)
            .order_by(
                Contract.created_at.desc()
            )
            .all()
        )

    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        db: Session,
        contract_id: UUID,
    ) -> Contract | None:
        return (
            db.query(Contract)
            .filter(
                Contract.id == contract_id
            )
            .first()
        )

    # ======================================================
    # VALIDATE FOREIGN KEYS
    # ======================================================

    def _validate_project_and_expert(
        self,
        db: Session,
        project_id: UUID,
        expert_id: UUID,
    ) -> tuple[Project, Expert]:
        project = (
            db.query(Project)
            .filter(
                Project.id == project_id
            )
            .first()
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        expert = (
            db.query(Expert)
            .filter(
                Expert.id == expert_id
            )
            .first()
        )

        if expert is None:
            raise ValueError(
                "Expert not found."
            )

        return project, expert

    # ======================================================
    # VALIDATE STATUS
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
            "ACTIVE",
            "IN_PROGRESS",
            "WAITING_APPROVAL",
            "COMPLETED",
            "CANCELLED",
            "REFUNDED",
        }

        if normalized_status not in allowed_statuses:
            raise ValueError(
                "Invalid contract status."
            )

        return normalized_status

    # ======================================================
    # CREATE
    # ======================================================

    def create(
        self,
        db: Session,
        data: ContractCreate,
    ) -> Contract:
        try:
            self._validate_project_and_expert(
                db=db,
                project_id=data.project_id,
                expert_id=data.expert_id,
            )

            normalized_status = (
                self._normalize_status(
                    data.status
                )
            )

            existing_contract = (
                db.query(Contract)
                .filter(
                    Contract.project_id
                    == data.project_id,
                    Contract.expert_id
                    == data.expert_id,
                )
                .first()
            )

            if existing_contract is not None:
                raise ValueError(
                    (
                        "Contract already exists "
                        "for this project and expert."
                    )
                )

            contract = Contract(
                project_id=data.project_id,
                expert_id=data.expert_id,
                title=data.title,
                total_amount=data.total_amount,
                terms=data.terms,
                status=normalized_status,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db.add(contract)
            db.commit()
            db.refresh(contract)

            return contract

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể tạo contract."
            )

            raise

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        db: Session,
        contract_id: UUID,
        data: ContractUpdate,
    ) -> Contract | None:
        contract = self.get_by_id(
            db,
            contract_id,
        )

        if contract is None:
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

            for field_name, value in (
                update_data.items()
            ):
                setattr(
                    contract,
                    field_name,
                    value,
                )

            contract.updated_at = (
                datetime.utcnow()
            )

            db.commit()
            db.refresh(contract)

            return contract

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật contract %s.",
                contract_id,
            )

            raise

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        db: Session,
        contract_id: UUID,
    ) -> bool:
        contract = self.get_by_id(
            db,
            contract_id,
        )

        if contract is None:
            return False

        try:
            db.delete(contract)
            db.commit()

            return True

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể xóa contract %s.",
                contract_id,
            )

            raise


contract_service = ContractService()