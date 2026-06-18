from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserEntity:
    id: Optional[int]
    username: str
    email: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    role: str = "User"


@dataclass
class PasswordResetTokenEntity:
    id: Optional[int]
    user_id: int
    token: str
    expires_at: datetime
    created_at: Optional[datetime] = None


@dataclass
class ProjectEntity:
    id: Optional[int]
    title: str
    description: str
    status: str = "OPEN"


@dataclass
class ProposalEntity:
    id: Optional[int]
    project_id: int
    expert_id: int
    price: int
    comment: Optional[str] = None
    status: str = "PENDING"


@dataclass
class ReviewEntity:
    id: Optional[int]
    project_id: int
    expert_id: int
    rating: int
    comment: str
