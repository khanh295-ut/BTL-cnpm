from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.src.models.project import Project
from backend.src.models.proposal import Proposal
from backend.src.models.review import Review


class StatisticsService:

    # =========================
    # PROJECT STATS BY MONTH
    # =========================
    def project_by_month(self, db: Session):

        rows = (
            db.query(
                func.date_part("month", Project.created_at).label("month"),
                func.count(Project.id)
            )
            .group_by("month")
            .order_by("month")
            .all()
        )

        return [
            {"month": int(month), "total": total}
            for month, total in rows
        ]

    # =========================
    # PROPOSAL STATS BY MONTH
    # =========================
    def proposal_by_month(self, db: Session):

        rows = (
            db.query(
                func.date_part("month", Proposal.created_at).label("month"),
                func.count(Proposal.id)
            )
            .group_by("month")
            .order_by("month")
            .all()
        )

        return [
            {"month": int(month), "total": total}
            for month, total in rows
        ]

    # =========================
    # REVENUE (from accepted proposals)
    # =========================
    def revenue(self, db: Session):

        total = (
            db.query(func.sum(Proposal.price))
            .filter(Proposal.status == "accepted")
            .scalar()
        )

        return {
            "revenue": float(total) if total else 0
        }

    # =========================
    # REVIEW RATING DISTRIBUTION
    # =========================
    def rating_distribution(self, db: Session):

        rows = (
            db.query(
                Review.rating,
                func.count(Review.id)
            )
            .group_by(Review.rating)
            .order_by(Review.rating)
            .all()
        )

        return [
            {"rating": rating, "total": total}
            for rating, total in rows
        ]