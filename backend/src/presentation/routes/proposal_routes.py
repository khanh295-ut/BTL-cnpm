from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.proposal import (
    ProposalCreate,
    ProposalUpdate,
    ProposalResponse,
    ProposalStatusUpdate,
)
from backend.src.services.proposal_service import proposal_service

# ✅ Khớp với frontend: /api/proposals
router = APIRouter(
    prefix="/api/proposals",
    tags=["Proposals"],
)

# =====================================================
# GET ALL
# =====================================================
@router.get("", response_model=list[ProposalResponse])
def get_all_proposals(db: Session = Depends(get_db)):
    return proposal_service.get_all(db)

# =====================================================
# GET BY ID
# =====================================================
@router.get("/{proposal_id}", response_model=ProposalResponse)
def get_proposal(proposal_id: UUID, db: Session = Depends(get_db)):
    proposal = proposal_service.get_by_id(db, proposal_id)
    if proposal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    return proposal

# =====================================================
# CREATE
# =====================================================
@router.post("", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
def create_proposal(data: ProposalCreate, db: Session = Depends(get_db)):
    return proposal_service.create(db, data)

# =====================================================
# UPDATE
# =====================================================
@router.put("/{proposal_id}", response_model=ProposalResponse)
def update_proposal(proposal_id: UUID, data: ProposalUpdate, db: Session = Depends(get_db)):
    proposal = proposal_service.update(db, proposal_id, data)
    if proposal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    return proposal

# =====================================================
# UPDATE STATUS
# =====================================================
@router.patch("/{proposal_id}/status", response_model=ProposalResponse)
def update_status(proposal_id: UUID, data: ProposalStatusUpdate, db: Session = Depends(get_db)):
    proposal = proposal_service.update_status(db, proposal_id, data.status)
    if proposal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    return proposal

# =====================================================
# DELETE
# =====================================================
@router.delete("/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_proposal(proposal_id: UUID, db: Session = Depends(get_db)):
    deleted = proposal_service.delete(db, proposal_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    return None
