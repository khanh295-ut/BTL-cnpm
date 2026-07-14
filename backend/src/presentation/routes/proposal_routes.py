# backend/src/presentation/routes/proposal_routes.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.proposal import (
    ProposalCreate,
    ProposalResponse,
    ProposalStatusUpdate,
    ProposalUpdate,
)
from backend.src.services.proposal_service import proposal_service

router = APIRouter(
    tags=["Proposals"],
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[ProposalResponse],
)
def get_all_proposals(
    db: Session = Depends(get_db),
):
    return proposal_service.get_all(db)


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{proposal_id}",
    response_model=ProposalResponse,
)
def get_proposal(
    proposal_id: UUID,
    db: Session = Depends(get_db),
):
    proposal = proposal_service.get_by_id(
        db,
        proposal_id,
    )

    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    return proposal


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_proposal(
    data: ProposalCreate,
    db: Session = Depends(get_db),
):
    try:
        return proposal_service.create(
            db,
            data,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==========================================================
# UPDATE
# ==========================================================

@router.put(
    "/{proposal_id}",
    response_model=ProposalResponse,
)
def update_proposal(
    proposal_id: UUID,
    data: ProposalUpdate,
    db: Session = Depends(get_db),
):
    try:
        proposal = proposal_service.update(
            db,
            proposal_id,
            data,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    return proposal


# ==========================================================
# UPDATE STATUS
# ==========================================================

@router.patch(
    "/{proposal_id}/status",
    response_model=ProposalResponse,
)
def update_status(
    proposal_id: UUID,
    data: ProposalStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        proposal = proposal_service.update_status(
            db=db,
            proposal_id=proposal_id,
            status=data.status,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    return proposal


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{proposal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_proposal(
    proposal_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = proposal_service.delete(
        db,
        proposal_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found",
        )

    return None