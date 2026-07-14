from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from backend.src.config.database import get_db
from backend.src.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
)
from backend.src.services.notification_service import (
    notification_service,
)


router = APIRouter(
    tags=["Notifications"],
)


# ==========================================================
# GET ALL
# ==========================================================

@router.get(
    "",
    response_model=list[NotificationResponse],
)
def get_all_notifications(
    db: Session = Depends(get_db),
):
    return notification_service.get_all(db)


# ==========================================================
# GET BY USER
#
# Lưu ý:
# Route tĩnh "/user/..." phải được khai báo trước
# route động "/{notification_id}" để tránh xung đột.
# ==========================================================

@router.get(
    "/user/{user_id}",
    response_model=list[NotificationResponse],
)
def get_user_notifications(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    return notification_service.get_by_user(
        db=db,
        user_id=user_id,
    )


# ==========================================================
# GET UNREAD BY USER
# ==========================================================

@router.get(
    "/user/{user_id}/unread",
    response_model=list[NotificationResponse],
)
def get_unread_notifications(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    return notification_service.get_unread(
        db=db,
        user_id=user_id,
    )


# ==========================================================
# MARK ALL USER NOTIFICATIONS AS READ
# ==========================================================

@router.patch(
    "/user/{user_id}/read-all",
)
def mark_all_notifications_as_read(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    total = notification_service.mark_all_as_read(
        db=db,
        user_id=user_id,
    )

    return {
        "message": "All notifications marked as read.",
        "updated_count": total,
    }


# ==========================================================
# DELETE ALL USER NOTIFICATIONS
# ==========================================================

@router.delete(
    "/user/{user_id}",
)
def delete_all_user_notifications(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    total = notification_service.delete_all_by_user(
        db=db,
        user_id=user_id,
    )

    return {
        "message": "All user notifications deleted.",
        "deleted_count": total,
    }


# ==========================================================
# GET BY ID
# ==========================================================

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def get_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
):
    notification = notification_service.get_by_id(
        db=db,
        notification_id=notification_id,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    return notification


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notification(
    data: NotificationCreate,
    db: Session = Depends(get_db),
):
    try:
        return notification_service.create(
            db=db,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# UPDATE
# ==========================================================

@router.put(
    "/{notification_id}",
    response_model=NotificationResponse,
)
def update_notification(
    notification_id: UUID,
    data: NotificationUpdate,
    db: Session = Depends(get_db),
):
    try:
        notification = notification_service.update(
            db=db,
            notification_id=notification_id,
            data=data,
        )

        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found.",
            )

        return notification

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ==========================================================
# MARK AS READ
# ==========================================================

@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
)
def mark_notification_as_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
):
    notification = notification_service.mark_as_read(
        db=db,
        notification_id=notification_id,
    )

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    return notification


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
):
    deleted = notification_service.delete(
        db=db,
        notification_id=notification_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )

    return None