from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.schemas.proposal import ProposalCreate
from src.crud.proposal import (
    create_proposal,
    get_proposals,
    get_proposal_by_id,
    update_proposal,
    delete_proposal,
    accept_proposal,
)

router = APIRouter(
    prefix="/proposals",
    tags=["Proposals"]
)


@router.post("/")
def create(data: ProposalCreate, db: Session = Depends(get_db)):
    proposal = create_proposal(db, data)
    if not proposal:
        raise HTTPException(status_code=404, detail="Project not found")
    return proposal


@router.get("/")
def read_all(db: Session = Depends(get_db)):
    return get_proposals(db)


@router.get("/{proposal_id}")
def read_one(proposal_id: int, db: Session = Depends(get_db)):
    proposal = get_proposal_by_id(db, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.put("/{proposal_id}")
def update(proposal_id: int, data: ProposalCreate, db: Session = Depends(get_db)):
    proposal = update_proposal(db, proposal_id, data)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.delete("/{proposal_id}")
def delete(proposal_id: int, db: Session = Depends(get_db)):
    success = delete_proposal(db, proposal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return {"message": "Proposal deleted successfully"}


@router.put("/{proposal_id}/accept")
def accept(proposal_id: int, db: Session = Depends(get_db)):
    proposal = accept_proposal(db, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal