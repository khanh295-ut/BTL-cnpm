from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# CREATE

class ReviewCreate(BaseModel):

    project_id: UUID

    expert_id: UUID

    rating: int = Field(
        ge=1,
        le=5,
    )

    comment: str | None = None


# UPDATE

class ReviewUpdate(BaseModel):

    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    comment: str | None = None


# RESPONSE

class ReviewResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    project_id: UUID

    expert_id: UUID

    rating: int

    comment: str | None

    created_at: datetime