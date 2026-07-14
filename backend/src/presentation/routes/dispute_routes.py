from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.dispute import (
    DisputeAssignAdminRequest,
    DisputeCloseRequest,
    DisputeCreate,
    DisputeResolveRequest,
    DisputeResponse,
    DisputeStatusUpdate,
    DisputeUpdate,
)
from backend.src.services.dispute_service import (
    dispute_service,
)


router = APIRouter(
    tags=["Disputes"],
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[DisputeResponse],
)
def get_all_disputes(
    db: Session = Depends(get_db),
):
    return dispute_service.get_all(db)


# ==========================================================
# GET BY CONTRACT
#
# Các route tĩnh phải đặt trước "/{dispute_id}"
# để tránh FastAPI hiểu "contract" là UUID.
# ==========================================================

@router.get(
    "/contract/{contract_id}",
    response_model=list[DisputeResponse],
)
def get_disputes_by_contract(
    contract_id: UUID,
    db: Session = Depends(get_db),
):
    return dispute_service.get_by_contract(
        db=db,
        contract_id=contract_id,
    )


# ==========================================================
# GET BY USER
# ==========================================================

@router.get(
    "/user/{user_id}",
    response_model=list[DisputeResponse],
)
def get_disputes_by_user(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    return dispute_service.get_by_user(
        db=db,
        user_id=user_id,
    )


# ==========================================================
# GET BY ADMIN
# ==========================================================

@router.get(
    "/admin/{admin_id}",
    response_model=list[DisputeResponse],
)
def get_disputes_by_admin(
    admin_id: UUID,
    db: Session = Depends(get_db),
):
    return dispute_service.get_by_admin(
        db=db,
        admin_id=admin_id,
    )


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "",
    response_model=DisputeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_dispute(
    data: DisputeCreate,
    db: Session = Depends(get_db),
):
    try:
        return dispute_service.create(
            db=db,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{dispute_id}",
    response_model=DisputeResponse,
)
def get_dispute(
    dispute_id: UUID,
    db: Session = Depends(get_db),
):
    dispute = dispute_service.get_by_id(
        db=db,
        dispute_id=dispute_id,
    )

    if dispute is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispute not found.",
        )

    return dispute


# ==========================================================
# UPDATE
# ==========================================================

@router.put(
    "/{dispute_id}",
    response_model=DisputeResponse,
)
def update_dispute(
    dispute_id: UUID,
    data: DisputeUpdate,
    db: Session = Depends(get_db),
):
    try:
        dispute = dispute_service.update(
            db=db,
            dispute_id=dispute_id,
            data=data,
        )

        if dispute is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found.",
            )

        return dispute

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# ASSIGN ADMIN
# ==========================================================

@router.patch(
    "/{dispute_id}/assign-admin",
    response_model=DisputeResponse,
)
def assign_dispute_admin(
    dispute_id: UUID,
    data: DisputeAssignAdminRequest,
    db: Session = Depends(get_db),
):
    try:
        dispute = dispute_service.assign_admin(
            db=db,
            dispute_id=dispute_id,
            data=data,
        )

        if dispute is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found.",
            )

        return dispute

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# UPDATE STATUS
# ==========================================================

@router.patch(
    "/{dispute_id}/status",
    response_model=DisputeResponse,
)
def update_dispute_status(
    dispute_id: UUID,
    data: DisputeStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        dispute = dispute_service.update_status(
            db=db,
            dispute_id=dispute_id,
            data=data,
        )

        if dispute is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found.",
            )

        return dispute

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# RESOLVE
# ==========================================================

@router.patch(
    "/{dispute_id}/resolve",
    response_model=DisputeResponse,
)
def resolve_dispute(
    dispute_id: UUID,
    data: DisputeResolveRequest,
    db: Session = Depends(get_db),
):
    try:
        dispute = dispute_service.resolve(
            db=db,
            dispute_id=dispute_id,
            data=data,
        )

        if dispute is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found.",
            )

        return dispute

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# CLOSE
# ==========================================================

@router.patch(
    "/{dispute_id}/close",
    response_model=DisputeResponse,
)
def close_dispute(
    dispute_id: UUID,
    data: DisputeCloseRequest,
    db: Session = Depends(get_db),
):
    try:
        dispute = dispute_service.close(
            db=db,
            dispute_id=dispute_id,
            data=data,
        )

        if dispute is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found.",
            )

        return dispute

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# CANCEL
# ==========================================================

@router.patch(
    "/{dispute_id}/cancel",
    response_model=DisputeResponse,
)
def cancel_dispute(
    dispute_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        dispute = dispute_service.cancel(
            db=db,
            dispute_id=dispute_id,
        )

        if dispute is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found.",
            )

        return dispute

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{dispute_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_dispute(
    dispute_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        deleted = dispute_service.delete(
            db=db,
            dispute_id=dispute_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dispute not found.",
            )

        return None

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc