from __future__ import annotations

from decimal import Decimal
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
from backend.src.schemas.ai_service import (
    AIServiceCreate,
    AIServiceFeaturedUpdate,
    AIServiceFilter,
    AIServiceMarketplaceResponse,
    AIServiceResponse,
    AIServiceStatusUpdate,
    AIServiceUpdate,
    AIServiceViewResponse,
)
from backend.src.services.ai_service_service import (
    ai_service_service,
)


# ==========================================================
# ROUTER
#
# Prefix "/ai-services" được khai báo trong all_routes.py.
# File này KHÔNG khai báo prefix để tránh lặp URL.
# ==========================================================

router = APIRouter(
    tags=["AI Services Marketplace"],
)


# ==========================================================
# INTERNAL HELPER
# ==========================================================

def _raise_bad_request(exc: ValueError) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    ) from exc


# ==========================================================
# MARKETPLACE SEARCH
#
# Endpoint cuối:
# GET /api/ai-services/marketplace
#
# Chỉ trả các dịch vụ PUBLISHED.
# Các route tĩnh phải được đặt trước "/{service_id}".
# ==========================================================

@router.get(
    "/marketplace",
    response_model=AIServiceMarketplaceResponse,
)
def search_ai_service_marketplace(
    keyword: str | None = Query(
        default=None,
        max_length=255,
    ),
    category_id: UUID | None = Query(
        default=None,
    ),
    expert_id: UUID | None = Query(
        default=None,
    ),
    min_price: Decimal | None = Query(
        default=None,
        ge=0,
    ),
    max_price: Decimal | None = Query(
        default=None,
        ge=0,
    ),
    max_delivery_days: int | None = Query(
        default=None,
        ge=1,
        le=365,
    ),
    skill: str | None = Query(
        default=None,
        max_length=100,
    ),
    is_featured: bool | None = Query(
        default=None,
    ),
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=12,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
):
    try:
        filters = AIServiceFilter(
            keyword=keyword,
            category_id=category_id,
            expert_id=expert_id,
            min_price=min_price,
            max_price=max_price,
            max_delivery_days=max_delivery_days,
            skill=skill,
            status="PUBLISHED",
            is_featured=is_featured,
        )

        return ai_service_service.marketplace_search(
            db=db,
            filters=filters,
            page=page,
            page_size=page_size,
        )

    except ValueError as exc:
        _raise_bad_request(exc)


# ==========================================================
# MARKETPLACE DETAIL BY SLUG
#
# Endpoint cuối:
# GET /api/ai-services/marketplace/{slug}
#
# Chỉ trả dịch vụ PUBLISHED.
# Có thể tăng view_count tự động.
# ==========================================================

@router.get(
    "/marketplace/{slug}",
    response_model=AIServiceResponse,
)
def get_marketplace_service_by_slug(
    slug: str,
    increase_view: bool = Query(
        default=True,
    ),
    db: Session = Depends(get_db),
):
    service = ai_service_service.get_by_slug(
        db=db,
        slug=slug,
    )

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI service not found.",
        )

    current_status = str(
        service.status or ""
    ).strip().upper()

    if current_status != "PUBLISHED":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI service not found.",
        )

    if increase_view:
        try:
            updated_service = (
                ai_service_service.increment_view(
                    db=db,
                    service_id=service.id,
                )
            )

            if updated_service is not None:
                service = updated_service

        except ValueError as exc:
            _raise_bad_request(exc)

    return service


# ==========================================================
# GET ALL
#
# Endpoint quản trị:
# GET /api/ai-services
#
# Trả cả DRAFT, PENDING, PUBLISHED, REJECTED...
# Sau này nên bảo vệ bằng get_current_admin.
# ==========================================================

@router.get(
    "",
    response_model=list[AIServiceResponse],
)
def get_all_ai_services(
    db: Session = Depends(get_db),
):
    return ai_service_service.get_all(
        db=db,
    )


# ==========================================================
# GET BY EXPERT
#
# Endpoint cuối:
# GET /api/ai-services/expert/{expert_id}
# ==========================================================

@router.get(
    "/expert/{expert_id}",
    response_model=list[AIServiceResponse],
)
def get_ai_services_by_expert(
    expert_id: UUID,
    db: Session = Depends(get_db),
):
    return ai_service_service.get_by_expert(
        db=db,
        expert_id=expert_id,
    )


# ==========================================================
# GET BY CATEGORY
#
# Endpoint cuối:
# GET /api/ai-services/category/{category_id}
# ==========================================================

@router.get(
    "/category/{category_id}",
    response_model=list[AIServiceResponse],
)
def get_ai_services_by_category(
    category_id: UUID,
    db: Session = Depends(get_db),
):
    return ai_service_service.get_by_category(
        db=db,
        category_id=category_id,
    )


# ==========================================================
# GET BY SLUG - INTERNAL
#
# Endpoint cuối:
# GET /api/ai-services/slug/{slug}
#
# Có thể trả cả service chưa PUBLISHED.
# ==========================================================

@router.get(
    "/slug/{slug}",
    response_model=AIServiceResponse,
)
def get_ai_service_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    service = ai_service_service.get_by_slug(
        db=db,
        slug=slug,
    )

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI service not found.",
        )

    return service


