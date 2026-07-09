# backend/src/services/contract_service.py
from uuid import UUID
from sqlalchemy.orm import Session
from backend.src.models.contract import Contract
from backend.src.schemas.contract import ContractCreate, ContractUpdate

class ContractService:
    def get_all(self, db: Session):
        return db.query(Contract).order_by(Contract.created_at.desc()).all()

    def get_by_id(self, db: Session, contract_id: UUID):
        return db.query(Contract).filter(Contract.id == contract_id).first()

    def create(self, db: Session, data: ContractCreate):
        contract = Contract(
            project_id=data.project_id,
            expert_id=data.expert_id,
            terms=data.terms,
            status=data.status,
        )
        db.add(contract)
        db.commit()
        db.refresh(contract)
        return contract

    def update(self, db: Session, contract_id: UUID, data: ContractUpdate):
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            return None
        if data.terms is not None:
            contract.terms = data.terms
        if data.status is not None:
            contract.status = data.status
        db.commit()
        db.refresh(contract)
        return contract

    def delete(self, db: Session, contract_id: UUID):
        contract = db.query(Contract).filter(Contract.id == contract_id).first()
        if not contract:
            return False
        db.delete(contract)
        db.commit()
        return True

contract_service = ContractService()
