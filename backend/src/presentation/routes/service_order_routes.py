from __future__ import annotations

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
from backend.src.schemas.service_order import (
    ServiceOrderCancelRequest,
    ServiceOrderCompleteRequest,
    ServiceOrderConfirmRequest,
    ServiceOrderCreate,
    ServiceOrderDeliverRequest,
    ServiceOrderDisputeRequest,
    ServiceOrderResponse,
    ServiceOrderStartRequest,
    ServiceOrderStatusUpdate,
    ServiceOrderSummaryResponse,
    ServiceOrderUpdate,
)
from backend.src.services.service_order_service import (
    service_order_service,
)


# ==========================================================
# ROUTER
#
# Prefix "/service-orders" được khai báo trong all_routes.py.
# File này KHÔNG khai báo prefix để tránh lặp URL.
# ==========================================================

router = APIRouter(
    tags=["Service Orders"],
)


# ==========================================================
# INTERNAL HELPERS
# ==========================================================

def _raise_bad_request(
    exc: ValueError,
) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    ) from exc


def _raise_not_found() -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Service order not found.",
    )


# ==========================================================
# GET ALL
#
# Endpoint cuối:
# GET /api/service-orders
#
# Sau này nên giới hạn cho Admin.
# ==========================================================

@router.get(
    "",
    response_model=list[ServiceOrderResponse],
)
def get_all_service_orders(
    db: Session = Depends(get_db),
):
    return service_order_service.get_all(
        db=db,
    )


# ==========================================================
# SUMMARY
#
# Route tĩnh phải đặt trước "/{order_id}".
#
# Endpoint cuối:
# GET /api/service-orders/summary
# ==========================================================

@router.get(
    "/summary",
    response_model=ServiceOrderSummaryResponse,
)
def get_service_order_summary(
    db: Session = Depends(get_db),
):
    return service_order_service.summary(
        db=db,
    )


# ==========================================================
# GET BY ENTERPRISE
#
# Endpoint cuối:
# GET /api/service-orders/enterprise/{enterprise_id}
# ==========================================================

@router.get(
    "/enterprise/{enterprise_id}",
    response_model=list[ServiceOrderResponse],
)
def get_service_orders_by_enterprise(
    enterprise_id: UUID,
    db: Session = Depends(get_db),
):
    return service_order_service.get_by_enterprise(
        db=db,
        enterprise_id=enterprise_id,
    )


# ==========================================================
# GET BY EXPERT
#
# Endpoint cuối:
# GET /api/service-orders/expert/{expert_id}
# ==========================================================

@router.get(
    "/expert/{expert_id}",
    response_model=list[ServiceOrderResponse],
)
def get_service_orders_by_expert(
    expert_id: UUID,
    db: Session = Depends(get_db),
):
    return service_order_service.get_by_expert(
        db=db,
        expert_id=expert_id,
    )


# ==========================================================
# GET BY AI SERVICE
#
# Endpoint cuối:
# GET /api/service-orders/service/{service_id}
# ==========================================================

@router.get(
    "/service/{service_id}",
    response_model=list[ServiceOrderResponse],
)
def get_service_orders_by_service(
    service_id: UUID,
    db: Session = Depends(get_db),
):
    return service_order_service.get_by_service(
        db=db,
        service_id=service_id,
    )


# ==========================================================
# GET BY STATUS
#
# Endpoint cuối:
# GET /api/service-orders/status/{status_value}
# ==========================================================

@router.get(
    "/status/{status_value}",
    response_model=list[ServiceOrderResponse],
)
def get_service_orders_by_status(
    status_value: str,
    db: Session = Depends(get_db),
):
    try:
        return service_order_service.get_by_status(
            db=db,
            status=status_value,
        )

    except ValueError as exc:
        _raise_bad_request(exc)


# ==========================================================
# CREATE
#
# Endpoint cuối:
# POST /api/service-orders
#
# Tạo đơn từ AIService đã PUBLISHED.
# Giá, Expert, currency, delivery_days được lấy từ AIService.
# ==========================================================

