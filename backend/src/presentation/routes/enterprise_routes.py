from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.enterprise import (
    EnterpriseCreate,
    EnterpriseUpdate,
    EnterpriseResponse,
)
from backend.src.services.enterprise_service import enterprise_service

router = APIRouter(
    prefix="/enterprises",
    tags=["Enterprises"],
)


# =====================================================
# GET ALL
# =====================================================

@router.get(
    "",
    response_model=List[EnterpriseResponse],
)
def get_enterprises(
    db: Session = Depends(get_db),
):
    return enterprise_service.get_all(db)


# =====================================================
# GET BY ID
# =====================================================

@router.get(
    "/{enterprise_id}",
    response_model=EnterpriseResponse,
)
def get_enterprise(
    enterprise_id: UUID,
    db: Session = Depends(get_db),
):
    enterprise = enterprise_service.get_by_id(
        db,
        enterprise_id,
    )

    if enterprise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise not found",
        )

    return enterprise


# =====================================================
# CREATE
# =====================================================

@router.post(
    "",
    response_model=EnterpriseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_enterprise(
    data: EnterpriseCreate,
    db: Session = Depends(get_db),
):
    return enterprise_service.create(
        db,
        data,
    )


# =====================================================
# UPDATE
# =====================================================

@router.put(
    "/{enterprise_id}",
    response_model=EnterpriseResponse,
)
def update_enterprise(
    enterprise_id: UUID,
    data: EnterpriseUpdate,
    db: Session = Depends(get_db),
):
    enterprise = enterprise_service.update(
        db,
        enterprise_id,
        data,
    )

    if enterprise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise not found",
        )

    return enterprise


# =====================================================
# DELETE
# =====================================================

@router.delete(
    "/{enterprise_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_enterprise(
    enterprise_id: UUID,
    db: Session = Depends(get_db),
):
    success = enterprise_service.delete(
        db,
        enterprise_id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise not found",
        )

    return