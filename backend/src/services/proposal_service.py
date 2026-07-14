from __future__ import annotations

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.contract import Contract
from backend.src.models.expert import Expert
from backend.src.models.payment import Payment
from backend.src.models.project import Project
from backend.src.models.proposal import Proposal
from backend.src.schemas.proposal import (
    ProposalCreate,
    ProposalUpdate,
)


logger = logging.getLogger("AITasker.ProposalService")


class ProposalService:
    # =====================================================
    # GET ALL
    # =====================================================

    def get_all(
        self,
        db: Session,
    ) -> list[Proposal]:
        try:
            return (
                db.query(Proposal)
                .order_by(Proposal.created_at.desc())
                .all()
            )
        except Exception:
            logger.exception(
                "Không thể lấy danh sách proposal."
            )
            raise

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        db: Session,
        proposal_id: UUID,
    ) -> Proposal | None:
        try:
            return (
                db.query(Proposal)
                .filter(Proposal.id == proposal_id)
                .first()
            )
        except Exception:
            logger.exception(
                "Không thể lấy proposal %s.",
                proposal_id,
            )
            raise

    # =====================================================
    # VALIDATE PROJECT AND EXPERT
    # =====================================================

    def _validate_project_and_expert(
        self,
        db: Session,
        project_id: UUID,
        expert_id: UUID,
    ) -> tuple[Project, Expert]:
        project = (
            db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        expert = (
            db.query(Expert)
            .filter(Expert.id == expert_id)
            .first()
        )

        if expert is None:
            raise ValueError(
                "Expert not found."
            )

        return project, expert

    # =====================================================
    # NORMALIZE STATUS
    # =====================================================

    def _normalize_status(
        self,
        status_value: str,
    ) -> str:
        normalized_status = str(
            status_value or ""
        ).strip().upper()

        allowed_statuses = {
            "PENDING",
            "ACCEPTED",
            "REJECTED",
            "CANCELLED",
        }

        if normalized_status not in allowed_statuses:
            raise ValueError(
                "Invalid proposal status."
            )

        return normalized_status

    # =====================================================
    # CREATE
    # =====================================================

    def create(
        self,
        db: Session,
        data: ProposalCreate,
    ) -> Proposal:
        try:
            self._validate_project_and_expert(
                db=db,
                project_id=data.project_id,
                expert_id=data.expert_id,
            )

            proposal = Proposal(
                project_id=data.project_id,
                expert_id=data.expert_id,
                bid_amount=data.bid_amount,
                cover_letter=data.cover_letter,
                estimated_days=data.estimated_days,
                status="PENDING",
                created_at=datetime.utcnow(),
            )

            if hasattr(
                proposal,
                "updated_at",
            ):
                proposal.updated_at = datetime.utcnow()

            db.add(proposal)
            db.commit()
            db.refresh(proposal)

            return proposal

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể tạo proposal."
            )

            raise

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        db: Session,
        proposal_id: UUID,
        data: ProposalUpdate,
    ) -> Proposal | None:
        proposal = self.get_by_id(
            db=db,
            proposal_id=proposal_id,
        )

        if proposal is None:
            return None

        try:
            update_data = data.model_dump(
                exclude_unset=True
            )

            next_project_id = update_data.get(
                "project_id",
                proposal.project_id,
            )

            next_expert_id = update_data.get(
                "expert_id",
                proposal.expert_id,
            )

            if (
                "project_id" in update_data
                or "expert_id" in update_data
            ):
                self._validate_project_and_expert(
                    db=db,
                    project_id=next_project_id,
                    expert_id=next_expert_id,
                )

            if "status" in update_data:
                update_data["status"] = (
                    self._normalize_status(
                        update_data["status"]
                    )
                )

            for field_name, value in update_data.items():
                setattr(
                    proposal,
                    field_name,
                    value,
                )

            if hasattr(
                proposal,
                "updated_at",
            ):
                proposal.updated_at = datetime.utcnow()

            if (
                update_data.get("status")
                == "ACCEPTED"
            ):
                self._create_contract_and_payment(
                    db=db,
                    proposal=proposal,
                )

            db.commit()
            db.refresh(proposal)

            return proposal

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật proposal %s.",
                proposal_id,
            )

            raise

    # =====================================================
    # FIND EXISTING CONTRACT
    # =====================================================

    def _find_existing_contract(
        self,
        db: Session,
        proposal: Proposal,
    ) -> Contract | None:
        return (
            db.query(Contract)
            .filter(
                Contract.project_id
                == proposal.project_id,
                Contract.expert_id
                == proposal.expert_id,
            )
            .first()
        )

    # =====================================================
    # FIND EXISTING PAYMENT
    # =====================================================

    def _find_existing_payment(
        self,
        db: Session,
        contract_id: UUID,
    ) -> Payment | None:
        return (
            db.query(Payment)
            .filter(
                Payment.contract_id
                == contract_id
            )
            .first()
        )

    # =====================================================
    # CREATE PAYMENT
    # =====================================================

    def _create_payment_for_contract(
        self,
        db: Session,
        contract: Contract,
        proposal: Proposal,
    ) -> Payment:
        existing_payment = (
            self._find_existing_payment(
                db=db,
                contract_id=contract.id,
            )
        )

        if existing_payment is not None:
            return existing_payment

        payment = Payment(
            contract_id=contract.id,
            amount=proposal.bid_amount,
            currency="VND",
            status="PENDING",
        )

        db.add(payment)

        return payment

    # =====================================================
    # CREATE CONTRACT AND PAYMENT
    # =====================================================

    def _create_contract_and_payment(
        self,
        db: Session,
        proposal: Proposal,
    ) -> Contract:
        """
        Khi Proposal được ACCEPTED:

        1. Nếu Contract chưa tồn tại:
           - tạo Contract;
           - flush để lấy contract.id;
           - tạo Payment PENDING.

        2. Nếu Contract đã tồn tại:
           - không tạo Contract trùng;
           - nếu chưa có Payment thì tạo Payment bổ sung.
        """

        existing_contract = (
            self._find_existing_contract(
                db=db,
                proposal=proposal,
            )
        )

        if existing_contract is not None:
            self._create_payment_for_contract(
                db=db,
                contract=existing_contract,
                proposal=proposal,
            )

            return existing_contract

        project = (
            db.query(Project)
            .filter(
                Project.id
                == proposal.project_id
            )
            .first()
        )

        if project is None:
            raise ValueError(
                "Project not found while creating contract."
            )

        project_title = (
            getattr(
                project,
                "title",
                None,
            )
            or "Dự án AI"
        )

        contract = Contract(
            project_id=proposal.project_id,
            expert_id=proposal.expert_id,
            title=(
                f"Hợp đồng - {project_title}"
            ),
            total_amount=proposal.bid_amount,
            terms=(
                proposal.cover_letter
                or (
                    "Thực hiện công việc theo nội dung "
                    "đề xuất đã được chấp nhận."
                )
            ),
            status="PENDING",
            created_at=datetime.utcnow(),
        )

        if hasattr(
            contract,
            "updated_at",
        ):
            contract.updated_at = datetime.utcnow()

        db.add(contract)

        # Sinh contract.id nhưng chưa commit.
        # Nếu tạo Payment lỗi, toàn bộ transaction sẽ rollback.
        db.flush()

        self._create_payment_for_contract(
            db=db,
            contract=contract,
            proposal=proposal,
        )

        return contract

    # =====================================================
    # UPDATE STATUS
    # =====================================================

    def update_status(
        self,
        db: Session,
        proposal_id: UUID,
        status: str,
    ) -> Proposal | None:
        proposal = self.get_by_id(
            db=db,
            proposal_id=proposal_id,
        )

        if proposal is None:
            return None

        normalized_status = (
            self._normalize_status(status)
        )

        try:
            proposal.status = normalized_status

            if hasattr(
                proposal,
                "updated_at",
            ):
                proposal.updated_at = datetime.utcnow()

            if normalized_status == "ACCEPTED":
                self._create_contract_and_payment(
                    db=db,
                    proposal=proposal,
                )

            db.commit()
            db.refresh(proposal)

            return proposal

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật trạng thái proposal %s.",
                proposal_id,
            )

            raise

    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        db: Session,
        proposal_id: UUID,
    ) -> bool:
        proposal = self.get_by_id(
            db=db,
            proposal_id=proposal_id,
        )

        if proposal is None:
            return False

        try:
            db.delete(proposal)
            db.commit()

            return True

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể xóa proposal %s.",
                proposal_id,
            )

            raise


proposal_service = ProposalService()