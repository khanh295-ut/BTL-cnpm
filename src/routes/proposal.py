from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.models.proposal import Proposal
from src.schemas.proposal import ProposalCreate

router = APIRouter(prefix="/proposals", tags=["proposals"])

# CREATE PROPOSAL
@router.post("/")
def create_proposal(data: ProposalCreate, db: Session = Depends(get_db)):
    proposal = Proposal(**data.dict())
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


# GET ALL PROPOSALS
@router.get("/")
def get_proposals(db: Session = Depends(get_db)):
    return db.query(Proposal).all()


# ACCEPT PROPOSAL
@router.post("/{proposal_id}/accept")
def accept_proposal(proposal_id: int, db: Session = Depends(get_db)):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()

    if not proposal:
        return {"error": "Proposal not found"}

    proposal.status = "ACCEPTED"
    db.commit()
    db.refresh(proposal)

    return {"message": "Proposal accepted", "data": proposal}