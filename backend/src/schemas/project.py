from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ==========================================================
# Base Schema
# ==========================================================

class ProjectBase(BaseModel):

    title: str

    description: str

    budget: Decimal | None = None

    deadline: date | None = None

    enterprise_id: UUID

    category_id: UUID | None = None


# ==========================================================
# Create
# ==========================================================

class ProjectCreate(ProjectBase):
    pass


# ==========================================================
# Update
# ==========================================================

class ProjectUpdate(BaseModel):

    title: str | None = None

    description: str | None = None

    budget: Decimal | None = None

    deadline: date | None = None

    enterprise_id: UUID | None = None

    category_id: UUID | None = None

    status: str | None = None


# ==========================================================
# Status Update
# ==========================================================

class ProjectStatusUpdate(BaseModel):

    status: str


# ==========================================================
# Response
# ==========================================================

class ProjectResponse(ProjectBase):

    id: UUID

    status: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# Simple Response
# ==========================================================

class ProjectSimple(BaseModel):

    id: UUID

    title: str

    status: str

    model_config = ConfigDict(
        from_attributes=True
    )