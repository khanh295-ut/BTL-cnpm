from uuid import UUID
from typing import List

from pydantic import BaseModel, ConfigDict


# =====================================================
# CHANGE ROLE
# =====================================================

class ChangeRoleRequest(BaseModel):
    role: str


# =====================================================
# USER INFO
# =====================================================

class AdminUserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    username: str

    email: str

    full_name: str | None = None

    bio: str | None = None


# =====================================================
# USER LIST
# =====================================================

class UserListResponse(BaseModel):
    users: List[AdminUserResponse]


# =====================================================
# DASHBOARD
# =====================================================

class DashboardResponse(BaseModel):

    users: int

    experts: int

    enterprises: int

    projects: int

    proposals: int

    reviews: int


# =====================================================
# PROJECT STATISTICS
# =====================================================

class ProjectStatistic(BaseModel):

    status: str

    total: int


# =====================================================
# PROPOSAL STATISTICS
# =====================================================

class ProposalStatistic(BaseModel):

    status: str

    total: int


# =====================================================
# REVIEW STATISTICS
# =====================================================

class ReviewStatistic(BaseModel):

    average_rating: float


# =====================================================
# ROLE STATISTICS
# =====================================================

class RoleStatistic(BaseModel):

    role: str

    total: int


# =====================================================
# MESSAGE RESPONSE
# =====================================================

class MessageResponse(BaseModel):

    message: str