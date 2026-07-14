from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# ==========================================================
# BASE
# ==========================================================

class AIServiceBase(BaseModel):
    expert_id: UUID

    category_id: Optional[UUID] = None

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    slug: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    short_description: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    description: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )

    price: Decimal = Field(
        ...,
        ge=0,
    )

    currency: str = Field(
        default="VND",
        min_length=1,
        max_length=10,
    )

    delivery_days: int = Field(
        default=7,
        gt=0,
        le=365,
    )

    revision_count: int = Field(
        default=1,
        ge=0,
        le=100,
    )

    skills: list[str] = Field(
        default_factory=list,
    )

    deliverables: list[str] = Field(
        default_factory=list,
    )

    requirements: list[str] = Field(
        default_factory=list,
    )

    features: list[str] = Field(
        default_factory=list,
    )

    image_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    demo_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    portfolio_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    @model_validator(mode="after")
    def normalize_values(self):
        self.title = self.title.strip()
        self.description = self.description.strip()

        if self.slug is not None:
            self.slug = self.slug.strip().lower()

        if self.short_description is not None:
            self.short_description = (
                self.short_description.strip()
            )

        self.currency = self.currency.strip().upper()

        self.skills = [
            item.strip()
            for item in self.skills
            if item and item.strip()
        ]

        self.deliverables = [
            item.strip()
            for item in self.deliverables
            if item and item.strip()
        ]

        self.requirements = [
            item.strip()
            for item in self.requirements
            if item and item.strip()
        ]

        self.features = [
            item.strip()
            for item in self.features
            if item and item.strip()
        ]

        for field_name in (
            "image_url",
            "demo_url",
            "portfolio_url",
        ):
            value = getattr(self, field_name)

            if value is not None:
                setattr(
                    self,
                    field_name,
                    value.strip(),
                )

        return self


# ==========================================================
# CREATE
# ==========================================================

class AIServiceCreate(AIServiceBase):
    pass


# ==========================================================
# UPDATE
# ==========================================================

class AIServiceUpdate(BaseModel):
    category_id: Optional[UUID] = None

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    slug: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    short_description: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    description: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=10000,
    )

    price: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )

    currency: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=10,
    )

    delivery_days: Optional[int] = Field(
        default=None,
        gt=0,
        le=365,
    )

    revision_count: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
    )

    skills: Optional[list[str]] = None

    deliverables: Optional[list[str]] = None

    requirements: Optional[list[str]] = None

    features: Optional[list[str]] = None

    image_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    demo_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    portfolio_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    @model_validator(mode="after")
    def normalize_values(self):
        for field_name in (
            "title",
            "slug",
            "short_description",
            "description",
            "currency",
            "image_url",
            "demo_url",
            "portfolio_url",
        ):
            value = getattr(self, field_name)

            if value is None:
                continue

            value = value.strip()

            if field_name == "slug":
                value = value.lower()

            if field_name == "currency":
                value = value.upper()

            setattr(
                self,
                field_name,
                value,
            )

        for field_name in (
            "skills",
            "deliverables",
            "requirements",
            "features",
        ):
            value = getattr(self, field_name)

            if value is not None:
                setattr(
                    self,
                    field_name,
                    [
                        item.strip()
                        for item in value
                        if item and item.strip()
                    ],
                )

        return self


# ==========================================================
# STATUS UPDATE
# ==========================================================

class AIServiceStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        min_length=1,
        max_length=30,
        examples=["PUBLISHED"],
    )

    rejection_reason: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    @model_validator(mode="after")
    def validate_status(self):
        normalized_status = self.status.strip().upper()

        allowed_statuses = {
            "DRAFT",
            "PENDING",
            "PUBLISHED",
            "REJECTED",
            "PAUSED",
            "ARCHIVED",
        }

        if normalized_status not in allowed_statuses:
            raise ValueError(
                "Invalid AI service status."
            )

        if (
            normalized_status == "REJECTED"
            and not self.rejection_reason
        ):
            raise ValueError(
                "rejection_reason is required "
                "when status is REJECTED."
            )

        self.status = normalized_status

        if self.rejection_reason is not None:
            self.rejection_reason = (
                self.rejection_reason.strip()
            )

        return self


# ==========================================================
# FEATURED UPDATE
# ==========================================================

class AIServiceFeaturedUpdate(BaseModel):
    is_featured: bool


# ==========================================================
# SEARCH FILTER
# ==========================================================

class AIServiceFilter(BaseModel):
    keyword: Optional[str] = None

    category_id: Optional[UUID] = None

    expert_id: Optional[UUID] = None

    min_price: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )

    max_price: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )

    max_delivery_days: Optional[int] = Field(
        default=None,
        gt=0,
        le=365,
    )

    skill: Optional[str] = None

    status: Optional[str] = None

    is_featured: Optional[bool] = None

    @model_validator(mode="after")
    def validate_price_range(self):
        if (
            self.min_price is not None
            and self.max_price is not None
            and self.min_price > self.max_price
        ):
            raise ValueError(
                "min_price cannot be greater than max_price."
            )

        if self.keyword is not None:
            self.keyword = self.keyword.strip()

        if self.skill is not None:
            self.skill = self.skill.strip()

        if self.status is not None:
            self.status = self.status.strip().upper()

        return self


# ==========================================================
# RESPONSE
# ==========================================================

class AIServiceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    expert_id: UUID

    category_id: Optional[UUID] = None

    title: str

    slug: str

    short_description: Optional[str] = None

    description: str

    price: Decimal

    currency: str

    delivery_days: int

    revision_count: int

    skills: list[str] = Field(
        default_factory=list,
    )

    deliverables: list[str] = Field(
        default_factory=list,
    )

    requirements: list[str] = Field(
        default_factory=list,
    )

    features: list[str] = Field(
        default_factory=list,
    )

    image_url: Optional[str] = None

    demo_url: Optional[str] = None

    portfolio_url: Optional[str] = None

    status: str

    rejection_reason: Optional[str] = None

    is_featured: str

    view_count: int

    order_count: int

    published_at: Optional[datetime] = None

    created_at: datetime

    updated_at: datetime


# ==========================================================
# MARKETPLACE CARD
# Dùng để hiển thị danh sách dịch vụ ngoài marketplace.
# ==========================================================

class AIServiceMarketplaceItem(BaseModel):
    id: UUID

    slug: str

    title: str

    short_description: Optional[str] = None

    price: Decimal

    currency: str

    delivery_days: int

    image_url: Optional[str] = None

    skills: list[str] = Field(
        default_factory=list,
    )

    is_featured: str

    view_count: int

    order_count: int

    expert_id: UUID

    expert_name: str

    expert_title: Optional[str] = None

    category_id: Optional[UUID] = None

    category_name: Optional[str] = None


# ==========================================================
# MARKETPLACE LIST RESPONSE
# ==========================================================

class AIServiceMarketplaceResponse(BaseModel):
    total: int

    page: int

    page_size: int

    items: list[AIServiceMarketplaceItem] = Field(
        default_factory=list,
    )


# ==========================================================
# VIEW COUNT RESPONSE
# ==========================================================

class AIServiceViewResponse(BaseModel):
    service_id: UUID

    view_count: int