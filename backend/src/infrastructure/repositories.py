from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.auth import (
    User,
    Role,
    PasswordResetToken,
)

from backend.src.models.project import Project
from backend.src.models.proposal import Proposal
from backend.src.models.review import Review


# =========================================================
# AUTH REPOSITORY
# =========================================================

class SQLAlchemyAuthRepository:

    def __init__(self, db: Session):
        self.db = db


    # =========================
    # USER
    # =========================

    def get_user_by_username(self, username: str):

        return (
            self.db.query(User)
            .filter(User.username == username)
            .first()
        )


    def get_user_by_email(self, email: str):

        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )


    def get_user_by_id(self, user_id: UUID):

        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )


    def list_users(self):

        return (
            self.db.query(User)
            .order_by(User.username)
            .all()
        )


    def save_user(self, user: User):

        self.db.add(user)

        return user



    # =========================
    # ROLE
    # =========================

    def ensure_role(
        self,
        name: str,
        description: str | None = None
    ):

        role = (
            self.db.query(Role)
            .filter(Role.name == name)
            .first()
        )


        if role:
            return role


        role = Role(
            name=name,
            description=description
        )


        self.db.add(role)
        self.db.flush()


        return role



    # =========================
    # PASSWORD RESET TOKEN
    # =========================

    def create_reset_token(
        self,
        user: User,
        token: str,
        expires_in_minutes: int = 30
    ):

        reset_token = PasswordResetToken.create_for_user(
            user,
            token,
            expires_in_minutes
        )


        self.db.add(reset_token)


        return reset_token



    def get_reset_token(self, token: str):

        return (
            self.db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token == token
            )
            .first()
        )



    def delete_reset_token(
        self,
        reset_token: PasswordResetToken
    ):

        self.db.delete(reset_token)



    # =========================
    # DATABASE
    # =========================

    def commit(self):

        self.db.commit()



    def flush(self):

        self.db.flush()





# =========================================================
# CONTENT REPOSITORY
# =========================================================

class SQLAlchemyContentRepository:


    def __init__(self, db: Session):

        self.db = db



    # =========================
    # PROJECT
    # =========================

    def create_project(
        self,
        title: str,
        description: str,
        status: str = "OPEN"
    ):

        project = Project(
            title=title,
            description=description,
            status=status
        )


        self.db.add(project)


        return project



    def list_projects(self):

        return (
            self.db.query(Project)
            .order_by(Project.id)
            .all()
        )



    def update_project(
        self,
        project_id: UUID,
        title: str,
        description: str
    ):

        project = (
            self.db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )


        if not project:
            return None


        project.title = title
        project.description = description


        return project



    def change_project_status(
        self,
        project_id: UUID,
        status: str
    ):

        project = (
            self.db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )


        if not project:
            return None


        project.status = status


        return project




    # =========================
    # PROPOSAL
    # =========================

    def create_proposal(
        self,
        project_id: UUID,
        expert_id: UUID,
        price: int,
        comment: Optional[str] = None,
        status: str = "PENDING"
    ):

        proposal = Proposal(
            project_id=project_id,
            expert_id=expert_id,
            price=price,
            comment=comment,
            status=status
        )


        self.db.add(proposal)


        return proposal



    def list_proposals(
        self,
        project_id: Optional[UUID] = None
    ):

        query = (
            self.db.query(Proposal)
            .order_by(Proposal.id)
        )


        if project_id is not None:

            query = query.filter(
                Proposal.project_id == project_id
            )


        return query.all()



    def accept_proposal(
        self,
        proposal_id: UUID
    ):

        proposal = (
            self.db.query(Proposal)
            .filter(Proposal.id == proposal_id)
            .first()
        )


        if not proposal:
            return None



        proposal.status = "ACCEPTED"



        self.db.query(Proposal).filter(
            Proposal.project_id == proposal.project_id,
            Proposal.id != proposal_id
        ).update(
            {
                "status": "REJECTED"
            }
        )



        project = (
            self.db.query(Project)
            .filter(Project.id == proposal.project_id)
            .first()
        )


        if project:

            project.status = "IN_PROGRESS"



        return proposal




    # =========================
    # REVIEW
    # =========================

    def create_review(
        self,
        project_id: UUID,
        expert_id: UUID,
        rating: int,
        comment: str
    ):

        review = Review(
            project_id=project_id,
            expert_id=expert_id,
            rating=rating,
            comment=comment
        )


        self.db.add(review)


        return review



    def list_reviews(self):

        return (
            self.db.query(Review)
            .order_by(Review.id)
            .all()
        )



    def commit(self):

        self.db.commit()



    def flush(self):

        self.db.flush()