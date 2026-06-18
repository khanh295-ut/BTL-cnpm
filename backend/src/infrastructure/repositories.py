from __future__ import annotations

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from backend.src.models import Permission, PasswordResetToken, Project, Proposal, Review, Role, User


class SQLAlchemyAuthRepository:
	def __init__(self, db: Session):
		self.db = db

	def get_user_by_id(self, user_id: int):
		return self.db.query(User).options(selectinload(User.roles).selectinload(Role.permissions)).filter(User.id == user_id).first()

	def get_user_by_login(self, login_input: str):
		return (
			self.db.query(User)
			.options(selectinload(User.roles).selectinload(Role.permissions))
			.filter(or_(User.username == login_input, User.email == login_input))
			.first()
		)

	def get_user_by_username(self, username: str):
		return self.db.query(User).filter(User.username == username).first()

	def get_user_by_email(self, email: str):
		return self.db.query(User).filter(User.email == email).first()

	def list_users(self):
		return self.db.query(User).options(selectinload(User.roles)).order_by(User.id).all()

	def save_user(self, user):
		self.db.add(user)
		return user

	def ensure_role(self, name: str, description: str):
		role = self.db.query(Role).filter(Role.name == name).first()
		if role is None:
			role = Role(name=name, description=description)
			self.db.add(role)
			self.db.flush()
		return role

	def ensure_permission(self, name: str, description: str):
		permission = self.db.query(Permission).filter(Permission.name == name).first()
		if permission is None:
			permission = Permission(name=name, description=description)
			self.db.add(permission)
			self.db.flush()
		return permission

	def create_reset_token(self, user, token: str, expires_in_minutes: int = 30):
		reset_token = PasswordResetToken.create_for_user(user, token, expires_in_minutes)
		self.db.add(reset_token)
		return reset_token

	def get_reset_token(self, token: str):
		return self.db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()

	def delete_reset_token(self, reset_token):
		self.db.delete(reset_token)

	def commit(self):
		self.db.commit()


class SQLAlchemyContentRepository:
	def __init__(self, db: Session):
		self.db = db

	def create_project(self, title: str, description: str, status: str = "OPEN"):
		project = Project(title=title, description=description, status=status)
		self.db.add(project)
		return project

	def list_projects(self):
		return self.db.query(Project).order_by(Project.id).all()

	def update_project(self, project_id: int, title: str, description: str):
		project = self.db.query(Project).filter(Project.id == project_id).first()
		if project is None:
			return None
		project.title = title
		project.description = description
		return project

	def change_project_status(self, project_id: int, status: str):
		project = self.db.query(Project).filter(Project.id == project_id).first()
		if project is None:
			return None
		project.status = status
		return project

	def create_proposal(self, project_id: int, expert_id: int, price: int, comment: Optional[str] = None, status: str = "PENDING"):
		proposal = Proposal(
			project_id=project_id,
			expert_id=expert_id,
			price=price,
			comment=comment,
			status=status,
		)
		self.db.add(proposal)
		return proposal

	def list_proposals(self, project_id: Optional[int] = None):
		query = self.db.query(Proposal).order_by(Proposal.id)
		if project_id is not None:
			query = query.filter(Proposal.project_id == project_id)
		return query.all()

	def accept_proposal(self, proposal_id: int):
		proposal = self.db.query(Proposal).filter(Proposal.id == proposal_id).first()
		if proposal is None:
			return None
		proposal.status = "ACCEPTED"
		self.db.query(Proposal).filter(
			Proposal.project_id == proposal.project_id,
			Proposal.id != proposal_id,
		).update({"status": "REJECTED"})
		project = self.db.query(Project).filter(Project.id == proposal.project_id).first()
		if project is not None:
			project.status = "IN_PROGRESS"
		return proposal

	def create_review(self, project_id: int, expert_id: int, rating: int, comment: str):
		review = Review(project_id=project_id, expert_id=expert_id, rating=rating, comment=comment)
		self.db.add(review)
		return review

	def list_reviews(self):
		return self.db.query(Review).order_by(Review.id).all()

	def commit(self):
		self.db.commit()

