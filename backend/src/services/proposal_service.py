from sqlalchemy.orm import Session
from backend.src.models.proposal import Proposal


class ProposalService:

    def create_proposal(self, db: Session, data):

        proposal = Proposal(
            project_id=data.project_id,
            expert_id=data.expert_id,
            price=data.price,
            comment=data.comment
        )

        db.add(proposal)
        db.commit()
        db.refresh(proposal)

        return proposal

    def list_proposals(self, db: Session):
        return db.query(Proposal).all()

    def accept_proposal(self, db: Session, proposal_id: str):

        proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
        proposal.status = "accepted"

        db.commit()

        return proposal