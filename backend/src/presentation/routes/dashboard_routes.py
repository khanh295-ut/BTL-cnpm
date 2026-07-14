# backend/src/presentation/routes/analytics_routes.py

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.dashboard import (
    DashboardResponse,
    RecentProjectResponse,
    RecentProposalResponse,
    RecentReviewResponse,
)
from backend.src.services.dashboard_service import DashboardService


logger = logging.getLogger("AITasker.Analytics")

router = APIRouter(
    tags=["Analytics"],
)

dashboard_service = DashboardService()


# ==========================================================
# DASHBOARD
# ==========================================================

@router.get(
    "/dashboard",
    response_model=DashboardResponse,
)
def get_dashboard(
    db: Session = Depends(get_db),
):
    try:
        return dashboard_service.get_dashboard(db)

    except Exception as exc:
        db.rollback()
        logger.exception("Không thể tải dữ liệu Dashboard.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tải dữ liệu Dashboard.",
        ) from exc


# ==========================================================
# RECENT PROJECTS
# ==========================================================

@router.get(
    "/recent-projects",
    response_model=list[RecentProjectResponse],
)
def get_recent_projects(
    limit: int = Query(
        default=5,
        ge=1,
        le=100,
        description="Số lượng dự án gần nhất",
    ),
    db: Session = Depends(get_db),
):
    try:
        return dashboard_service.recent_projects(
            db,
            limit=limit,
        )

    except Exception as exc:
        db.rollback()
        logger.exception("Không thể tải danh sách dự án gần đây.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tải danh sách dự án gần đây.",
        ) from exc


# ==========================================================
# RECENT PROPOSALS
# ==========================================================

@router.get(
    "/recent-proposals",
    response_model=list[RecentProposalResponse],
)
def get_recent_proposals(
    limit: int = Query(
        default=5,
        ge=1,
        le=100,
        description="Số lượng đề xuất gần nhất",
    ),
    db: Session = Depends(get_db),
):
    try:
        return dashboard_service.recent_proposals(
            db,
            limit=limit,
        )

    except Exception as exc:
        db.rollback()
        logger.exception("Không thể tải danh sách đề xuất gần đây.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tải danh sách đề xuất gần đây.",
        ) from exc


# ==========================================================
# RECENT REVIEWS
# ==========================================================

@router.get(
    "/recent-reviews",
    response_model=list[RecentReviewResponse],
)
def get_recent_reviews(
    limit: int = Query(
        default=5,
        ge=1,
        le=100,
        description="Số lượng đánh giá gần nhất",
    ),
    db: Session = Depends(get_db),
):
    try:
        return dashboard_service.recent_reviews(
            db,
            limit=limit,
        )

    except Exception as exc:
        db.rollback()
        logger.exception("Không thể tải danh sách đánh giá gần đây.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tải danh sách đánh giá gần đây.",
        ) from exc