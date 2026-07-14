from __future__ import annotations

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from backend.src.models.auth import User
from backend.src.models.notification import Notification
from backend.src.schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
)


logger = logging.getLogger("AITasker.NotificationService")


class NotificationService:
    # ======================================================
    # GET ALL
    # ======================================================

    def get_all(
        self,
        db: Session,
    ) -> list[Notification]:
        return (
            db.query(Notification)
            .order_by(Notification.created_at.desc())
            .all()
        )

    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        db: Session,
        notification_id: UUID,
    ) -> Notification | None:
        return (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

    # ======================================================
    # GET BY USER
    # ======================================================

    def get_by_user(
        self,
        db: Session,
        user_id: UUID,
    ) -> list[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

    # ======================================================
    # GET UNREAD
    # ======================================================

    def get_unread(
        self,
        db: Session,
        user_id: UUID,
    ) -> list[Notification]:
        return (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .order_by(Notification.created_at.desc())
            .all()
        )

    # ======================================================
    # CREATE
    # ======================================================

    def create(
        self,
        db: Session,
        data: NotificationCreate,
    ) -> Notification:

        user = (
            db.query(User)
            .filter(User.id == data.user_id)
            .first()
        )

        if user is None:
            raise ValueError("User not found.")

        notification = Notification(
            user_id=data.user_id,
            title=data.title.strip(),
            message=data.message.strip(),
            notification_type=data.notification_type.upper(),
            reference_type=(
                data.reference_type.upper()
                if data.reference_type
                else None
            ),
            reference_id=data.reference_id,
            is_read=False,
            created_at=datetime.utcnow(),
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        return notification

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        db: Session,
        notification_id: UUID,
        data: NotificationUpdate,
    ) -> Notification | None:

        notification = self.get_by_id(
            db,
            notification_id,
        )

        if notification is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():

            if isinstance(value, str):
                value = value.strip()

            if (
                field == "notification_type"
                and value
            ):
                value = value.upper()

            if (
                field == "reference_type"
                and value
            ):
                value = value.upper()

            setattr(
                notification,
                field,
                value,
            )

        db.commit()
        db.refresh(notification)

        return notification

    # ======================================================
    # MARK AS READ
    # ======================================================

    def mark_as_read(
        self,
        db: Session,
        notification_id: UUID,
    ) -> Notification | None:

        notification = self.get_by_id(
            db,
            notification_id,
        )

        if notification is None:
            return None

        notification.is_read = True
        notification.read_at = datetime.utcnow()

        db.commit()
        db.refresh(notification)

        return notification

    # ======================================================
    # MARK ALL AS READ
    # ======================================================

    def mark_all_as_read(
        self,
        db: Session,
        user_id: UUID,
    ) -> int:

        notifications = (
            db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .all()
        )

        for item in notifications:
            item.is_read = True
            item.read_at = datetime.utcnow()

        db.commit()

        return len(notifications)

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        db: Session,
        notification_id: UUID,
    ) -> bool:

        notification = self.get_by_id(
            db,
            notification_id,
        )

        if notification is None:
            return False

        db.delete(notification)
        db.commit()

        return True

    # ======================================================
    # DELETE ALL USER NOTIFICATIONS
    # ======================================================

    def delete_all_by_user(
        self,
        db: Session,
        user_id: UUID,
    ) -> int:

        notifications = (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .all()
        )

        total = len(notifications)

        for item in notifications:
            db.delete(item)

        db.commit()

        return total

    # ======================================================
    # AUTO CREATE SYSTEM NOTIFICATION
    # ======================================================

    def send_system_notification(
        self,
        db: Session,
        *,
        user_id: UUID,
        title: str,
        message: str,
        notification_type: str = "SYSTEM",
        reference_type: str | None = None,
        reference_id: UUID | None = None,
    ) -> Notification:

        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type.upper(),
            reference_type=(
                reference_type.upper()
                if reference_type
                else None
            ),
            reference_id=reference_id,
            is_read=False,
            created_at=datetime.utcnow(),
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        logger.info(
            "Notification created for user %s",
            user_id,
        )

        return notification


notification_service = NotificationService()