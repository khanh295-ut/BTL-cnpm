from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.dashboard import (
    DashboardResponse,
    RecentProjectResponse,
    RecentProposalResponse,
    RecentReviewResponse,
)
from backend.src.services.dashboard_service import DashboardService

router = APIRouter(tags=["Analytics"])
service = DashboardService()


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)):
    return service.get_dashboard(db)


@router.get("/recent-projects", response_model=list[RecentProjectResponse])
def recent_projects(
    limit: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.recent_projects(db, limit=limit)


@router.get("/recent-proposals", response_model=list[RecentProposalResponse])
def recent_proposals(
    limit: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.recent_proposals(db, limit=limit)


@router.get("/recent-reviews", response_model=list[RecentReviewResponse])
def recent_reviews(
    limit: int = Query(5, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.recent_reviews(db, limit=limit)
