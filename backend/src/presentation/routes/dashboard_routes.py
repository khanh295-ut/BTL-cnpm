from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.services.dashboard_service import DashboardService
from backend.src.schemas.dashboard import (
    DashboardResponse,
    RecentProjectResponse,
    RecentProposalResponse,
    RecentReviewResponse,
)

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)

service = DashboardService()

@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)):
    return service.get_dashboard(db)

@router.get("/recent-projects", response_model=list[RecentProjectResponse])
def recent_projects(db: Session = Depends(get_db)):
    return service.recent_projects(db)

@router.get("/recent-proposals", response_model=list[RecentProposalResponse])
def recent_proposals(db: Session = Depends(get_db)):
    return service.recent_proposals(db)

@router.get("/recent-reviews", response_model=list[RecentReviewResponse])
def recent_reviews(db: Session = Depends(get_db)):
    return service.recent_reviews(db)
