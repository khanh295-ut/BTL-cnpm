# backend/src/presentation/routes/statistics_routes.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.statistics import (
    MonthlyStat,
    RatingDistribution,
    RevenueResponse,
)
from backend.src.services.statistics_service import statistics_service


# ==========================================================
# ROUTER
#
# Quy ước:
# - app.py thêm prefix "/api"
# - all_routes.py thêm prefix "/statistics"
# - file này không thêm prefix
#
# Endpoint cuối:
# GET /api/statistics/dashboard
# GET /api/statistics/projects
# GET /api/statistics/proposals
# GET /api/statistics/revenue
# GET /api/statistics/contract-value
# GET /api/statistics/ratings
# GET /api/statistics/skills
# GET /api/statistics/activities
# ==========================================================

router = APIRouter(
    tags=["Statistics"],
)


# ==========================================================
# DASHBOARD SUMMARY
# ==========================================================

@router.get(
    "/dashboard",
    summary="Lấy thống kê tổng quan hệ thống",
)
def dashboard_statistics(
    db: Session = Depends(get_db),
):
    """
    Trả về các chỉ số tổng quan:

    - Tổng doanh thu thực tế
    - Số chuyên gia hoạt động
    - Số dự án hoàn thành
    - Số dự án đang chờ hoặc đang xử lý
    - Tổng dự án
    - Tổng chuyên gia
    - Tổng proposal
    - Tổng hợp đồng
    - Tổng giao dịch
    """

    try:
        return statistics_service.dashboard_summary(db)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể tải dữ liệu thống kê tổng quan: "
                f"{str(exc)}"
            ),
        ) from exc


# ==========================================================
# PROJECTS BY MONTH
# ==========================================================

@router.get(
    "/projects",
    response_model=list[MonthlyStat],
    summary="Thống kê dự án theo tháng",
)
def project_statistics(
    db: Session = Depends(get_db),
):
    try:
        return statistics_service.project_by_month(db)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể thống kê dự án theo tháng: "
                f"{str(exc)}"
            ),
        ) from exc


# ==========================================================
# PROPOSALS BY MONTH
# ==========================================================

@router.get(
    "/proposals",
    response_model=list[MonthlyStat],
    summary="Thống kê đề xuất theo tháng",
)
def proposal_statistics(
    db: Session = Depends(get_db),
):
    try:
        return statistics_service.proposal_by_month(db)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể thống kê proposal theo tháng: "
                f"{str(exc)}"
            ),
        ) from exc


# ==========================================================
# REVENUE
# ==========================================================

@router.get(
    "/revenue",
    response_model=RevenueResponse,
    summary="Tính tổng doanh thu thực tế",
)
def revenue_statistics(
    db: Session = Depends(get_db),
):
    """
    Doanh thu chỉ tính từ các Payment có trạng thái:

    - SUCCESS
    - COMPLETED
    - RELEASED

    Payment ở trạng thái PENDING chưa được tính là doanh thu.
    """

    try:
        return statistics_service.revenue(db)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể tính tổng doanh thu: "
                f"{str(exc)}"
            ),
        ) from exc


# ==========================================================
# TOTAL CONTRACT VALUE
# ==========================================================

@router.get(
    "/contract-value",
    summary="Tính tổng giá trị hợp đồng",
)
def total_contract_value(
    db: Session = Depends(get_db),
):
    """
    Tổng giá trị của toàn bộ hợp đồng.

    Chỉ số này khác doanh thu:
    - Giá trị hợp đồng có thể bao gồm Payment chưa hoàn tất.
    - Doanh thu chỉ tính các Payment thành công hoặc đã giải ngân.
    """

    try:
        return statistics_service.total_contract_value(db)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể tính tổng giá trị hợp đồng: "
                f"{str(exc)}"
            ),
        ) from exc


# ==========================================================
# RATING DISTRIBUTION
# ==========================================================

@router.get(
    "/ratings",
    response_model=list[RatingDistribution],
    summary="Thống kê phân bố đánh giá",
)
def rating_statistics(
    db: Session = Depends(get_db),
):
    try:
        return statistics_service.rating_distribution(db)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể thống kê đánh giá: "
                f"{str(exc)}"
            ),
        ) from exc


# ==========================================================
# POPULAR SKILLS
# ==========================================================

@router.get(
    "/skills",
    summary="Lấy danh sách kỹ năng AI phổ biến",
)
def popular_skills_statistics(
    limit: int = Query(
        default=5,
        ge=1,
        le=50,
        description="Số kỹ năng tối đa cần trả về",
    ),
    db: Session = Depends(get_db),
):
    try:
        return statistics_service.popular_skills(
            db=db,
            limit=limit,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể thống kê kỹ năng phổ biến: "
                f"{str(exc)}"
            ),
        ) from exc


# ==========================================================
# RECENT ACTIVITIES
# ==========================================================

@router.get(
    "/activities",
    summary="Lấy hoạt động gần đây của hệ thống",
)
def recent_activities_statistics(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Số hoạt động tối đa cần trả về",
    ),
    db: Session = Depends(get_db),
):
    try:
        return statistics_service.recent_activities(
            db=db,
            limit=limit,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể tải hoạt động gần đây: "
                f"{str(exc)}"
            ),
        ) from exc


# ==========================================================
# COMPLETE ANALYTICS RESPONSE
# ==========================================================

@router.get(
    "/overview",
    summary="Lấy toàn bộ dữ liệu cho trang Analytics",
)
def statistics_overview(
    skill_limit: int = Query(
        default=5,
        ge=1,
        le=50,
    ),
    activity_limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    """
    Endpoint tổng hợp dành cho frontend Analytics.

    Frontend chỉ cần gọi:

        GET /api/statistics/overview

    thay vì gọi riêng nhiều endpoint.
    """

    try:
        return {
            "summary": (
                statistics_service.dashboard_summary(db)
            ),
            "revenue": (
                statistics_service.revenue(db)
            ),
            "contract_value": (
                statistics_service.total_contract_value(db)
            ),
            "projects_by_month": (
                statistics_service.project_by_month(db)
            ),
            "proposals_by_month": (
                statistics_service.proposal_by_month(db)
            ),
            "rating_distribution": (
                statistics_service.rating_distribution(db)
            ),
            "popular_skills": (
                statistics_service.popular_skills(
                    db=db,
                    limit=skill_limit,
                )
            ),
            "recent_activities": (
                statistics_service.recent_activities(
                    db=db,
                    limit=activity_limit,
                )
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Không thể tải dữ liệu Analytics: "
                f"{str(exc)}"
            ),
        ) from exc