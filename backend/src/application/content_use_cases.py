from __future__ import annotations

from backend.src.domain.exceptions import NotFoundError
from backend.src.infrastructure.repositories import SQLAlchemyContentRepository


def create_project(db, title: str, description: str):
    repo = SQLAlchemyContentRepository(db)
    project = repo.create_project(title=title, description=description)
    repo.commit()
    return project


def list_projects(db):
    return SQLAlchemyContentRepository(db).list_projects()


def update_project(db, project_id: int, title: str, description: str):
    repo = SQLAlchemyContentRepository(db)
    project = repo.update_project(project_id, title, description)
    if project is None:
        raise NotFoundError("Not found")
    repo.commit()
    return project


def change_project_status(db, project_id: int, status: str):
    repo = SQLAlchemyContentRepository(db)
    project = repo.change_project_status(project_id, status)
    if project is None:
        raise NotFoundError("Not found")
    repo.commit()
    return project


def create_proposal(db, project_id: int, expert_id: int, price: int, comment: str | None = None):
    repo = SQLAlchemyContentRepository(db)
    proposal = repo.create_proposal(project_id, expert_id, price, comment)
    repo.commit()
    return proposal


def list_proposals(db, project_id: int | None = None):
    return SQLAlchemyContentRepository(db).list_proposals(project_id)


def accept_proposal(db, proposal_id: int):
    repo = SQLAlchemyContentRepository(db)
    proposal = repo.accept_proposal(proposal_id)
    if proposal is None:
        raise NotFoundError("Proposal not found")
    repo.commit()
    return proposal


def create_review(db, project_id: int, expert_id: int, rating: int, comment: str):
    repo = SQLAlchemyContentRepository(db)
    review = repo.create_review(project_id, expert_id, rating, comment)
    repo.commit()
    return review


def list_reviews(db):
    return SQLAlchemyContentRepository(db).list_reviews()

