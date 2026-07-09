from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.src.models.auth import User, Role
from backend.src.models.project import Project
from backend.src.models.proposal import Proposal
from backend.src.models.review import Review
from backend.src.models.enterprise import Enterprise
from backend.src.models.expert import Expert


class AdminService:

    # =====================================================
    # USER
    # =====================================================

    def get_all_users(
        self,
        db: Session,
    ):
        return db.query(User).all()

    def get_user(
        self,
        db: Session,
        user_id: UUID,
    ):
        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def delete_user(
        self,
        db: Session,
        user_id: UUID,
    ):

        user = self.get_user(db, user_id)

        if not user:
            return False

        db.delete(user)
        db.commit()

        return True

    # =====================================================
    # ROLE
    # =====================================================

    def change_role(
        self,
        db: Session,
        user_id: UUID,
        role_name: str,
    ):

        user = self.get_user(db, user_id)

        if not user:
            return None

        role = (
            db.query(Role)
            .filter(Role.name == role_name)
            .first()
        )

        if not role:
            return None

        user.roles = [role]

        db.commit()
        db.refresh(user)

        return user

    # =====================================================
    # DASHBOARD
    # =====================================================

    def dashboard(self, db: Session):

        return {
            "users": db.query(User).count(),
            "experts": db.query(Expert).count(),
            "enterprises": db.query(Enterprise).count(),
            "projects": db.query(Project).count(),
            "proposals": db.query(Proposal).count(),
            "reviews": db.query(Review).count(),
        }

    # =====================================================
    # PROJECT STATUS
    # =====================================================

    def project_statistics(
        self,
        db: Session,
    ):

        rows = (
            db.query(
                Project.status,
                func.count(Project.id)
            )
            .group_by(Project.status)
            .all()
        )

        return [
            {
                "status": status,
                "total": total,
            }
            for status, total in rows
        ]

    # =====================================================
    # PROPOSAL STATUS
    # =====================================================

    def proposal_statistics(
        self,
        db: Session,
    ):

        rows = (
            db.query(
                Proposal.status,
                func.count(Proposal.id)
            )
            .group_by(Proposal.status)
            .all()
        )

        return [
            {
                "status": status,
                "total": total,
            }
            for status, total in rows
        ]

    # =====================================================
    # REVIEW
    # =====================================================

    def average_rating(
        self,
        db: Session,
    ):

        avg = db.query(
            func.avg(Review.rating)
        ).scalar()

        return round(float(avg), 2) if avg else 0

    # =====================================================
    # USERS BY ROLE
    # =====================================================

    def users_by_role(
        self,
        db: Session,
    ):

        result = []

        roles = db.query(Role).all()

        for role in roles:

            result.append(
                {
                    "role": role.name,
                    "total": len(role.users),
                }
            )

        return result