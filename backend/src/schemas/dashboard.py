from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


# ==========================================================
# STATUS SUMMARY
# ==========================================================

class ProjectStatusResponse(BaseModel):
    status: str
    total: int = 0


class ProposalStatusResponse(BaseModel):
    status: str
    total: int = 0


class ServiceOrderStatusResponse(BaseModel):
    status: str
    total: int = 0


class AIServiceStatusResponse(BaseModel):
    status: str
    total: int = 0


# ==========================================================
# EXPERT SUMMARY
# ==========================================================

class DashboardExpertResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID | None = None
    name: str = "Chuyên gia"
    skills: list[Any] = Field(
        default_factory=list,
    )


# ==========================================================
# RECENT PROJECT
# ==========================================================

class RecentProjectResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    title: str
    description: str | None = None
    budget: float = 0
    deadline: date | None = None
    status: str = "PENDING"
    enterprise_id: UUID | None = None
    category_id: UUID | None = None
    created_at: datetime | None = None


# ==========================================================
# RECENT PROPOSAL
# ==========================================================

class RecentProposalResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    project_id: UUID
    expert_id: UUID
    bid_amount: float = 0
    cover_letter: str | None = None
    estimated_days: int | None = None
    status: str = "PENDING"
    created_at: datetime | None = None


# ==========================================================
# RECENT REVIEW
# ==========================================================

class RecentReviewResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    project_id: UUID | None = None
    expert_id: UUID | None = None
    reviewer_id: UUID | None = None
    reviewee_id: UUID | None = None
    rating: float = 0
    comment: str | None = None
    created_at: datetime | None = None


# ==========================================================
# RECENT SERVICE ORDER
# ==========================================================

class RecentServiceOrderResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    service_id: UUID
    service_title: str
    enterprise_id: UUID
    expert_id: UUID
    price: float = 0
    currency: str = "VND"
    status: str = "PENDING"
    created_at: datetime | None = None


# ==========================================================
# RECENT AI SERVICE
# ==========================================================

class RecentAIServiceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    expert_id: UUID
    category_id: UUID | None = None
    title: str
    slug: str
    price: float = 0
    currency: str = "VND"
    status: str = "DRAFT"
    created_at: datetime | None = None


# ==========================================================
# RECENT WITHDRAWAL
# ==========================================================

class RecentWithdrawalResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    user_id: UUID | None = None
    wallet_id: UUID | None = None
    amount: float = 0
    currency: str = "VND"
    status: str = "PENDING"
    created_at: datetime | None = None


# ==========================================================
# RECENT DISPUTE
# ==========================================================

class RecentDisputeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    contract_id: UUID | None = None
    opened_by_user_id: UUID | None = None
    assigned_admin_id: UUID | None = None
    reason: str | None = None
    status: str = "OPEN"
    created_at: datetime | None = None


# ==========================================================
# GENERAL DASHBOARD RESPONSE
# ==========================================================

class DashboardResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    # =====================================================
    # USERS
    # =====================================================

    total_users: int = 0
    total_enterprises: int = 0
    total_experts: int = 0

    # =====================================================
    # PROJECTS
    # =====================================================

    total_projects: int = 0
    total_proposals: int = 0
    total_contracts: int = 0

    # =====================================================
    # AI MARKETPLACE
    # =====================================================

    total_ai_services: int = 0
    total_service_orders: int = 0

    # =====================================================
    # PAYMENT
    # =====================================================

    total_wallets: int = 0
    total_escrows: int = 0
    total_withdrawals: int = 0

    total_revenue: float = 0
    total_escrow_amount: float = 0
    held_escrow_amount: float = 0

    # =====================================================
    # DISPUTE
    # =====================================================

    total_disputes: int = 0

    # =====================================================
    # ACTIVE / PENDING COUNTS
    # =====================================================

    active_projects: int = 0
    active_service_orders: int = 0
    pending_withdrawals: int = 0
    open_disputes: int = 0
    pending_ai_services: int = 0

    # =====================================================
    # RECENT DATA
    # =====================================================

    experts: list[DashboardExpertResponse] = Field(
        default_factory=list,
    )

    recent_projects: list[RecentProjectResponse] = Field(
        default_factory=list,
    )

    recent_proposals: list[RecentProposalResponse] = Field(
        default_factory=list,
    )

    recent_reviews: list[RecentReviewResponse] = Field(
        default_factory=list,
    )

    # =====================================================
    # STATUS DISTRIBUTION
    # =====================================================

    project_status: list[
        ProjectStatusResponse
    ] = Field(
        default_factory=list,
    )

    proposal_status: list[
        ProposalStatusResponse
    ] = Field(
        default_factory=list,
    )

    service_order_status: list[
        ServiceOrderStatusResponse
    ] = Field(
        default_factory=list,
    )

    ai_service_status: list[
        AIServiceStatusResponse
    ] = Field(
        default_factory=list,
    )


# ==========================================================
# ADMIN DASHBOARD RESPONSE
# ==========================================================

class AdminDashboardResponse(DashboardResponse):
    recent_service_orders: list[
        RecentServiceOrderResponse
    ] = Field(
        default_factory=list,
    )

    recent_withdrawals: list[
        RecentWithdrawalResponse
    ] = Field(
        default_factory=list,
    )

    recent_disputes: list[
        RecentDisputeResponse
    ] = Field(
        default_factory=list,
    )

    recent_ai_services: list[
        RecentAIServiceResponse
    ] = Field(
        default_factory=list,
    )


# ==========================================================
# EXPERT DASHBOARD RESPONSE
# ==========================================================

class ExpertDashboardResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    expert: DashboardExpertResponse

    total_ai_services: int = 0
    published_ai_services: int = 0

    total_orders: int = 0
    active_orders: int = 0
    completed_orders: int = 0

    total_proposals: int = 0
    accepted_proposals: int = 0

    total_income: float = 0
    average_rating: float = 0
    review_count: int = 0

    recent_orders: list[
        RecentServiceOrderResponse
    ] = Field(
        default_factory=list,
    )


# ==========================================================
# ENTERPRISE DASHBOARD RESPONSE
# ==========================================================

class EnterpriseDashboardResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    enterprise_id: UUID
    enterprise_name: str

    total_projects: int = 0
    active_projects: int = 0

    total_proposals_received: int = 0

    total_service_orders: int = 0
    active_service_orders: int = 0
    completed_service_orders: int = 0

    total_spent: float = 0

    recent_projects: list[
        RecentProjectResponse
    ] = Field(
        default_factory=list,
    )

    recent_orders: list[
        RecentServiceOrderResponse
    ] = Field(
        default_factory=list,
    )