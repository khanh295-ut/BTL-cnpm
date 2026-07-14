from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.recommendation import (
    RecommendationCreate,
    RecommendationFeedbackUpdate,
    RecommendationGenerateRequest,
    RecommendationGenerateResponse,
    RecommendationResponse,
    RecommendationUpdate,
)
from backend.src.services.recommendation_service import (
    recommendation_service,
)


router = APIRouter(
    tags=["Recommendations"],
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[RecommendationResponse],
)
def get_all_recommendations(
    db: Session = Depends(get_db),
):
    return recommendation_service.get_all(db)


# ==========================================================
# GENERATE
#
# Route tĩnh phải đặt trước "/{recommendation_id}"
# để tránh FastAPI hiểu "generate" là UUID.
# ==========================================================

@router.post(
    "/generate",
    response_model=RecommendationGenerateResponse,
)
def generate_recommendations(
    data: RecommendationGenerateRequest,
    db: Session = Depends(get_db),
):
    try:
        return recommendation_service.generate(
            db=db,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# GENERATE BY PROJECT
#
# Endpoint ngắn gọn để frontend gọi trực tiếp bằng project_id.
# ==========================================================

@router.post(
    "/project/{project_id}/generate",
    response_model=RecommendationGenerateResponse,
)
def generate_recommendations_by_project(
    project_id: UUID,
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    force_refresh: bool = Query(
        default=False,
    ),
    algorithm_version: str = Query(
        default="v1.0",
        min_length=1,
        max_length=50,
    ),
    db: Session = Depends(get_db),
):
    try:
        request = RecommendationGenerateRequest(
            project_id=project_id,
            limit=limit,
            force_refresh=force_refresh,
            algorithm_version=algorithm_version,
        )

        return recommendation_service.generate(
            db=db,
            data=request,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# GET BY PROJECT
# ==========================================================

@router.get(
    "/project/{project_id}",
    response_model=list[RecommendationResponse],
)
def get_recommendations_by_project(
    project_id: UUID,
    limit: int | None = Query(
        default=None,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    return recommendation_service.get_by_project(
        db=db,
        project_id=project_id,
        limit=limit,
    )


# ==========================================================
# GET BY EXPERT
# ==========================================================

@router.get(
    "/expert/{expert_id}",
    response_model=list[RecommendationResponse],
)
def get_recommendations_by_expert(
    expert_id: UUID,
    db: Session = Depends(get_db),
):
    return recommendation_service.get_by_expert(
        db=db,
        expert_id=expert_id,
    )


# ==========================================================
# CREATE MANUALLY
# ==========================================================

@router.post(
    "",
    response_model=RecommendationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recommendation(
    data: RecommendationCreate,
    db: Session = Depends(get_db),
):
    try:
        return recommendation_service.create(
            db=db,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{recommendation_id}",
    response_model=RecommendationResponse,
)
def get_recommendation(
    recommendation_id: UUID,
    db: Session = Depends(get_db),
):
    recommendation = (
        recommendation_service.get_by_id(
            db=db,
            recommendation_id=(
                recommendation_id
            ),
        )
    )

    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found.",
        )

    return recommendation


# ==========================================================
# UPDATE
# ==========================================================

@router.put(
    "/{recommendation_id}",
    response_model=RecommendationResponse,
)
def update_recommendation(
    recommendation_id: UUID,
    data: RecommendationUpdate,
    db: Session = Depends(get_db),
):
    try:
        recommendation = (
            recommendation_service.update(
                db=db,
                recommendation_id=(
                    recommendation_id
                ),
                data=data,
            )
        )

        if recommendation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found.",
            )

        return recommendation

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# UPDATE FEEDBACK
# ==========================================================

@router.patch(
    "/{recommendation_id}/feedback",
    response_model=RecommendationResponse,
)
def update_recommendation_feedback(
    recommendation_id: UUID,
    data: RecommendationFeedbackUpdate,
    db: Session = Depends(get_db),
):
    try:
        recommendation = (
            recommendation_service.update_feedback(
                db=db,
                recommendation_id=(
                    recommendation_id
                ),
                data=data,
            )
        )

        if recommendation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found.",
            )

        return recommendation

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# DELETE BY PROJECT
#
# Route tĩnh phải đặt trước "/{recommendation_id}" về mặt
# khai báo nếu dùng cùng HTTP method DELETE.
# ==========================================================

@router.delete(
    "/project/{project_id}",
)
def delete_recommendations_by_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        deleted_count = (
            recommendation_service
            .delete_by_project(
                db=db,
                project_id=project_id,
            )
        )

        return {
            "message": (
                "Recommendations deleted successfully."
            ),
            "deleted_count": deleted_count,
            "project_id": project_id,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# DELETE BY ID
# ==========================================================

@router.delete(
    "/{recommendation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_recommendation(
    recommendation_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        deleted = recommendation_service.delete(
            db=db,
            recommendation_id=(
                recommendation_id
            ),
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recommendation not found.",
            )

        return None

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc