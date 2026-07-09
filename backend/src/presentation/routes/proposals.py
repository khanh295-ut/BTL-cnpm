from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from backend.src.config.database import get_db
from backend.src.schemas.proposal import (
    ProposalCreate,
    ProposalUpdate,
    ProposalResponse,
    ProposalStatusUpdate,
)
from backend.src.services.proposal_service import proposal_service

# 🔴 Thêm "/api" vào prefix để đồng bộ với frontend
router = APIRouter(
    prefix="/api/proposals",
    tags=["Proposals"]
)

# ======================================================
# GET ALL PROPOSALS
# ======================================================
@router.get("/", response_model=List[ProposalResponse])
def get_proposals(db: Session = Depends(get_db)):
    return proposal_service.get_all(db)

# ======================================================
# CREATE PROPOSAL
# ======================================================
@router.post("/", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
def create_proposal(payload: ProposalCreate, db: Session = Depends(get_db)):
    return proposal_service.create(db, payload)

# ======================================================
# GET PROPOSAL BY ID
# ======================================================
@router.get("/{proposal_id}/", response_model=ProposalResponse)
def get_proposal(proposal_id: UUID, db: Session = Depends(get_db)):
    proposal = proposal_service.get_by_id(db, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal

# ======================================================
# UPDATE PROPOSAL
# ======================================================
@router.put("/{proposal_id}/", response_model=ProposalResponse)
def update_proposal(proposal_id: UUID, payload: ProposalUpdate, db: Session = Depends(get_db)):
    proposal = proposal_service.update(db, proposal_id, payload)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal

# ======================================================
# UPDATE STATUS
# ======================================================
@router.patch("/{proposal_id}/status", response_model=ProposalResponse)
def update_proposal_status(proposal_id: UUID, payload: ProposalStatusUpdate, db: Session = Depends(get_db)):
    proposal = proposal_service.update_status(db, proposal_id, payload.status)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal

# ======================================================
# DELETE PROPOSAL
# ======================================================
@router.delete("/{proposal_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_proposal(proposal_id: UUID, db: Session = Depends(get_db)):
    deleted = proposal_service.delete(db, proposal_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return None