@router.post(
    "",
    response_model=ServiceOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service_order(
    data: ServiceOrderCreate,
    db: Session = Depends(get_db),
):
    try:
        return service_order_service.create(
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
# GET /api/service-orders/{order_id}
# ==========================================================

@router.get(
    "/{order_id}",
    response_model=ServiceOrderResponse,
)
def get_service_order_by_id(
    order_id: UUID,
    db: Session = Depends(get_db),
):
    order = service_order_service.get_by_id(
        db=db,
        order_id=order_id,
    )

    if order is None:
        _raise_not_found()

    return order


# ==========================================================
# UPDATE
#
# Endpoint cuối:
# PUT /api/service-orders/{order_id}
#
# Chỉ sửa được khi order còn PENDING.
# ==========================================================

@router.put(
    "/{order_id}",
    response_model=ServiceOrderResponse,
)
def update_service_order(
    order_id: UUID,
    data: ServiceOrderUpdate,
    db: Session = Depends(get_db),
):
    try:
        order = service_order_service.update(
            db=db,
            order_id=order_id,
            data=data,
        )

        if order is None:
            _raise_not_found()

        return order

    except ValueError as exc:
        _raise_bad_request(exc)


# ==========================================================
# CONFIRM
#
# Endpoint cuối:
# PATCH /api/service-orders/{order_id}/confirm
#
# PENDING -> CONFIRMED
# Có thể liên kết Payment, Contract và Escrow hiện có.
# ==========================================================

@router.patch(
    "/{order_id}/confirm",
    response_model=ServiceOrderResponse,
)
def confirm_service_order(
    order_id: UUID,
    data: ServiceOrderConfirmRequest,
    db: Session = Depends(get_db),
):
    try:
        return service_order_service.confirm(
            db=db,
            order_id=order_id,
            data=data,
        )

    except ValueError as exc:
        if str(exc) == "Service order not found.":
            _raise_not_found()

        _raise_bad_request(exc)


# ==========================================================
# START
#
# Endpoint cuối:
# PATCH /api/service-orders/{order_id}/start
#
# CONFIRMED -> IN_PROGRESS
# ==========================================================

@router.patch(
    "/{order_id}/start",
    response_model=ServiceOrderResponse,
)
def start_service_order(
    order_id: UUID,
    data: ServiceOrderStartRequest,
    db: Session = Depends(get_db),
):
    try:
        return service_order_service.start(
            db=db,
            order_id=order_id,
            data=data,
        )

    except ValueError as exc:
        if str(exc) == "Service order not found.":
            _raise_not_found()

        _raise_bad_request(exc)


# ==========================================================
# DELIVER
#
# Endpoint cuối:
# PATCH /api/service-orders/{order_id}/deliver
#
# IN_PROGRESS -> DELIVERED
# Có thể đính kèm deliverable_id.
# ==========================================================

@router.patch(
    "/{order_id}/deliver",
    response_model=ServiceOrderResponse,
)
def deliver_service_order(
    order_id: UUID,
    data: ServiceOrderDeliverRequest,
    db: Session = Depends(get_db),
):
    try:
        return service_order_service.deliver(
            db=db,
            order_id=order_id,
            data=data,
        )

    except ValueError as exc:
        if str(exc) == "Service order not found.":
            _raise_not_found()

        _raise_bad_request(exc)


# ==========================================================
# COMPLETE
#
# Endpoint cuối:
# PATCH /api/service-orders/{order_id}/complete
#
# DELIVERED -> COMPLETED
# Nếu release_escrow=True thì giải ngân toàn bộ Escrow.
# ==========================================================

@router.patch(
    "/{order_id}/complete",
    response_model=ServiceOrderResponse,
)
def complete_service_order(
    order_id: UUID,
    data: ServiceOrderCompleteRequest,
    db: Session = Depends(get_db),
):
    try:
        return service_order_service.complete(
            db=db,
            order_id=order_id,
            data=data,
        )

    except ValueError as exc:
        if str(exc) == "Service order not found.":
            _raise_not_found()

        _raise_bad_request(exc)


# ==========================================================
# CANCEL
#
# Endpoint cuối:
# PATCH /api/service-orders/{order_id}/cancel
#
# Có thể hoàn tiền Escrow nếu refund_escrow=True.
# ==========================================================

@router.patch(
    "/{order_id}/cancel",
    response_model=ServiceOrderResponse,
)
def cancel_service_order(
    order_id: UUID,
    data: ServiceOrderCancelRequest,
    db: Session = Depends(get_db),
):
    try:
        return service_order_service.cancel(
            db=db,
            order_id=order_id,
            data=data,
        )

    except ValueError as exc:
        if str(exc) == "Service order not found.":
            _raise_not_found()

        _raise_bad_request(exc)


# ==========================================================
# DISPUTE
#
# Endpoint cuối:
# PATCH /api/service-orders/{order_id}/dispute
#
# Chuyển ServiceOrder và Escrow sang DISPUTED.
# ==========================================================

@router.patch(
    "/{order_id}/dispute",
    response_model=ServiceOrderResponse,
)
def dispute_service_order(
    order_id: UUID,
    data: ServiceOrderDisputeRequest,
    db: Session = Depends(get_db),
):
    try:
        return service_order_service.dispute(
            db=db,
            order_id=order_id,
            data=data,
        )

    except ValueError as exc:
        if str(exc) == "Service order not found.":
            _raise_not_found()

        _raise_bad_request(exc)


# ==========================================================
# UPDATE STATUS
#
# Endpoint cuối:
# PATCH /api/service-orders/{order_id}/status
#
# Chỉ nên dùng cho Admin hoặc xử lý nghiệp vụ đặc biệt.
# Các luồng thông thường nên dùng confirm/start/deliver/complete.
# ==========================================================

@router.patch(
    "/{order_id}/status",
    response_model=ServiceOrderResponse,
)
def update_service_order_status(
    order_id: UUID,
    data: ServiceOrderStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        return service_order_service.update_status(
            db=db,
            order_id=order_id,
            data=data,
        )

    except ValueError as exc:
        if str(exc) == "Service order not found.":
            _raise_not_found()

        _raise_bad_request(exc)


# ==========================================================
# DELETE
#
# Endpoint cuối:
# DELETE /api/service-orders/{order_id}
#
# Chỉ xóa PENDING/CANCELLED và chưa liên kết Contract/Escrow.
# ==========================================================

@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service_order(
    order_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        deleted = service_order_service.delete(
            db=db,
            order_id=order_id,
        )

        if not deleted:
            _raise_not_found()

        return None

    except ValueError as exc:
        _raise_bad_request(exc)