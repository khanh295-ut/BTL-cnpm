from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.services.statistics_service import StatisticsService
from backend.src.schemas.statistics import (
    MonthlyStat,
    RevenueResponse,
    RatingDistribution
)

router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"]
)

service = StatisticsService()


# =========================
# PROJECT BY MONTH
# =========================
@router.get("/projects", response_model=list[MonthlyStat])
def project_stats(db: Session = Depends(get_db)):
    return service.project_by_month(db)


# =========================
# PROPOSAL BY MONTH
# =========================
@router.get("/proposals", response_model=list[MonthlyStat])
def proposal_stats(db: Session = Depends(get_db)):
    return service.proposal_by_month(db)


# =========================
# REVENUE
# =========================
@router.get("/revenue", response_model=RevenueResponse)
def revenue(db: Session = Depends(get_db)):
    return service.revenue(db)


# =========================
# RATING DISTRIBUTION
# =========================
@router.get("/ratings", response_model=list[RatingDistribution])
def ratings(db: Session = Depends(get_db)):
    return service.rating_distribution(db)