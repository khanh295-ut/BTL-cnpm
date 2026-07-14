# backend/src/services/dashboard_service.py

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from backend.src.models.ai_service import AIService
from backend.src.models.auth import User
from backend.src.models.contract import Contract
from backend.src.models.dispute import Dispute
from backend.src.models.enterprise import Enterprise
from backend.src.models.escrow import Escrow
from backend.src.models.expert import Expert
from backend.src.models.payment import Payment
from backend.src.models.project import Project
from backend.src.models.proposal import Proposal
from backend.src.models.review import Review
from backend.src.models.service_order import ServiceOrder
from backend.src.models.wallet import Wallet
from backend.src.models.withdrawal import Withdrawal


logger = logging.getLogger(
    "AITasker.DashboardService"
)


class DashboardService:
    """
    Tổng hợp dữ liệu Dashboard của AITasker.

    Cung cấp:

    - Dashboard tổng quát
    - Dashboard Admin
    - Dashboard Expert
    - Dashboard Enterprise
    - Dữ liệu gần đây
    - Phân bố trạng thái
    """

    SUCCESS_PAYMENT_STATUSES = {
        "SUCCESS",
        "COMPLETED",
        "RELEASED",
    }

    ACTIVE_PROJECT_STATUSES = {
        "OPEN",
        "PENDING",
        "IN_PROGRESS",
        "ACTIVE",
    }

    ACTIVE_ORDER_STATUSES = {
        "CONFIRMED",
        "IN_PROGRESS",
        "DELIVERED",
    }

    OPEN_DISPUTE_STATUSES = {
        "OPEN",
        "PENDING",
        "IN_REVIEW",
        "PROCESSING",
    }

    PENDING_WITHDRAWAL_STATUSES = {
        "PENDING",
        "PROCESSING",
    }

    # ======================================================
    # BASIC HELPERS
    # ======================================================

    @staticmethod
    def _decimal(
        value: Decimal | float | int | str | None,
    ) -> Decimal:
        if value is None:
            return Decimal("0.00")

        if isinstance(value, Decimal):
            return value

        try:
            return Decimal(str(value))
        except (
            TypeError,
            ValueError,
            ArithmeticError,
        ):
            return Decimal("0.00")

    @classmethod
    def _to_float(
        cls,
        value: Decimal | float | int | str | None,
    ) -> float:
        return float(
            cls._decimal(value)
        )

    @staticmethod
    def _to_int(
        value: Any,
    ) -> int:
        try:
            return int(value or 0)
        except (
            TypeError,
            ValueError,
        ):
            return 0

    @staticmethod
    def _stringify_uuid(
        value: Any,
    ) -> str | None:
        if value is None:
            return None

        return str(value)

    @staticmethod
    def _normalize_status(
        value: Any,
    ) -> str:
        return str(
            value or "UNKNOWN"
        ).strip().upper()

    @staticmethod
    def _safe_limit(
        limit: int,
        *,
        default: int = 5,
        maximum: int = 100,
    ) -> int:
        try:
            normalized = int(limit)
        except (
            TypeError,
            ValueError,
        ):
            normalized = default

        return max(
            1,
            min(normalized, maximum),
        )

    # ======================================================
    # SAFE DATABASE HELPERS
    # ======================================================

    @staticmethod
    def _safe_count(
        db: Session,
        model: Any,
    ) -> int:
        try:
            return int(
                db.query(
                    func.count(model.id)
                ).scalar()
                or 0
            )

        except SQLAlchemyError:
            db.rollback()

            logger.exception(
                "Không thể đếm dữ liệu của model %s.",
                getattr(
                    model,
                    "__name__",
                    str(model),
                ),
            )

            return 0

    @classmethod
    def _safe_sum(
        cls,
        db: Session,
        column: Any,
        *filters: Any,
    ) -> Decimal:
        try:
            query = db.query(
                func.coalesce(
                    func.sum(column),
                    0,
                )
            )

            if filters:
                query = query.filter(
                    *filters
                )

            return cls._decimal(
                query.scalar()
            )

        except SQLAlchemyError:
            db.rollback()

            logger.exception(
                "Không thể tính tổng cho column %s.",
                column,
            )

            return Decimal("0.00")

    @staticmethod
    def _safe_status_count(
        db: Session,
        model: Any,
        statuses: set[str],
    ) -> int:
        if not statuses:
            return 0

        try:
            return int(
                db.query(
                    func.count(model.id)
                )
                .filter(
                    func.upper(
                        model.status
                    ).in_(
                        list(statuses)
                    )
                )
                .scalar()
                or 0
            )

        except (
            SQLAlchemyError,
            AttributeError,
        ):
            db.rollback()

            logger.exception(
                "Không thể đếm trạng thái của model %s.",
                getattr(
                    model,
                    "__name__",
                    str(model),
                ),
            )

            return 0

    @staticmethod
    def _status_distribution(
        db: Session,
        model: Any,
    ) -> list[dict[str, Any]]:
        try:
            rows = (
                db.query(
                    model.status,
                    func.count(
                        model.id
                    ).label("total"),
                )
                .group_by(
                    model.status
                )
                .order_by(
                    model.status
                )
                .all()
            )

            return [
                {
                    "status": str(
                        status_value
                        or "UNKNOWN"
                    ).upper(),
                    "total": int(
                        total or 0
                    ),
                }
                for status_value, total in rows
            ]

        except (
            SQLAlchemyError,
            AttributeError,
        ):
            db.rollback()

            logger.exception(
                "Không thể lấy phân bố trạng thái của %s.",
                getattr(
                    model,
                    "__name__",
                    str(model),
                ),
            )

            return []

    # ======================================================
    # PAYMENT / ESCROW AGGREGATES
    # ======================================================

    def _total_revenue(
        self,
        db: Session,
    ) -> Decimal:
        return self._safe_sum(
            db,
            Payment.amount,
            func.upper(
                Payment.status
            ).in_(
                list(
                    self.SUCCESS_PAYMENT_STATUSES
                )
            ),
        )

    def _total_escrow_amount(
        self,
        db: Session,
    ) -> Decimal:
        return self._safe_sum(
            db,
            Escrow.amount,
        )

    def _held_escrow_amount(
        self,
        db: Session,
    ) -> Decimal:
        try:
            value = (
                db.query(
                    func.coalesce(
                        func.sum(
                            Escrow.amount
                            - Escrow.released_amount
                            - Escrow.refunded_amount
                        ),
                        0,
                    )
                )
                .filter(
                    func.upper(
                        Escrow.status
                    ).in_(
                        [
                            "FUNDED",
                            "HELD",
                            "PARTIALLY_RELEASED",
                            "PARTIALLY_REFUNDED",
                            "DISPUTED",
                        ]
                    )
                )
                .scalar()
            )

            return self._decimal(
                value
            )

        except SQLAlchemyError:
            db.rollback()

            logger.exception(
                "Không thể tính số tiền Escrow đang giữ."
            )

            return Decimal("0.00")

    # ======================================================
    # EXPERT SERIALIZATION
    # ======================================================

    def _serialize_expert(
        self,
        expert: Expert,
    ) -> dict[str, Any]:
        raw_skills = getattr(
            expert,
            "skills",
            [],
        ) or []

        skills: list[Any] = []

        for skill in raw_skills:
            if hasattr(
                skill,
                "name",
            ):
                skills.append(
                    {
                        "id": self._stringify_uuid(
                            getattr(
                                skill,
                                "id",
                                None,
                            )
                        ),
                        "name": getattr(
                            skill,
                            "name",
                            "",
                        ),
                    }
                )

            elif isinstance(
                skill,
                dict,
            ):
                skills.append(
                    skill
                )

            else:
                value = str(
                    skill or ""
                ).strip()

                if value:
                    skills.append(
                        value
                    )

        return {
            "id": self._stringify_uuid(
                getattr(
                    expert,
                    "id",
                    None,
                )
            ),
            "name": (
                getattr(
                    expert,
                    "full_name",
                    None,
                )
                or getattr(
                    expert,
                    "name",
                    None,
                )
                or "Chuyên gia"
            ),
            "skills": skills,
        }

    def _experts_data(
        self,
        db: Session,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        try:
            query = (
                db.query(Expert)
                .options(
                    selectinload(
                        Expert.skills
                    )
                )
                .order_by(
                    Expert.created_at.desc()
                )
            )

            if limit is not None:
                query = query.limit(
                    self._safe_limit(limit)
                )

            return [
                self._serialize_expert(
                    expert
                )
                for expert in query.all()
            ]

        except SQLAlchemyError:
            db.rollback()

            logger.exception(
                "Không thể lấy danh sách chuyên gia Dashboard."
            )

            return []

    # ======================================================
    # GENERAL DASHBOARD
    # ======================================================

    def get_dashboard(
        self,
        db: Session,
    ) -> dict[str, Any]:
        """
        Dashboard tổng quát, tương thích với frontend cũ
        và bổ sung số liệu của hệ thống mới.
        """

        total_revenue = self._total_revenue(
            db
        )

        total_escrow_amount = (
            self._total_escrow_amount(
                db
            )
        )

        return {
            # USERS
            "total_users": self._safe_count(
                db,
                User,
            ),
            "total_enterprises": self._safe_count(
                db,
                Enterprise,
            ),
            "total_experts": self._safe_count(
                db,
                Expert,
            ),

            # PROJECT MARKETPLACE
            "total_projects": self._safe_count(
                db,
                Project,
            ),
            "total_proposals": self._safe_count(
                db,
                Proposal,
            ),
            "total_contracts": self._safe_count(
                db,
                Contract,
            ),

            # AI SERVICE MARKETPLACE
            "total_ai_services": self._safe_count(
                db,
                AIService,
            ),
            "total_service_orders": self._safe_count(
                db,
                ServiceOrder,
            ),

            # MONEY
            "total_wallets": self._safe_count(
                db,
                Wallet,
            ),
            "total_escrows": self._safe_count(
                db,
                Escrow,
            ),
            "total_withdrawals": self._safe_count(
                db,
                Withdrawal,
            ),
            "total_revenue": self._to_float(
                total_revenue
            ),
            "total_escrow_amount": self._to_float(
                total_escrow_amount
            ),
            "held_escrow_amount": self._to_float(
                self._held_escrow_amount(
                    db
                )
            ),

            # DISPUTES
            "total_disputes": self._safe_count(
                db,
                Dispute,
            ),

            # STATUS SUMMARIES
            "active_projects": (
                self._safe_status_count(
                    db,
                    Project,
                    self.ACTIVE_PROJECT_STATUSES,
                )
            ),
            "active_service_orders": (
                self._safe_status_count(
                    db,
                    ServiceOrder,
                    self.ACTIVE_ORDER_STATUSES,
                )
            ),
            "pending_withdrawals": (
                self._safe_status_count(
                    db,
                    Withdrawal,
                    self.PENDING_WITHDRAWAL_STATUSES,
                )
            ),
            "open_disputes": (
                self._safe_status_count(
                    db,
                    Dispute,
                    self.OPEN_DISPUTE_STATUSES,
                )
            ),
            "pending_ai_services": (
                self._safe_status_count(
                    db,
                    AIService,
                    {"PENDING"},
                )
            ),

            # FRONTEND DATA
            "experts": self._experts_data(
                db
            ),
            "recent_projects": self.recent_projects(
                db,
                limit=5,
            ),
            "recent_proposals": self.recent_proposals(
                db,
                limit=5,
            ),
            "recent_reviews": self.recent_reviews(
                db,
                limit=5,
            ),

            # STATUS DISTRIBUTION
            "project_status": (
                self.project_status(
                    db
                )
            ),
            "proposal_status": (
                self.proposal_status(
                    db
                )
            ),
            "service_order_status": (
                self.service_order_status(
                    db
                )
            ),
            "ai_service_status": (
                self.ai_service_status(
                    db
                )
            ),
        }

    # ======================================================
    # ADMIN DASHBOARD
    # ======================================================

    def get_admin_dashboard(
        self,
        db: Session,
    ) -> dict[str, Any]:
        dashboard = self.get_dashboard(
            db
        )

        dashboard.update(
            {
                "recent_service_orders": (
                    self.recent_service_orders(
                        db,
                        limit=10,
                    )
                ),
                "recent_withdrawals": (
                    self.recent_withdrawals(
                        db,
                        limit=10,
                    )
                ),
                "recent_disputes": (
                    self.recent_disputes(
                        db,
                        limit=10,
                    )
                ),
                "recent_ai_services": (
                    self.recent_ai_services(
                        db,
                        limit=10,
                    )
                ),
            }
        )

        return dashboard

    # ======================================================
    # EXPERT DASHBOARD
    # ======================================================

    def get_expert_dashboard(
        self,
        db: Session,
        expert_id: UUID,
    ) -> dict[str, Any]:
        expert = (
            db.query(Expert)
            .options(
                selectinload(
                    Expert.skills
                )
            )
            .filter(
                Expert.id == expert_id
            )
            .first()
        )

        if expert is None:
            raise ValueError(
                "Expert not found."
            )

        total_services = int(
            db.query(
                func.count(
                    AIService.id
                )
            )
            .filter(
                AIService.expert_id
                == expert_id
            )
            .scalar()
            or 0
        )

        published_services = int(
            db.query(
                func.count(
                    AIService.id
                )
            )
            .filter(
                AIService.expert_id
                == expert_id,
                func.upper(
                    AIService.status
                )
                == "PUBLISHED",
            )
            .scalar()
            or 0
        )

        total_orders = int(
            db.query(
                func.count(
                    ServiceOrder.id
                )
            )
            .filter(
                ServiceOrder.expert_id
                == expert_id
            )
            .scalar()
            or 0
        )

        active_orders = int(
            db.query(
                func.count(
                    ServiceOrder.id
                )
            )
            .filter(
                ServiceOrder.expert_id
                == expert_id,
                func.upper(
                    ServiceOrder.status
                ).in_(
                    list(
                        self.ACTIVE_ORDER_STATUSES
                    )
                ),
            )
            .scalar()
            or 0
        )

        completed_orders = int(
            db.query(
                func.count(
                    ServiceOrder.id
                )
            )
            .filter(
                ServiceOrder.expert_id
                == expert_id,
                func.upper(
                    ServiceOrder.status
                )
                == "COMPLETED",
            )
            .scalar()
            or 0
        )

        total_income = self._safe_sum(
            db,
            ServiceOrder.price,
            ServiceOrder.expert_id
            == expert_id,
            func.upper(
                ServiceOrder.status
            )
            == "COMPLETED",
        )

        total_proposals = int(
            db.query(
                func.count(
                    Proposal.id
                )
            )
            .filter(
                Proposal.expert_id
                == expert_id
            )
            .scalar()
            or 0
        )

        accepted_proposals = int(
            db.query(
                func.count(
                    Proposal.id
                )
            )
            .filter(
                Proposal.expert_id
                == expert_id,
                func.upper(
                    Proposal.status
                )
                == "ACCEPTED",
            )
            .scalar()
            or 0
        )

        rating_row = (
            db.query(
                func.coalesce(
                    func.avg(
                        Review.rating
                    ),
                    0,
                ),
                func.count(
                    Review.id
                ),
            )
            .filter(
                Review.expert_id
                == expert_id
            )
            .first()
        )

        average_rating = self._to_float(
            rating_row[0]
            if rating_row
            else 0
        )

        review_count = self._to_int(
            rating_row[1]
            if rating_row
            else 0
        )

        return {
            "expert": self._serialize_expert(
                expert
            ),
            "total_ai_services": total_services,
            "published_ai_services": (
                published_services
            ),
            "total_orders": total_orders,
            "active_orders": active_orders,
            "completed_orders": completed_orders,
            "total_proposals": total_proposals,
            "accepted_proposals": (
                accepted_proposals
            ),
            "total_income": self._to_float(
                total_income
            ),
            "average_rating": average_rating,
            "review_count": review_count,
            "recent_orders": (
                self.recent_service_orders(
                    db,
                    limit=10,
                    expert_id=expert_id,
                )
            ),
        }

    # ======================================================
    # ENTERPRISE DASHBOARD
    # ======================================================

    def get_enterprise_dashboard(
        self,
        db: Session,
        enterprise_id: UUID,
    ) -> dict[str, Any]:
        enterprise = (
            db.query(Enterprise)
            .filter(
                Enterprise.id
                == enterprise_id
            )
            .first()
        )

        if enterprise is None:
            raise ValueError(
                "Enterprise not found."
            )

        total_projects = int(
            db.query(
                func.count(
                    Project.id
                )
            )
            .filter(
                Project.enterprise_id
                == enterprise_id
            )
            .scalar()
            or 0
        )

        active_projects = int(
            db.query(
                func.count(
                    Project.id
                )
            )
            .filter(
                Project.enterprise_id
                == enterprise_id,
                func.upper(
                    Project.status
                ).in_(
                    list(
                        self.ACTIVE_PROJECT_STATUSES
                    )
                ),
            )
            .scalar()
            or 0
        )

        total_orders = int(
            db.query(
                func.count(
                    ServiceOrder.id
                )
            )
            .filter(
                ServiceOrder.enterprise_id
                == enterprise_id
            )
            .scalar()
            or 0
        )

        active_orders = int(
            db.query(
                func.count(
                    ServiceOrder.id
                )
            )
            .filter(
                ServiceOrder.enterprise_id
                == enterprise_id,
                func.upper(
                    ServiceOrder.status
                ).in_(
                    list(
                        self.ACTIVE_ORDER_STATUSES
                    )
                ),
            )
            .scalar()
            or 0
        )

        completed_orders = int(
            db.query(
                func.count(
                    ServiceOrder.id
                )
            )
            .filter(
                ServiceOrder.enterprise_id
                == enterprise_id,
                func.upper(
                    ServiceOrder.status
                )
                == "COMPLETED",
            )
            .scalar()
            or 0
        )

        total_spent = self._safe_sum(
            db,
            ServiceOrder.price,
            ServiceOrder.enterprise_id
            == enterprise_id,
            func.upper(
                ServiceOrder.status
            )
            == "COMPLETED",
        )

        total_proposals_received = int(
            db.query(
                func.count(
                    Proposal.id
                )
            )
            .join(
                Project,
                Project.id
                == Proposal.project_id,
            )
            .filter(
                Project.enterprise_id
                == enterprise_id
            )
            .scalar()
            or 0
        )

        return {
            "enterprise_id": enterprise.id,
            "enterprise_name": getattr(
                enterprise,
                "name",
                "Enterprise",
            ),
            "total_projects": total_projects,
            "active_projects": active_projects,
            "total_proposals_received": (
                total_proposals_received
            ),
            "total_service_orders": total_orders,
            "active_service_orders": (
                active_orders
            ),
            "completed_service_orders": (
                completed_orders
            ),
            "total_spent": self._to_float(
                total_spent
            ),
            "recent_projects": (
                self.recent_projects(
                    db,
                    limit=10,
                    enterprise_id=enterprise_id,
                )
            ),
            "recent_orders": (
                self.recent_service_orders(
                    db,
                    limit=10,
                    enterprise_id=enterprise_id,
                )
            ),
        }

    # ======================================================
    # STATUS DISTRIBUTIONS
    # ======================================================

    def project_status(
        self,
        db: Session,
    ) -> list[dict[str, Any]]:
        return self._status_distribution(
            db,
            Project,
        )

    def proposal_status(
        self,
        db: Session,
    ) -> list[dict[str, Any]]:
        return self._status_distribution(
            db,
            Proposal,
        )

    def service_order_status(
        self,
        db: Session,
    ) -> list[dict[str, Any]]:
        return self._status_distribution(
            db,
            ServiceOrder,
        )

    def ai_service_status(
        self,
        db: Session,
    ) -> list[dict[str, Any]]:
        return self._status_distribution(
            db,
            AIService,
        )

    # ======================================================
    # RECENT PROJECTS
    # ======================================================

    def recent_projects(
        self,
        db: Session,
        limit: int = 5,
        enterprise_id: UUID | None = None,
    ) -> list[dict[str, Any]]:
        safe_limit = self._safe_limit(
            limit
        )

        try:
            query = db.query(
                Project
            )

            if enterprise_id is not None:
                query = query.filter(
                    Project.enterprise_id
                    == enterprise_id
                )

            projects = (
                query.order_by(
                    Project.created_at.desc()
                )
                .limit(
                    safe_limit
                )
                .all()
            )

            return [
                {
                    "id": project.id,
                    "title": project.title,
                    "description": getattr(
                        project,
                        "description",
                        None,
                    ),
                    "budget": self._to_float(
                        getattr(
                            project,
                            "budget",
                            0,
                        )
                    ),
                    "deadline": getattr(
                        project,
                        "deadline",
                        None,
                    ),
                    "status": self._normalize_status(
                        getattr(
                            project,
                            "status",
                            "PENDING",
                        )
                    ),
                    "enterprise_id": getattr(
                        project,
                        "enterprise_id",
                        None,
                    ),
                    "category_id": getattr(
                        project,
                        "category_id",
                        None,
                    ),
                    "created_at": getattr(
                        project,
                        "created_at",
                        None,
                    ),
                }
                for project in projects
            ]

        except SQLAlchemyError:
            db.rollback()

            logger.exception(
                "Không thể lấy dự án gần đây."
            )

            return []

    # ======================================================
    # RECENT PROPOSALS
    # ======================================================

    def recent_proposals(
        self,
        db: Session,
        limit: int = 5,
        expert_id: UUID | None = None,
    ) -> list[dict[str, Any]]:
        safe_limit = self._safe_limit(
            limit
        )

        try:
            query = db.query(
                Proposal
            )

            if expert_id is not None:
                query = query.filter(
                    Proposal.expert_id
                    == expert_id
                )

            proposals = (
                query.order_by(
                    Proposal.created_at.desc()
                )
                .limit(
                    safe_limit
                )
                .all()
            )

            return [
                {
                    "id": proposal.id,
                    "project_id": getattr(
                        proposal,
                        "project_id",
                        None,
                    ),
                    "expert_id": getattr(
                        proposal,
                        "expert_id",
                        None,
                    ),
                    "bid_amount": self._to_float(
                        getattr(
                            proposal,
                            "bid_amount",
                            0,
                        )
                    ),
                    "cover_letter": getattr(
                        proposal,
                        "cover_letter",
                        None,
                    ),
                    "estimated_days": getattr(
                        proposal,
                        "estimated_days",
                        None,
                    ),
                    "status": self._normalize_status(
                        getattr(
                            proposal,
                            "status",
                            "PENDING",
                        )
                    ),
                    "created_at": getattr(
                        proposal,
                        "created_at",
                        None,
                    ),
                }
                for proposal in proposals
            ]

        except SQLAlchemyError:
            db.rollback()

            logger.exception(
                "Không thể lấy proposal gần đây."
            )

            return []

    # ======================================================
    # RECENT REVIEWS
    # ======================================================

    def recent_reviews(
        self,
        db: Session,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        safe_limit = self._safe_limit(
            limit
        )

        try:
            reviews = (
                db.query(Review)
                .order_by(
                    Review.created_at.desc()
                )
                .limit(
                    safe_limit
                )
                .all()
            )

            return [
                {
                    "id": review.id,
                    "project_id": getattr(
                        review,
                        "project_id",
                        None,
                    ),
                    "expert_id": getattr(
                        review,
                        "expert_id",
                        None,
                    ),
                    "reviewer_id": getattr(
                        review,
                        "reviewer_id",
                        None,
                    ),
                    "reviewee_id": getattr(
                        review,
                        "reviewee_id",
                        None,
                    ),
                    "rating": self._to_float(
                        getattr(
                            review,
                            "rating",
                            0,
                        )
                    ),
                    "comment": getattr(
                        review,
                        "comment",
                        None,
                    ),
                    "created_at": getattr(
                        review,
                        "created_at",
                        None,
                    ),
                }
                for review in reviews
            ]

        except SQLAlchemyError:
            db.rollback()

            logger.exception(
                "Không thể lấy review gần đây."
            )

            return []

    # ======================================================
    # RECENT SERVICE ORDERS
    # ======================================================

    def recent_service_orders(
        self,
        db: Session,
        limit: int = 5,
        enterprise_id: UUID | None = None,
        expert_id: UUID | None = None,
    ) -> list[dict[str, Any]]:
        safe_limit = self._safe_limit(
            limit
        )

        try:
            query = db.query(
                ServiceOrder
            )

            if enterprise_id is not None:
                query = query.filter(
                    ServiceOrder.enterprise_id
                    == enterprise_id
                )

            if expert_id is not None:
                query = query.filter(
                    ServiceOrder.expert_id
                    == expert_id
                )

            orders = (
                query.order_by(
                    ServiceOrder.created_at.desc()
                )
                .limit(
                    safe_limit
                )
                .all()
            )

            return [
                {
                    "id": order.id,
                    "service_id": order.service_id,
                    "service_title": (
                        order.service_title
                    ),
                    "enterprise_id": (
                        order.enterprise_id
                    ),
                    "expert_id": order.expert_id,
                    "price": self._to_float(
                        order.price
                    ),
                    "currency": order.currency,
                    "status": self._normalize_status(
                        order.status
                    ),
                    "created_at": order.created_at,
                }
                for order in orders
            ]

        except SQLAlchemyError:
            db.rollback()

            logger.exception(
                "Không thể lấy service order gần đây."
            )

            return []

    # ======================================================
    # RECENT AI SERVICES
    # ======================================================

    def recent_ai_services(
        self,
        db: Session,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        safe_limit = self._safe_limit(
            limit
        )

        try:
            services = (
                db.query(AIService)
                .order_by(
                    AIService.created_at.desc()
                )
                .limit(
                    safe_limit
                )
                .all()
            )

            return [
                {
                    "id": service.id,
                    "expert_id": service.expert_id,
                    "category_id": (
                        service.category_id
                    ),
                    "title": service.title,
                    "slug": service.slug,
                    "price": self._to_float(
                        service.price
                    ),
                    "currency": service.currency,
                    "status": self._normalize_status(
                        service.status
                    ),
                    "created_at": (
                        service.created_at
                    ),
                }
                for service in services
            ]

        except SQLAlchemyError:
            db.rollback()

            logger.exception(
                "Không thể lấy AI service gần đây."
            )

            return []

    # ======================================================
    # RECENT WITHDRAWALS
    # ======================================================

    def recent_withdrawals(
        self,
        db: Session,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        safe_limit = self._safe_limit(
            limit
        )

        try:
            withdrawals = (
                db.query(Withdrawal)
                .order_by(
                    Withdrawal.created_at.desc()
                )
                .limit(
                    safe_limit
                )
                .all()
            )

            return [
                {
                    "id": withdrawal.id,
                    "user_id": getattr(
                        withdrawal,
                        "user_id",
                        None,
                    ),
                    "wallet_id": getattr(
                        withdrawal,
                        "wallet_id",
                        None,
                    ),
                    "amount": self._to_float(
                        getattr(
                            withdrawal,
                            "amount",
                            0,
                        )
                    ),
                    "currency": getattr(
                        withdrawal,
                        "currency",
                        "VND",
                    ),
                    "status": self._normalize_status(
                        getattr(
                            withdrawal,
                            "status",
                            "PENDING",
                        )
                    ),
                    "created_at": getattr(
                        withdrawal,
                        "created_at",
                        None,
                    ),
                }
                for withdrawal in withdrawals
            ]

        except SQLAlchemyError:
            db.rollback()

            logger.exception(
                "Không thể lấy withdrawal gần đây."
            )

            return []

    # ======================================================
    # RECENT DISPUTES
    # ======================================================

    def recent_disputes(
        self,
        db: Session,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        safe_limit = self._safe_limit(
            limit
        )

        try:
            disputes = (
                db.query(Dispute)
                .order_by(
                    Dispute.created_at.desc()
                )
                .limit(
                    safe_limit
                )
                .all()
            )

            return [
                {
                    "id": dispute.id,
                    "contract_id": getattr(
                        dispute,
                        "contract_id",
                        None,
                    ),
                    "opened_by_user_id": getattr(
                        dispute,
                        "opened_by_user_id",
                        None,
                    ),
                    "assigned_admin_id": getattr(
                        dispute,
                        "assigned_admin_id",
                        None,
                    ),
                    "reason": getattr(
                        dispute,
                        "reason",
                        None,
                    ),
                    "status": self._normalize_status(
                        getattr(
                            dispute,
                            "status",
                            "OPEN",
                        )
                    ),
                    "created_at": getattr(
                        dispute,
                        "created_at",
                        None,
                    ),
                }
                for dispute in disputes
            ]

        except SQLAlchemyError:
            db.rollback()

            logger.exception(
                "Không thể lấy dispute gần đây."
            )

            return []


dashboard_service = DashboardService()