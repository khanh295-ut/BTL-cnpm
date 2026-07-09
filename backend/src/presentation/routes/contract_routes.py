# backend/src/presentation/routes/contract_routes.py
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.contract import ContractResponse, ContractCreate, ContractUpdate
from backend.src.services.contract_service import contract_service

router = APIRouter(
    prefix="/api/contracts",
    tags=["Contracts"],
)

@router.get("", response_model=list[ContractResponse])
def get_all_contracts(db: Session = Depends(get_db)):
    return contract_service.get_all(db)

@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(contract_id: UUID, db: Session = Depends(get_db)):
    contract = contract_service.get_by_id(db, contract_id)
    if contract is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return contract

@router.post("", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(data: ContractCreate, db: Session = Depends(get_db)):
    return contract_service.create(db, data)

@router.put("/{contract_id}", response_model=ContractResponse)
def update_contract(contract_id: UUID, data: ContractUpdate, db: Session = Depends(get_db)):
    contract = contract_service.update(db, contract_id, data)
    if contract is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return contract

@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(contract_id: UUID, db: Session = Depends(get_db)):
    deleted = contract_service.delete(db, contract_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return None
