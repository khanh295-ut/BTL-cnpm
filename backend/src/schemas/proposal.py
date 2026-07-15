from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


# CREATE PROPOSAL
class ProposalCreate(BaseModel):
    project_id: UUID
    expert_id: UUID
    bid_amount: Decimal = Field(..., gt=0, description="Giá đề xuất")
    cover_letter: str = Field(..., min_length=1, description="Thư giới thiệu")
    estimated_days: int = Field(..., gt=0, description="Số ngày hoàn thành dự kiến")


# UPDATE PROPOSAL
class ProposalUpdate(BaseModel):
    bid_amount: Decimal | None = Field(default=None, gt=0)
    cover_letter: str | None = None
    estimated_days: int | None = Field(default=None, gt=0)


# UPDATE STATUS
class ProposalStatusUpdate(BaseModel):
    status: str


# RESPONSE
class ProposalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    expert_id: UUID
    bid_amount: Decimal
    cover_letter: str
    estimated_days: int
    status: str
    created_at: datetime

