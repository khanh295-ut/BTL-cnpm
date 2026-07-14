from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.deliverable import (
    DeliverableCreate,
    DeliverableReview,
    DeliverableResponse,
    DeliverableUpdate,
)
from backend.src.services.deliverable_service import (
    deliverable_service,
)

router = APIRouter(
    tags=["Deliverables"],
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[DeliverableResponse],
)
def get_all_deliverables(
    db: Session = Depends(get_db),
):
    return deliverable_service.get_all(db)


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{deliverable_id}",
    response_model=DeliverableResponse,
)
def get_deliverable(
    deliverable_id: UUID,
    db: Session = Depends(get_db),
):
    deliverable = deliverable_service.get_by_id(
        db=db,
        deliverable_id=deliverable_id,
    )

    if deliverable is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deliverable not found",
        )

    return deliverable


# ==========================================================
# GET BY MILESTONE
# ==========================================================

@router.get(
    "/milestone/{milestone_id}",
    response_model=list[DeliverableResponse],
)
def get_milestone_deliverables(
    milestone_id: UUID,
    db: Session = Depends(get_db),
):
    return deliverable_service.get_by_milestone(
        db=db,
        milestone_id=milestone_id,
    )


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "",
    response_model=DeliverableResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_deliverable(
    data: DeliverableCreate,
    db: Session = Depends(get_db),
):
    try:
        return deliverable_service.create(
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
    "/{deliverable_id}",
    response_model=DeliverableResponse,
)
def update_deliverable(
    deliverable_id: UUID,
    data: DeliverableUpdate,
    db: Session = Depends(get_db),
):
    try:
        deliverable = deliverable_service.update(
            db=db,
            deliverable_id=deliverable_id,
            data=data,
        )

        if deliverable is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deliverable not found",
            )

        return deliverable

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==========================================================
# SUBMIT
# ==========================================================

@router.patch(
    "/{deliverable_id}/submit",
    response_model=DeliverableResponse,
)
def submit_deliverable(
    deliverable_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        deliverable = deliverable_service.submit(
            db=db,
            deliverable_id=deliverable_id,
        )

        if deliverable is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deliverable not found",
            )

        return deliverable

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==========================================================
# REVIEW
# ==========================================================

@router.patch(
    "/{deliverable_id}/review",
    response_model=DeliverableResponse,
)
def review_deliverable(
    deliverable_id: UUID,
    data: DeliverableReview,
    db: Session = Depends(get_db),
):
    try:
        deliverable = deliverable_service.review(
            db=db,
            deliverable_id=deliverable_id,
            data=data,
        )

        if deliverable is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deliverable not found",
            )

        return deliverable

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{deliverable_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_deliverable(
    deliverable_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        success = deliverable_service.delete(
            db=db,
            deliverable_id=deliverable_id,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deliverable not found",
            )

        return None

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )