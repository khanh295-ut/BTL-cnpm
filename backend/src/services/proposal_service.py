from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from backend.src.models.proposal import Proposal
from backend.src.schemas.proposal import (
    ProposalCreate,
    ProposalUpdate,
)


class ProposalService:
    # =====================================================
    # GET ALL
    # =====================================================
    def get_all(self, db: Session):
        try:
            return db.query(Proposal).all()
        except Exception as e:
            print(f"❌ Lỗi lấy proposals: {e}")
            return []

    # =====================================================
    # GET BY ID
    # =====================================================
    def get_by_id(self, db: Session, proposal_id: UUID):
        try:
            return db.query(Proposal).filter(Proposal.id == proposal_id).first()
        except Exception as e:
            print(f"❌ Lỗi lấy proposal theo ID: {e}")
            return None

    # =====================================================
    # CREATE
    # =====================================================
    def create(self, db: Session, data: ProposalCreate) -> Proposal:
        try:
            proposal = Proposal(
                project_id=data.project_id,
                expert_id=data.expert_id,
                bid_amount=data.bid_amount,
                cover_letter=data.cover_letter,
                estimated_days=data.estimated_days,
                status="PENDING",
                created_at=datetime.utcnow(),  # nếu model có field này
            )
            db.add(proposal)
            db.commit()
            db.refresh(proposal)
            return proposal
        except Exception as e:
            print(f"❌ Lỗi tạo proposal: {e}")
            db.rollback()
            raise

    # =====================================================
    # UPDATE
    # =====================================================
    def update(self, db: Session, proposal_id: UUID, data: ProposalUpdate):
        proposal = self.get_by_id(db, proposal_id)
        if proposal is None:
            return None

        try:
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(proposal, key, value)

            proposal.updated_at = datetime.utcnow()  # nếu có field updated_at
            db.commit()
            db.refresh(proposal)
            return proposal
        except Exception as e:
            print(f"❌ Lỗi cập nhật proposal: {e}")
            db.rollback()
            return None

    # =====================================================
    # UPDATE STATUS
    # =====================================================
    def update_status(self, db: Session, proposal_id: UUID, status: str):
        proposal = self.get_by_id(db, proposal_id)
        if proposal is None:
            return None

        try:
            proposal.status = status
            proposal.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(proposal)
            return proposal
        except Exception as e:
            print(f"❌ Lỗi cập nhật status proposal: {e}")
            db.rollback()
            return None

    # =====================================================
    # DELETE
    # =====================================================
    def delete(self, db: Session, proposal_id: UUID) -> bool:
        proposal = self.get_by_id(db, proposal_id)
        if proposal is None:
            return False

        try:
            db.delete(proposal)
            db.commit()
            return True
        except Exception as e:
            print(f"❌ Lỗi xóa proposal: {e}")
            db.rollback()
            return False


proposal_service = ProposalService()
