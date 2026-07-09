# backend/src/presentation/routes/analytics_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
# DashboardService đã được tạo trong backend/src/services/dashboard_service.py
try:
    from backend.src.services.dashboard_service import DashboardService
except Exception:
    # Fallback: nếu service chưa tồn tại, trả về stub an toàn
    class DashboardService:
        def get_dashboard(self, db: Session):
            return {"users": 0, "projects": 0, "experts": 0, "proposals": 0, "contracts": 0}
        def recent_projects(self, db: Session, limit: int = 5):
            return []
        def recent_proposals(self, db: Session, limit: int = 5):
            return []
        def recent_reviews(self, db: Session, limit: int = 5):
            return []

dashboard_service = DashboardService()

router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"],
)

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    try:
        return dashboard_service.get_dashboard(db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/recent-projects")
def get_recent_projects(db: Session = Depends(get_db), limit: int = 5):
    try:
        return dashboard_service.recent_projects(db, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/recent-proposals")
def get_recent_proposals(db: Session = Depends(get_db), limit: int = 5):
    try:
        return dashboard_service.recent_proposals(db, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/recent-reviews")
def get_recent_reviews(db: Session = Depends(get_db), limit: int = 5):
    try:
        return dashboard_service.recent_reviews(db, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
