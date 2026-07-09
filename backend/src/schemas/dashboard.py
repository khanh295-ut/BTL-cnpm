from pydantic import BaseModel, ConfigDict
from uuid import UUID


# =====================================================
# PROJECT STATUS
# =====================================================

class ProjectStatusResponse(BaseModel):
    status: str
    total: int


# =====================================================
# PROPOSAL STATUS
# =====================================================

class ProposalStatusResponse(BaseModel):
    status: str
    total: int


# =====================================================
# RECENT PROJECT
# =====================================================

class RecentProjectResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    status: str


# =====================================================
# RECENT PROPOSAL
# =====================================================

class RecentProposalResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    expert_id: UUID
    price: float
    status: str


# =====================================================
# RECENT REVIEW
# =====================================================

class RecentReviewResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    expert_id: UUID
    rating: int
    comment: str


# =====================================================
# DASHBOARD RESPONSE
# =====================================================

class DashboardResponse(BaseModel):

    users: int
    experts: int
    enterprises: int
    projects: int
    proposals: int
    reviews: int

    average_rating: float

    project_status: list[ProjectStatusResponse]
    proposal_status: list[ProposalStatusResponse]