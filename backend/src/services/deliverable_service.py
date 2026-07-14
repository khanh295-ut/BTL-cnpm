from __future__ import annotations

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.deliverable import Deliverable
from backend.src.models.milestone import Milestone
from backend.src.schemas.deliverable import (
    DeliverableCreate,
    DeliverableReview,
    DeliverableUpdate,
)


logger = logging.getLogger("AITasker.DeliverableService")


class DeliverableService:
    # ======================================================
    # GET ALL
    # ======================================================

    def get_all(
        self,
        db: Session,
    ) -> list[Deliverable]:
        try:
            return (
                db.query(Deliverable)
                .order_by(Deliverable.created_at.desc())
                .all()
            )
        except Exception:
            logger.exception(
                "Không thể lấy danh sách deliverable."
            )
            raise

    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        db: Session,
        deliverable_id: UUID,
    ) -> Deliverable | None:
        try:
            return (
                db.query(Deliverable)
                .filter(
                    Deliverable.id == deliverable_id
                )
                .first()
            )
        except Exception:
            logger.exception(
                "Không thể lấy deliverable %s.",
                deliverable_id,
            )
            raise

    # ======================================================
    # GET BY MILESTONE
    # ======================================================

    def get_by_milestone(
        self,
        db: Session,
        milestone_id: UUID,
    ) -> list[Deliverable]:
        try:
            return (
                db.query(Deliverable)
                .filter(
                    Deliverable.milestone_id
                    == milestone_id
                )
                .order_by(
                    Deliverable.created_at.desc()
                )
                .all()
            )
        except Exception:
            logger.exception(
                "Không thể lấy deliverable của milestone %s.",
                milestone_id,
            )
            raise

    # ======================================================
    # VALIDATE MILESTONE
    # ======================================================

    def _get_milestone(
        self,
        db: Session,
        milestone_id: UUID,
    ) -> Milestone:
        milestone = (
            db.query(Milestone)
            .filter(
                Milestone.id == milestone_id
            )
            .first()
        )

        if milestone is None:
            raise ValueError(
                "Milestone not found."
            )

        return milestone

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
            "DRAFT",
            "SUBMITTED",
            "APPROVED",
            "REJECTED",
            "REVISION_REQUIRED",
        }

        if normalized_status not in allowed_statuses:
            raise ValueError(
                "Invalid deliverable status."
            )

        return normalized_status

    # ======================================================
    # CREATE
    # ======================================================

    def create(
        self,
        db: Session,
        data: DeliverableCreate,
    ) -> Deliverable:
        try:
            milestone = self._get_milestone(
                db=db,
                milestone_id=data.milestone_id,
            )

            deliverable = Deliverable(
                milestone_id=data.milestone_id,
                description=(
                    data.description.strip()
                    if data.description
                    else None
                ),
                file_url=(
                    data.file_url.strip()
                    if data.file_url
                    else None
                ),
                demo_url=(
                    data.demo_url.strip()
                    if data.demo_url
                    else None
                ),
                status="DRAFT",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db.add(deliverable)

            if str(milestone.status).upper() == "PENDING":
                milestone.status = "IN_PROGRESS"
                milestone.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(deliverable)

            return deliverable

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể tạo deliverable."
            )

            raise

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        db: Session,
        deliverable_id: UUID,
        data: DeliverableUpdate,
    ) -> Deliverable | None:
        deliverable = self.get_by_id(
            db=db,
            deliverable_id=deliverable_id,
        )

        if deliverable is None:
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

            for field_name in (
                "description",
                "file_url",
                "demo_url",
                "feedback",
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
                    deliverable,
                    field_name,
                    value,
                )

            if (
                update_data.get("status")
                == "SUBMITTED"
            ):
                deliverable.submitted_at = (
                    datetime.utcnow()
                )

            if (
                update_data.get("status")
                in {
                    "APPROVED",
                    "REJECTED",
                    "REVISION_REQUIRED",
                }
            ):
                deliverable.reviewed_at = (
                    datetime.utcnow()
                )

            deliverable.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(deliverable)

            return deliverable

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật deliverable %s.",
                deliverable_id,
            )

            raise

    # ======================================================
    # SUBMIT
    # ======================================================

    def submit(
        self,
        db: Session,
        deliverable_id: UUID,
    ) -> Deliverable | None:
        deliverable = self.get_by_id(
            db=db,
            deliverable_id=deliverable_id,
        )

        if deliverable is None:
            return None

        try:
            if (
                not deliverable.file_url
                and not deliverable.demo_url
                and not deliverable.description
            ):
                raise ValueError(
                    "Deliverable must contain description, file URL, or demo URL before submission."
                )

            deliverable.status = "SUBMITTED"
            deliverable.submitted_at = datetime.utcnow()
            deliverable.updated_at = datetime.utcnow()

            milestone = self._get_milestone(
                db=db,
                milestone_id=deliverable.milestone_id,
            )

            milestone.status = "SUBMITTED"
            milestone.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(deliverable)

            return deliverable

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể submit deliverable %s.",
                deliverable_id,
            )

            raise

    # ======================================================
    # REVIEW
    # ======================================================

    def review(
        self,
        db: Session,
        deliverable_id: UUID,
        data: DeliverableReview,
    ) -> Deliverable | None:
        deliverable = self.get_by_id(
            db=db,
            deliverable_id=deliverable_id,
        )

        if deliverable is None:
            return None

        try:
            normalized_status = self._normalize_status(
                data.status
            )

            allowed_review_statuses = {
                "APPROVED",
                "REJECTED",
                "REVISION_REQUIRED",
            }

            if normalized_status not in allowed_review_statuses:
                raise ValueError(
                    "Review status must be APPROVED, REJECTED, or REVISION_REQUIRED."
                )

            if (
                str(deliverable.status).upper()
                != "SUBMITTED"
            ):
                raise ValueError(
                    "Only submitted deliverables can be reviewed."
                )

            deliverable.status = normalized_status
            deliverable.feedback = (
                data.feedback.strip()
                if data.feedback
                else None
            )
            deliverable.reviewed_at = datetime.utcnow()
            deliverable.updated_at = datetime.utcnow()

            milestone = self._get_milestone(
                db=db,
                milestone_id=deliverable.milestone_id,
            )

            if normalized_status == "APPROVED":
                milestone.status = "APPROVED"

            elif normalized_status == "REVISION_REQUIRED":
                milestone.status = "IN_PROGRESS"

            elif normalized_status == "REJECTED":
                milestone.status = "REJECTED"

            milestone.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(deliverable)

            return deliverable

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể review deliverable %s.",
                deliverable_id,
            )

            raise

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        db: Session,
        deliverable_id: UUID,
    ) -> bool:
        deliverable = self.get_by_id(
            db=db,
            deliverable_id=deliverable_id,
        )

        if deliverable is None:
            return False

        try:
            if (
                str(deliverable.status).upper()
                == "APPROVED"
            ):
                raise ValueError(
                    "Approved deliverable cannot be deleted."
                )

            db.delete(deliverable)
            db.commit()

            return True

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể xóa deliverable %s.",
                deliverable_id,
            )

            raise


deliverable_service = DeliverableService()