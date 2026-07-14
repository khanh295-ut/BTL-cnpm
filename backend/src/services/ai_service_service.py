from __future__ import annotations

import logging
import re
import unicodedata
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from backend.src.models.ai_service import AIService
from backend.src.models.category import Category
from backend.src.models.expert import Expert
from backend.src.schemas.ai_service import (
    AIServiceCreate,
    AIServiceFeaturedUpdate,
    AIServiceFilter,
    AIServiceStatusUpdate,
    AIServiceUpdate,
)


logger = logging.getLogger(
    "AITasker.AIServiceService"
)


class AIServiceService:
    """
    Service quản lý AI Service Marketplace.

    Luồng trạng thái đầy đủ:

        DRAFT
          ↓ submit
        PENDING
        ↙     ↘
    PUBLISHED REJECTED
        ↓
      PAUSED
        ↓
      ARCHIVED

    Trong phiên bản hiện tại, dịch vụ mới tạo được tự động
    chuyển sang PUBLISHED để xuất hiện ngay trên Marketplace.
    """

    ALLOWED_STATUSES = {
        "DRAFT",
        "PENDING",
        "PUBLISHED",
        "REJECTED",
        "PAUSED",
        "ARCHIVED",
    }

    EDITABLE_STATUSES = {
        "DRAFT",
        "REJECTED",
        "PAUSED",
    }

    PUBLIC_STATUSES = {
        "PUBLISHED",
    }

    # ======================================================
    # HELPERS
    # ======================================================

    @staticmethod
    def _decimal(
        value,
    ) -> Decimal:
        if value is None:
            return Decimal("0.00")

        if isinstance(value, Decimal):
            return value

        return Decimal(str(value))

    @staticmethod
    def _normalize_status(
        value: str | None,
    ) -> str:
        return str(
            value or ""
        ).strip().upper()

    @staticmethod
    def _normalize_currency(
        value: str | None,
    ) -> str:
        normalized = str(
            value or "VND"
        ).strip().upper()

        return normalized or "VND"

    @staticmethod
    def _normalize_string_list(
        values: list[str] | None,
    ) -> list[str]:
        if not values:
            return []

        unique_items: dict[str, str] = {}

        for value in values:
            item = str(
                value or ""
            ).strip()

            if not item:
                continue

            normalized_key = item.casefold()

            if normalized_key not in unique_items:
                unique_items[normalized_key] = item

        return list(
            unique_items.values()
        )

    @staticmethod
    def _normalize_optional_string(
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None

    @staticmethod
    def _slugify(
        value: str,
    ) -> str:
        """
        Chuyển tiêu đề thành slug.

        Ví dụ:

        "Xây dựng Chatbot AI"
        -> "xay-dung-chatbot-ai"
        """

        normalized = unicodedata.normalize(
            "NFKD",
            value,
        )

        ascii_text = normalized.encode(
            "ascii",
            "ignore",
        ).decode("ascii")

        ascii_text = ascii_text.lower().strip()

        ascii_text = re.sub(
            r"[^a-z0-9]+",
            "-",
            ascii_text,
        )

        ascii_text = re.sub(
            r"-+",
            "-",
            ascii_text,
        )

        return ascii_text.strip("-")

    def _generate_unique_slug(
        self,
        db: Session,
        title: str,
        custom_slug: str | None = None,
        exclude_service_id: UUID | None = None,
    ) -> str:
        base_slug = self._slugify(
            custom_slug or title
        )

        if not base_slug:
            base_slug = "ai-service"

        candidate = base_slug
        counter = 2

        while True:
            query = (
                db.query(AIService)
                .filter(
                    AIService.slug == candidate
                )
            )

            if exclude_service_id is not None:
                query = query.filter(
                    AIService.id
                    != exclude_service_id
                )

            existing = query.first()

            if existing is None:
                return candidate

            candidate = (
                f"{base_slug}-{counter}"
            )

            counter += 1

    # ======================================================
    # GET EXPERT
    # ======================================================

    def _get_expert(
        self,
        db: Session,
        expert_id: UUID,
    ) -> Expert:
        expert = (
            db.query(Expert)
            .filter(
                Expert.id == expert_id
            )
            .first()
        )

        if expert is None:
            raise ValueError(
                "Expert not found."
            )

        return expert

    # ======================================================
    # GET CATEGORY
    # ======================================================

    def _get_category(
        self,
        db: Session,
        category_id: UUID | None,
    ) -> Category | None:
        if category_id is None:
            return None

        category = (
            db.query(Category)
            .filter(
                Category.id == category_id
            )
            .first()
        )

        if category is None:
            raise ValueError(
                "Category not found."
            )

        return category

    # ======================================================
    # VALIDATE PRICE AND DELIVERY
    # ======================================================

    def _validate_business_values(
        self,
        *,
        price,
        delivery_days: int,
        revision_count: int,
    ) -> None:
        normalized_price = self._decimal(
            price
        )

        if normalized_price < Decimal("0"):
            raise ValueError(
                "Price cannot be negative."
            )

        if delivery_days <= 0:
            raise ValueError(
                "Delivery days must be greater than zero."
            )

        if revision_count < 0:
            raise ValueError(
                "Revision count cannot be negative."
            )

    # ======================================================
    # VALIDATE EDITABLE
    # ======================================================

    def _ensure_editable(
        self,
        service: AIService,
    ) -> None:
        current_status = self._normalize_status(
            service.status
        )

        if current_status not in self.EDITABLE_STATUSES:
            raise ValueError(
                "Only DRAFT, REJECTED, or PAUSED "
                "services can be edited."
            )

    # ======================================================
    # GET ALL
    # ======================================================

    def get_all(
        self,
        db: Session,
    ) -> list[AIService]:
        try:
            return (
                db.query(AIService)
                .options(
                    joinedload(
                        AIService.expert
                    ),
                    joinedload(
                        AIService.category
                    ),
                )
                .order_by(
                    AIService.created_at.desc()
                )
                .all()
            )

        except Exception:
            logger.exception(
                "Không thể lấy danh sách AI services."
            )

            raise

    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        db: Session,
        service_id: UUID,
    ) -> AIService | None:
        try:
            return (
                db.query(AIService)
                .options(
                    joinedload(
                        AIService.expert
                    ),
                    joinedload(
                        AIService.category
                    ),
                )
                .filter(
                    AIService.id == service_id
                )
                .first()
            )

        except Exception:
            logger.exception(
                "Không thể lấy AI service %s.",
                service_id,
            )

            raise

    # ======================================================
    # GET BY SLUG
    # ======================================================

    def get_by_slug(
        self,
        db: Session,
        slug: str,
    ) -> AIService | None:
        normalized_slug = self._slugify(
            slug
        )

        try:
            return (
                db.query(AIService)
                .options(
                    joinedload(
                        AIService.expert
                    ),
                    joinedload(
                        AIService.category
                    ),
                )
                .filter(
                    AIService.slug
                    == normalized_slug
                )
                .first()
            )

        except Exception:
            logger.exception(
                "Không thể lấy AI service bằng slug %s.",
                slug,
            )

            raise

    # ======================================================
    # GET BY EXPERT
    # ======================================================

    def get_by_expert(
        self,
        db: Session,
        expert_id: UUID,
    ) -> list[AIService]:
        try:
            return (
                db.query(AIService)
                .filter(
                    AIService.expert_id
                    == expert_id
                )
                .order_by(
                    AIService.created_at.desc()
                )
                .all()
            )

        except Exception:
            logger.exception(
                "Không thể lấy dịch vụ của expert %s.",
                expert_id,
            )

            raise

    # ======================================================
    # GET BY CATEGORY
    # ======================================================

    def get_by_category(
        self,
        db: Session,
        category_id: UUID,
    ) -> list[AIService]:
        try:
            return (
                db.query(AIService)
                .filter(
                    AIService.category_id
                    == category_id
                )
                .order_by(
                    AIService.created_at.desc()
                )
                .all()
            )

        except Exception:
            logger.exception(
                "Không thể lấy dịch vụ của category %s.",
                category_id,
            )

            raise

    # ======================================================
    # CREATE
    # ======================================================

    def create(
        self,
        db: Session,
        data: AIServiceCreate,
    ) -> AIService:
        """
        Tạo một dịch vụ AI mới.

        Phiên bản hiện tại tự động xuất bản dịch vụ:

            status = PUBLISHED
            published_at = thời điểm tạo

        Vì vậy dịch vụ sẽ xuất hiện ngay trên Marketplace.
        """

        try:
            expert = self._get_expert(
                db=db,
                expert_id=data.expert_id,
            )

            category = self._get_category(
                db=db,
                category_id=data.category_id,
            )

            self._validate_business_values(
                price=data.price,
                delivery_days=data.delivery_days,
                revision_count=data.revision_count,
            )

            slug = self._generate_unique_slug(
                db=db,
                title=data.title,
                custom_slug=data.slug,
            )

            now = datetime.utcnow()

            service = AIService(
                expert_id=expert.id,

                category_id=(
                    category.id
                    if category is not None
                    else None
                ),

                title=data.title.strip(),

                slug=slug,

                short_description=(
                    self._normalize_optional_string(
                        data.short_description
                    )
                ),

                description=(
                    data.description.strip()
                ),

                price=self._decimal(
                    data.price
                ),

                currency=self._normalize_currency(
                    data.currency
                ),

                delivery_days=(
                    data.delivery_days
                ),

                revision_count=(
                    data.revision_count
                ),

                skills=self._normalize_string_list(
                    data.skills
                ),

                deliverables=(
                    self._normalize_string_list(
                        data.deliverables
                    )
                ),

                requirements=(
                    self._normalize_string_list(
                        data.requirements
                    )
                ),

                features=(
                    self._normalize_string_list(
                        data.features
                    )
                ),

                image_url=(
                    self._normalize_optional_string(
                        data.image_url
                    )
                ),

                demo_url=(
                    self._normalize_optional_string(
                        data.demo_url
                    )
                ),

                portfolio_url=(
                    self._normalize_optional_string(
                        data.portfolio_url
                    )
                ),

                # Tạo xong xuất bản ngay.
                status="PUBLISHED",

                rejection_reason=None,

                is_featured="NO",

                view_count=0,

                order_count=0,

                # Phải có published_at vì Marketplace
                # sắp xếp theo cột này.
                published_at=now,

                created_at=now,

                updated_at=now,
            )

            db.add(service)
            db.commit()
            db.refresh(service)

            logger.info(
                "AI service %s created and published "
                "by expert %s.",
                service.id,
                expert.id,
            )

            return service

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể tạo AI service."
            )

            raise

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        db: Session,
        service_id: UUID,
        data: AIServiceUpdate,
    ) -> AIService | None:
        service = self.get_by_id(
            db=db,
            service_id=service_id,
        )

        if service is None:
            return None

        try:
            self._ensure_editable(
                service
            )

            update_data = data.model_dump(
                exclude_unset=True
            )

            if "category_id" in update_data:
                category = self._get_category(
                    db=db,
                    category_id=(
                        update_data[
                            "category_id"
                        ]
                    ),
                )

                service.category_id = (
                    category.id
                    if category is not None
                    else None
                )

            title = update_data.get(
                "title",
                service.title,
            )

            custom_slug = update_data.get(
                "slug",
                service.slug,
            )

            if (
                "title" in update_data
                or "slug" in update_data
            ):
                service.slug = (
                    self._generate_unique_slug(
                        db=db,
                        title=title,
                        custom_slug=custom_slug,
                        exclude_service_id=(
                            service.id
                        ),
                    )
                )

            if "title" in update_data:
                service.title = (
                    update_data[
                        "title"
                    ].strip()
                )

            if "short_description" in update_data:
                service.short_description = (
                    self._normalize_optional_string(
                        update_data[
                            "short_description"
                        ]
                    )
                )

            if "description" in update_data:
                service.description = (
                    update_data[
                        "description"
                    ].strip()
                )

            if "price" in update_data:
                service.price = self._decimal(
                    update_data["price"]
                )

            if "currency" in update_data:
                service.currency = (
                    self._normalize_currency(
                        update_data["currency"]
                    )
                )

            if "delivery_days" in update_data:
                service.delivery_days = (
                    update_data[
                        "delivery_days"
                    ]
                )

            if "revision_count" in update_data:
                service.revision_count = (
                    update_data[
                        "revision_count"
                    ]
                )

            for field_name in (
                "skills",
                "deliverables",
                "requirements",
                "features",
            ):
                if field_name in update_data:
                    setattr(
                        service,
                        field_name,
                        self._normalize_string_list(
                            update_data[
                                field_name
                            ]
                        ),
                    )

            for field_name in (
                "image_url",
                "demo_url",
                "portfolio_url",
            ):
                if field_name in update_data:
                    setattr(
                        service,
                        field_name,
                        self._normalize_optional_string(
                            update_data[
                                field_name
                            ]
                        ),
                    )

            self._validate_business_values(
                price=service.price,
                delivery_days=(
                    service.delivery_days
                ),
                revision_count=(
                    service.revision_count
                ),
            )

            service.updated_at = (
                datetime.utcnow()
            )

            if (
                self._normalize_status(
                    service.status
                )
                == "REJECTED"
            ):
                service.status = "DRAFT"
                service.rejection_reason = None

            db.commit()
            db.refresh(service)

            logger.info(
                "AI service %s updated.",
                service.id,
            )

            return service

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật AI service %s.",
                service_id,
            )

            raise

    # ======================================================
    # SUBMIT FOR REVIEW
    # ======================================================

    def submit_for_review(
        self,
        db: Session,
        service_id: UUID,
    ) -> AIService | None:
        service = self.get_by_id(
            db=db,
            service_id=service_id,
        )

        if service is None:
            return None

        try:
            current_status = self._normalize_status(
                service.status
            )

            if current_status not in {
                "DRAFT",
                "REJECTED",
            }:
                raise ValueError(
                    "Only DRAFT or REJECTED services "
                    "can be submitted for review."
                )

            if not service.title:
                raise ValueError(
                    "Service title is required."
                )

            if not service.description:
                raise ValueError(
                    "Service description is required."
                )

            if self._decimal(
                service.price
            ) < Decimal("0"):
                raise ValueError(
                    "Invalid service price."
                )

            service.status = "PENDING"
            service.rejection_reason = None
            service.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(service)

            return service

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể gửi AI service %s để duyệt.",
                service_id,
            )

            raise

    # ======================================================
    # UPDATE STATUS
    # ======================================================

    def update_status(
        self,
        db: Session,
        service_id: UUID,
        data: AIServiceStatusUpdate,
    ) -> AIService | None:
        service = self.get_by_id(
            db=db,
            service_id=service_id,
        )

        if service is None:
            return None

        try:
            new_status = self._normalize_status(
                data.status
            )

            if new_status not in self.ALLOWED_STATUSES:
                raise ValueError(
                    "Invalid AI service status."
                )

            current_status = self._normalize_status(
                service.status
            )

            allowed_transitions = {
                "DRAFT": {
                    "PENDING",
                    "ARCHIVED",
                },
                "PENDING": {
                    "PUBLISHED",
                    "REJECTED",
                    "DRAFT",
                },
                "PUBLISHED": {
                    "PAUSED",
                    "ARCHIVED",
                },
                "REJECTED": {
                    "DRAFT",
                    "PENDING",
                    "ARCHIVED",
                },
                "PAUSED": {
                    "PUBLISHED",
                    "ARCHIVED",
                },
                "ARCHIVED": set(),
            }

            if (
                new_status != current_status
                and new_status
                not in allowed_transitions.get(
                    current_status,
                    set(),
                )
            ):
                raise ValueError(
                    f"Invalid status transition: "
                    f"{current_status} -> {new_status}."
                )

            if new_status == "REJECTED":
                if not data.rejection_reason:
                    raise ValueError(
                        "Rejection reason is required."
                    )

                service.rejection_reason = (
                    data.rejection_reason.strip()
                )

            else:
                service.rejection_reason = None

            now = datetime.utcnow()

            service.status = new_status
            service.updated_at = now

            if new_status == "PUBLISHED":
                if service.published_at is None:
                    service.published_at = now

            db.commit()
            db.refresh(service)

            logger.info(
                "AI service %s status changed "
                "from %s to %s.",
                service.id,
                current_status,
                new_status,
            )

            return service

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật trạng thái AI service %s.",
                service_id,
            )

            raise

    # ======================================================
    # FEATURED
    # ======================================================

    def update_featured(
        self,
        db: Session,
        service_id: UUID,
        data: AIServiceFeaturedUpdate,
    ) -> AIService | None:
        service = self.get_by_id(
            db=db,
            service_id=service_id,
        )

        if service is None:
            return None

        try:
            if (
                data.is_featured
                and self._normalize_status(
                    service.status
                )
                != "PUBLISHED"
            ):
                raise ValueError(
                    "Only published services "
                    "can be featured."
                )

            service.is_featured = (
                "YES"
                if data.is_featured
                else "NO"
            )

            service.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(service)

            return service

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể cập nhật featured "
                "cho AI service %s.",
                service_id,
            )

            raise

    # ======================================================
    # INCREMENT VIEW
    # ======================================================

    def increment_view(
        self,
        db: Session,
        service_id: UUID,
    ) -> AIService | None:
        try:
            service = (
                db.query(AIService)
                .filter(
                    AIService.id == service_id
                )
                .with_for_update()
                .first()
            )

            if service is None:
                return None

            if self._normalize_status(
                service.status
            ) != "PUBLISHED":
                raise ValueError(
                    "Only published services "
                    "can receive marketplace views."
                )

            service.view_count = int(
                service.view_count or 0
            ) + 1

            service.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(service)

            return service

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể tăng lượt xem AI service %s.",
                service_id,
            )

            raise

    # ======================================================
    # INCREMENT ORDER COUNT
    # ======================================================

    def increment_order_count(
        self,
        db: Session,
        service_id: UUID,
    ) -> AIService | None:
        try:
            service = (
                db.query(AIService)
                .filter(
                    AIService.id == service_id
                )
                .with_for_update()
                .first()
            )

            if service is None:
                return None

            if self._normalize_status(
                service.status
            ) != "PUBLISHED":
                raise ValueError(
                    "Only published services "
                    "can receive orders."
                )

            service.order_count = int(
                service.order_count or 0
            ) + 1

            service.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(service)

            return service

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể tăng số đơn AI service %s.",
                service_id,
            )

            raise

    # ======================================================
    # MARKETPLACE SEARCH
    # ======================================================

    def marketplace_search(
        self,
        db: Session,
        filters: AIServiceFilter,
        *,
        page: int = 1,
        page_size: int = 12,
    ) -> dict:
        try:
            if page < 1:
                raise ValueError(
                    "Page must be greater than or equal to 1."
                )

            if page_size < 1 or page_size > 100:
                raise ValueError(
                    "Page size must be between 1 and 100."
                )

            query = (
                db.query(AIService)
                .options(
                    joinedload(
                        AIService.expert
                    ),
                    joinedload(
                        AIService.category
                    ),
                )
            )

            requested_status = (
                self._normalize_status(
                    filters.status
                )
                if filters.status
                else "PUBLISHED"
            )

            query = query.filter(
                AIService.status
                == requested_status
            )

            if filters.keyword:
                keyword = (
                    f"%{filters.keyword.strip()}%"
                )

                query = query.filter(
                    or_(
                        AIService.title.ilike(
                            keyword
                        ),
                        AIService.short_description.ilike(
                            keyword
                        ),
                        AIService.description.ilike(
                            keyword
                        ),
                    )
                )

            if filters.category_id is not None:
                query = query.filter(
                    AIService.category_id
                    == filters.category_id
                )

            if filters.expert_id is not None:
                query = query.filter(
                    AIService.expert_id
                    == filters.expert_id
                )

            if filters.min_price is not None:
                query = query.filter(
                    AIService.price
                    >= filters.min_price
                )

            if filters.max_price is not None:
                query = query.filter(
                    AIService.price
                    <= filters.max_price
                )

            if (
                filters.max_delivery_days
                is not None
            ):
                query = query.filter(
                    AIService.delivery_days
                    <= filters.max_delivery_days
                )

            if filters.skill:
                normalized_skill = (
                    filters.skill.strip()
                )

                query = query.filter(
                    AIService.skills.contains(
                        [normalized_skill]
                    )
                )

            if filters.is_featured is not None:
                query = query.filter(
                    AIService.is_featured
                    == (
                        "YES"
                        if filters.is_featured
                        else "NO"
                    )
                )

            total = query.count()

            services = (
                query.order_by(
                    AIService.is_featured.desc(),
                    AIService.order_count.desc(),
                    AIService.view_count.desc(),
                    AIService.published_at.desc(),
                    AIService.created_at.desc(),
                )
                .offset(
                    (page - 1)
                    * page_size
                )
                .limit(page_size)
                .all()
            )

            items: list[dict] = []

            for service in services:
                expert = service.expert
                category = service.category

                items.append(
                    {
                        "id": service.id,
                        "slug": service.slug,
                        "title": service.title,
                        "short_description": (
                            service.short_description
                        ),
                        "price": self._decimal(
                            service.price
                        ),
                        "currency": (
                            service.currency
                        ),
                        "delivery_days": (
                            service.delivery_days
                        ),
                        "image_url": (
                            service.image_url
                        ),
                        "skills": (
                            service.skills or []
                        ),
                        "is_featured": (
                            service.is_featured
                        ),
                        "view_count": int(
                            service.view_count or 0
                        ),
                        "order_count": int(
                            service.order_count or 0
                        ),
                        "expert_id": (
                            service.expert_id
                        ),
                        "expert_name": (
                            expert.full_name
                            if expert
                            else "Unknown expert"
                        ),
                        "expert_title": (
                            expert.title
                            if expert
                            else None
                        ),
                        "category_id": (
                            service.category_id
                        ),
                        "category_name": (
                            category.name
                            if category
                            else None
                        ),
                    }
                )

            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": items,
            }

        except Exception:
            logger.exception(
                "Không thể tìm kiếm AI Service Marketplace."
            )

            raise

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        db: Session,
        service_id: UUID,
    ) -> bool:
        service = self.get_by_id(
            db=db,
            service_id=service_id,
        )

        if service is None:
            return False

        try:
            current_status = self._normalize_status(
                service.status
            )

            if current_status not in {
                "DRAFT",
                "REJECTED",
                "ARCHIVED",
            }:
                raise ValueError(
                    "Only DRAFT, REJECTED, or ARCHIVED "
                    "services can be deleted."
                )

            if int(
                service.order_count or 0
            ) > 0:
                raise ValueError(
                    "Service with orders cannot be deleted."
                )

            db.delete(service)
            db.commit()

            logger.info(
                "AI service %s deleted.",
                service_id,
            )

            return True

        except Exception:
            db.rollback()

            logger.exception(
                "Không thể xóa AI service %s.",
                service_id,
            )

            raise


ai_service_service = AIServiceService()