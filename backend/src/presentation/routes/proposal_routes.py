from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.schemas.proposal import ProposalCreate
from src.services.proposal_service import (
    create_proposal,
    get_proposals,
    accept_proposal,
)

router = APIRouter(prefix="/proposals", tags=["Proposals"])


@router.post("/")
def create(data: ProposalCreate, db: Session = Depends(get_db)):
    proposal = create_proposal(db, data)
    if not proposal:
        raise HTTPException(status_code=404, detail="Project not found")
    return proposal


@router.get("/")
def get_all(project_id: int = None, db: Session = Depends(get_db)):
    return get_proposals(db, project_id)


@router.put("/{proposal_id}/accept")
def accept(proposal_id: int, db: Session = Depends(get_db)):
    proposal = accept_proposal(db, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal