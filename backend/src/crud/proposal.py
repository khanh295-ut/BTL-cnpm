from sqlalchemy.orm import Session
from backend.src.models.proposal import Proposal
from backend.src.schemas.proposal import ProposalCreate

def get_all_proposals(db: Session):
    """Lấy danh sách tất cả đề xuất"""
    return db.query(Proposal).all()

def create_proposal(db: Session, proposal_in: ProposalCreate):
    """
    Tạo đề xuất mới với việc gán thủ công từng trường 
    để đảm bảo khớp với Model Database.
    """
    db_proposal = Proposal(
        project_id=proposal_in.project_id,
        expert_id=proposal_in.expert_id,
        cover_letter=proposal_in.cover_letter,
        bid_amount=proposal_in.bid_amount,
        estimated_days=proposal_in.estimated_days,
        status="PENDING" # Giá trị mặc định
    )
    
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    return db_proposal

def get_proposal_by_id(db: Session, proposal_id: str):
    """Lấy đề xuất theo ID"""
    return db.query(Proposal).filter(Proposal.id == proposal_id).first()