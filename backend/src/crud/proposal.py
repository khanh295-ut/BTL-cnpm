from sqlalchemy.orm import Session

from src.models.proposal import Proposal
from src.models.project import Project
from src.schemas.proposal import ProposalCreate


def create_proposal(db: Session, data: ProposalCreate):
    project = db.query(Project).filter(Project.id == data.project_id).first()
    if not project:
        return None

    proposal = Proposal(
        project_id=data.project_id,
        expert_id=data.expert_id,
        price=data.price,
        comment=data.comment,
        status="PENDING"
    )

    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


def get_proposals(db: Session):
    return db.query(Proposal).all()


def get_proposal_by_id(db: Session, proposal_id: int):
    return db.query(Proposal).filter(Proposal.id == proposal_id).first()


def update_proposal(db: Session, proposal_id: int, data: ProposalCreate):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        return None

    proposal.project_id = data.project_id
    proposal.expert_id = data.expert_id
    proposal.price = data.price
    proposal.comment = data.comment

    db.commit()
    db.refresh(proposal)
    return proposal


def delete_proposal(db: Session, proposal_id: int):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        return False

    db.delete(proposal)
    db.commit()
    return True


def accept_proposal(db: Session, proposal_id: int):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        return None

    proposal.status = "ACCEPTED"

    db.query(Proposal).filter(
        Proposal.project_id == proposal.project_id,
        Proposal.id != proposal_id
    ).update({"status": "REJECTED"})

    project = db.query(Project).filter(Project.id == proposal.project_id).first()
    if project:
        project.status = "IN_PROGRESS"

    db.commit()
    db.refresh(proposal)
    return proposal