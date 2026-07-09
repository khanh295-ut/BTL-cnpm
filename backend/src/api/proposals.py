from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from backend.src.config.database import get_db
from backend.src.schemas.proposal import ProposalCreate, ProposalUpdate, ProposalResponse, ProposalStatusUpdate
from backend.src.services.proposal_service import proposal_service

# 🔴 THÊM "/api" VÀO TRƯỚC PREFIX
router = APIRouter(
    prefix="/api/proposals",
    tags=["Proposals"]
)

@router.get("/", response_model=List[ProposalResponse])
def get_proposals(db: Session = Depends(get_db)):
    return proposal_service.get_all(db)

@router.post("/", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
def create_proposal(payload: ProposalCreate, db: Session = Depends(get_db)):
    return proposal_service.create(db, payload)

@router.get("/{proposal_id}/", response_model=ProposalResponse)
def get_proposal(proposal_id: UUID, db: Session = Depends(get_db)):
    proposal = proposal_service.get_by_id(db, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal