from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# BASE
# ==========================================================

class SkillBase(BaseModel):
    name: str = Field(..., max_length=100)


# ==========================================================
# CREATE
# ==========================================================

class SkillCreate(SkillBase):
    expert_id: UUID


# ==========================================================
# UPDATE
# ==========================================================

class SkillUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)


# ==========================================================
# RESPONSE
# ==========================================================

class SkillResponse(SkillBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    expert_id: UUID