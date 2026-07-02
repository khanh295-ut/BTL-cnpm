from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.application.content_use_cases import (
    create_proposal,
    list_proposals,
    accept_proposal
)

from backend.src.schemas.proposal import (
    ProposalCreate,
    ProposalResponse
)

router = APIRouter(prefix="/proposals", tags=["Proposals"])


@router.get("/", response_model=list[ProposalResponse])
def get_proposals(db: Session = Depends(get_db)):
    return list_proposals(db)


@router.post("/", response_model=ProposalResponse)
def create(data: ProposalCreate, db: Session = Depends(get_db)):
    return create_proposal(
        db,
        data.project_id,
        data.expert_id,
        data.price,
        data.comment
    )


@router.post("/{proposal_id}/accept")
def accept(proposal_id: str, db: Session = Depends(get_db)):
    return accept_proposal(db, proposal_id)