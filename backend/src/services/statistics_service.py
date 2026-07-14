from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.src.models.contract import Contract
from backend.src.models.expert import Expert
from backend.src.models.payment import Payment
from backend.src.models.project import Project
from backend.src.models.proposal import Proposal
from backend.src.models.review import Review
from backend.src.models.skill import Skill


class StatisticsService:
    # ======================================================
    # PROJECTS BY MONTH
    # ======================================================

    def project_by_month(
        self,
        db: Session,
    ) -> list[dict]:
        month_expression = func.date_part(
            "month",
            Project.created_at,
        )

        rows = (
            db.query(
                month_expression.label("month"),
                func.count(Project.id).label("total"),
            )
            .filter(Project.created_at.isnot(None))
            .group_by(month_expression)
            .order_by(month_expression)
            .all()
        )

        return [
            {
                "month": int(month),
                "total": int(total or 0),
            }
            for month, total in rows
            if month is not None
        ]

    # ======================================================
    # PROPOSALS BY MONTH
    # ======================================================

    def proposal_by_month(
        self,
        db: Session,
    ) -> list[dict]:
        month_expression = func.date_part(
            "month",
            Proposal.created_at,
        )

        rows = (
            db.query(
                month_expression.label("month"),
                func.count(Proposal.id).label("total"),
            )
            .filter(Proposal.created_at.isnot(None))
            .group_by(month_expression)
            .order_by(month_expression)
            .all()
        )

        return [
            {
                "month": int(month),
                "total": int(total or 0),
            }
            for month, total in rows
            if month is not None
        ]

    # ======================================================
    # REVENUE
    # ======================================================

    def revenue(
        self,
        db: Session,
    ) -> dict:
        total = (
            db.query(
                func.coalesce(
                    func.sum(Payment.amount),
                    0,
                )
            )
            .filter(
                func.upper(Payment.status).in_(
                    [
                        "SUCCESS",
                        "COMPLETED",
                        "RELEASED",
                    ]
                )
            )
            .scalar()
        )

        return {
            "revenue": float(total or 0),
        }

    # ======================================================
    # TOTAL CONTRACT VALUE
    # ======================================================

    def total_contract_value(
        self,
        db: Session,
    ) -> dict:
        total = (
            db.query(
                func.coalesce(
                    func.sum(Contract.total_amount),
                    0,
                )
            )
            .scalar()
        )

        return {
            "total_contract_value": float(total or 0),
        }

    # ======================================================
    # RATING DISTRIBUTION
    # ======================================================

    def rating_distribution(
        self,
        db: Session,
    ) -> list[dict]:
        rows = (
            db.query(
                Review.rating,
                func.count(Review.id).label("total"),
            )
            .group_by(Review.rating)
            .order_by(Review.rating)
            .all()
        )

        return [
            {
                "rating": float(rating),
                "total": int(total or 0),
            }
            for rating, total in rows
            if rating is not None
        ]

    # ======================================================
    # DASHBOARD SUMMARY
    # ======================================================

    def dashboard_summary(
        self,
        db: Session,
    ) -> dict:
        total_revenue = (
            db.query(
                func.coalesce(
                    func.sum(Payment.amount),
                    0,
                )
            )
            .filter(
                func.upper(Payment.status).in_(
                    [
                        "SUCCESS",
                        "COMPLETED",
                        "RELEASED",
                    ]
                )
            )
            .scalar()
        )

        active_experts = (
            db.query(
                func.count(
                    func.distinct(
                        Proposal.expert_id
                    )
                )
            )
            .filter(
                func.upper(Proposal.status)
                == "ACCEPTED"
            )
            .scalar()
        )

        completed_projects = (
            db.query(func.count(Project.id))
            .filter(
                func.upper(Project.status)
                == "COMPLETED"
            )
            .scalar()
        )

        pending_projects = (
            db.query(func.count(Project.id))
            .filter(
                func.upper(Project.status).in_(
                    [
                        "OPEN",
                        "PENDING",
                        "IN_PROGRESS",
                    ]
                )
            )
            .scalar()
        )

        total_projects = (
            db.query(func.count(Project.id))
            .scalar()
        )

        total_experts = (
            db.query(func.count(Expert.id))
            .scalar()
        )

        total_proposals = (
            db.query(func.count(Proposal.id))
            .scalar()
        )

        total_contracts = (
            db.query(func.count(Contract.id))
            .scalar()
        )

        total_payments = (
            db.query(func.count(Payment.id))
            .scalar()
        )

        return {
            "total_revenue": float(total_revenue or 0),
            "active_experts": int(active_experts or 0),
            "completed_projects": int(completed_projects or 0),
            "pending_projects": int(pending_projects or 0),
            "total_projects": int(total_projects or 0),
            "total_experts": int(total_experts or 0),
            "total_proposals": int(total_proposals or 0),
            "total_contracts": int(total_contracts or 0),
            "total_payments": int(total_payments or 0),
        }

    # ======================================================
    # POPULAR SKILLS
    # Expert 1 -> N Skill
    # ======================================================

    def popular_skills(
        self,
        db: Session,
        limit: int = 5,
    ) -> list[dict]:
        rows = (
            db.query(
                Skill.name.label("name"),
                func.count(
                    func.distinct(
                        Skill.expert_id
                    )
                ).label("total"),
            )
            .group_by(Skill.name)
            .order_by(
                func.count(
                    func.distinct(
                        Skill.expert_id
                    )
                ).desc(),
                Skill.name.asc(),
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "name": name,
                "total": int(total or 0),
                "trend": "STABLE",
            }
            for name, total in rows
        ]

    # ======================================================
    # RECENT ACTIVITIES
    # ======================================================

    def recent_activities(
        self,
        db: Session,
        limit: int = 10,
    ) -> list[dict]:
        activities: list[dict] = []

        recent_projects = (
            db.query(Project)
            .order_by(Project.created_at.desc())
            .limit(limit)
            .all()
        )

        for project in recent_projects:
            activities.append(
                {
                    "type": "PROJECT",
                    "title": (
                        f"Dự án mới: "
                        f"{project.title or 'Chưa cập nhật'}"
                    ),
                    "status": project.status,
                    "created_at": project.created_at,
                }
            )

        recent_proposals = (
            db.query(Proposal)
            .order_by(Proposal.created_at.desc())
            .limit(limit)
            .all()
        )

        for proposal in recent_proposals:
            activities.append(
                {
                    "type": "PROPOSAL",
                    "title": (
                        "Một đề xuất mới đã được gửi"
                    ),
                    "status": proposal.status,
                    "created_at": proposal.created_at,
                }
            )

        recent_contracts = (
            db.query(Contract)
            .order_by(Contract.created_at.desc())
            .limit(limit)
            .all()
        )

        for contract in recent_contracts:
            activities.append(
                {
                    "type": "CONTRACT",
                    "title": contract.title,
                    "status": contract.status,
                    "created_at": contract.created_at,
                }
            )

        recent_payments = (
            db.query(Payment)
            .order_by(Payment.created_at.desc())
            .limit(limit)
            .all()
        )

        for payment in recent_payments:
            activities.append(
                {
                    "type": "PAYMENT",
                    "title": (
                        f"Giao dịch "
                        f"{float(payment.amount):,.0f} "
                        f"{payment.currency}"
                    ),
                    "status": payment.status,
                    "created_at": payment.created_at,
                }
            )

        def get_timestamp(item: dict) -> float:
            value = item.get("created_at")

            if value is None:
                return 0.0

            if isinstance(value, datetime):
                try:
                    return value.timestamp()
                except (
                    ValueError,
                    OverflowError,
                    OSError,
                ):
                    return 0.0

            return 0.0

        activities.sort(
            key=get_timestamp,
            reverse=True,
        )

        return activities[:limit]


statistics_service = StatisticsService()