# ==========================================================
# CREATE
#
# Endpoint cuối:
# POST /api/ai-services
#
# Service mới được tạo với status DRAFT.
# ==========================================================

@router.post(
    "",
    response_model=AIServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ai_service(
    data: AIServiceCreate,
    db: Session = Depends(get_db),
):
    try:
        return ai_service_service.create(
            db=db,
            data=data,
        )

    except ValueError as exc:
        _raise_bad_request(exc)


# ==========================================================
# GET BY ID
#
# Route động phải đặt sau các route tĩnh.
#
# Endpoint cuối:
# GET /api/ai-services/{service_id}
# ==========================================================

@router.get(
    "/{service_id}",
    response_model=AIServiceResponse,
)
def get_ai_service_by_id(
    service_id: UUID,
    db: Session = Depends(get_db),
):
    service = ai_service_service.get_by_id(
        db=db,
        service_id=service_id,
    )

    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI service not found.",
        )

    return service


# ==========================================================
# UPDATE
#
# Endpoint cuối:
# PUT /api/ai-services/{service_id}
#
# Chỉ sửa được DRAFT, REJECTED hoặc PAUSED.
# ==========================================================

@router.put(
    "/{service_id}",
    response_model=AIServiceResponse,
)
def update_ai_service(
    service_id: UUID,
    data: AIServiceUpdate,
    db: Session = Depends(get_db),
):
    try:
        service = ai_service_service.update(
            db=db,
            service_id=service_id,
            data=data,
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI service not found.",
            )

        return service

    except ValueError as exc:
        _raise_bad_request(exc)


# ==========================================================
# SUBMIT FOR REVIEW
#
# Endpoint cuối:
# PATCH /api/ai-services/{service_id}/submit
#
# DRAFT/REJECTED -> PENDING
# ==========================================================

@router.patch(
    "/{service_id}/submit",
    response_model=AIServiceResponse,
)
def submit_ai_service_for_review(
    service_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        service = ai_service_service.submit_for_review(
            db=db,
            service_id=service_id,
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI service not found.",
            )

        return service

    except ValueError as exc:
        _raise_bad_request(exc)


# ==========================================================
# UPDATE STATUS
#
# Endpoint cuối:
# PATCH /api/ai-services/{service_id}/status
#
# Ví dụ:
# PENDING -> PUBLISHED
# PENDING -> REJECTED
# PUBLISHED -> PAUSED
# PAUSED -> PUBLISHED
# ==========================================================

@router.patch(
    "/{service_id}/status",
    response_model=AIServiceResponse,
)
def update_ai_service_status(
    service_id: UUID,
    data: AIServiceStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        service = ai_service_service.update_status(
            db=db,
            service_id=service_id,
            data=data,
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI service not found.",
            )

        return service

    except ValueError as exc:
        _raise_bad_request(exc)


# ==========================================================
# UPDATE FEATURED
#
# Endpoint cuối:
# PATCH /api/ai-services/{service_id}/featured
#
# Chỉ Admin nên được gọi endpoint này.
# ==========================================================

@router.patch(
    "/{service_id}/featured",
    response_model=AIServiceResponse,
)
def update_ai_service_featured(
    service_id: UUID,
    data: AIServiceFeaturedUpdate,
    db: Session = Depends(get_db),
):
    try:
        service = ai_service_service.update_featured(
            db=db,
            service_id=service_id,
            data=data,
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI service not found.",
            )

        return service

    except ValueError as exc:
        _raise_bad_request(exc)


# ==========================================================
# INCREMENT VIEW
#
# Endpoint cuối:
# PATCH /api/ai-services/{service_id}/view
# ==========================================================

@router.patch(
    "/{service_id}/view",
    response_model=AIServiceViewResponse,
)
def increment_ai_service_view(
    service_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        service = ai_service_service.increment_view(
            db=db,
            service_id=service_id,
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI service not found.",
            )

        return {
            "service_id": service.id,
            "view_count": int(
                service.view_count or 0
            ),
        }

    except ValueError as exc:
        _raise_bad_request(exc)


# ==========================================================
# INCREMENT ORDER COUNT
#
# Endpoint cuối:
# PATCH /api/ai-services/{service_id}/order
#
# Hiện chỉ tăng bộ đếm. Sau này nên gọi tự động khi
# ServiceOrder được tạo thành công.
# ==========================================================

@router.patch(
    "/{service_id}/order",
    response_model=AIServiceResponse,
)
def increment_ai_service_order_count(
    service_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        service = (
            ai_service_service.increment_order_count(
                db=db,
                service_id=service_id,
            )
        )

        if service is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI service not found.",
            )

        return service

    except ValueError as exc:
        _raise_bad_request(exc)


# ==========================================================
# DELETE
#
# Endpoint cuối:
# DELETE /api/ai-services/{service_id}
#
# Chỉ xóa DRAFT, REJECTED hoặc ARCHIVED và chưa có order.
# ==========================================================

@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_ai_service(
    service_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        deleted = ai_service_service.delete(
            db=db,
            service_id=service_id,
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI service not found.",
            )

        return None

    except ValueError as exc:
        _raise_bad_request(exc)