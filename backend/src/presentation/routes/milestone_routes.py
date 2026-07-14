from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.milestone import (
    MilestoneCreate,
    MilestoneUpdate,
    MilestoneResponse,
)
from backend.src.services.milestone_service import (
    milestone_service,
)

router = APIRouter(
    tags=["Milestones"],
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[MilestoneResponse],
)
def get_all_milestones(
    db: Session = Depends(get_db),
):
    return milestone_service.get_all(db)


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{milestone_id}",
    response_model=MilestoneResponse,
)
def get_milestone(
    milestone_id: UUID,
    db: Session = Depends(get_db),
):
    milestone = milestone_service.get_by_id(
        db=db,
        milestone_id=milestone_id,
    )

    if milestone is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found",
        )

    return milestone


# ==========================================================
# GET BY CONTRACT
# ==========================================================

@router.get(
    "/contract/{contract_id}",
    response_model=list[MilestoneResponse],
)
def get_contract_milestones(
    contract_id: UUID,
    db: Session = Depends(get_db),
):
    return milestone_service.get_by_contract(
        db=db,
        contract_id=contract_id,
    )


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_milestone(
    data: MilestoneCreate,
    db: Session = Depends(get_db),
):
    try:
        return milestone_service.create(
            db=db,
            data=data,
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
    "/{milestone_id}",
    response_model=MilestoneResponse,
)
def update_milestone(
    milestone_id: UUID,
    data: MilestoneUpdate,
    db: Session = Depends(get_db),
):
    try:
        milestone = milestone_service.update(
            db=db,
            milestone_id=milestone_id,
            data=data,
        )

        if milestone is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Milestone not found",
            )

        return milestone

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==========================================================
# UPDATE STATUS
# ==========================================================

@router.patch(
    "/{milestone_id}/status",
    response_model=MilestoneResponse,
)
def update_status(
    milestone_id: UUID,
    status_value: str,
    db: Session = Depends(get_db),
):
    try:
        milestone = milestone_service.update_status(
            db=db,
            milestone_id=milestone_id,
            status=status_value,
        )

        if milestone is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Milestone not found",
            )

        return milestone

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{milestone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_milestone(
    milestone_id: UUID,
    db: Session = Depends(get_db),
):
    success = milestone_service.delete(
        db=db,
        milestone_id=milestone_id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Milestone not found",
        )

    return None