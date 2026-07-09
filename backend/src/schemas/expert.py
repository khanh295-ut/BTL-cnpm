from uuid import UUID
from decimal import Decimal
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# SKILL SCHEMAS
# ==========================================================

class SkillBase(BaseModel):
    name: str = Field(..., max_length=100)


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


# ==========================================================
# EXPERT BASE
# ==========================================================

class ExpertBase(BaseModel):
    full_name: str = Field(..., max_length=255)
    title: Optional[str] = Field(default=None, max_length=255)
    bio: Optional[str] = Field(default=None, max_length=500)
    hourly_rate: Decimal = Field(default=Decimal("0.00"), ge=0)
    location: Optional[str] = Field(default=None, max_length=255)


# ==========================================================
# CREATE
# ==========================================================

class ExpertCreate(ExpertBase):
    skills: list[SkillCreate] = Field(default_factory=list)


# ==========================================================
# UPDATE
# ==========================================================

class ExpertUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=255)
    title: Optional[str] = Field(default=None, max_length=255)
    bio: Optional[str] = Field(default=None, max_length=500)
    hourly_rate: Optional[Decimal] = Field(default=None, ge=0)
    location: Optional[str] = Field(default=None, max_length=255)

    # Nếu gửi thì sẽ thay thế toàn bộ danh sách skill
    skills: Optional[list[SkillCreate]] = None


# ==========================================================
# RESPONSE
# ==========================================================

class ExpertResponse(ExpertBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    skills: list[SkillResponse] = Field(default_factory=list)