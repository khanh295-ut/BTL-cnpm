from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ==========================================================
# BASE
# ==========================================================

class ContractBase(BaseModel):
    project_id: UUID
    expert_id: UUID

    title: str

    total_amount: Decimal

    terms: str

    status: str = "PENDING"


# ==========================================================
# CREATE
# ==========================================================

class ContractCreate(ContractBase):
    pass


# ==========================================================
# UPDATE
# ==========================================================

class ContractUpdate(BaseModel):
    title: str | None = None

    total_amount: Decimal | None = None

    terms: str | None = None

    status: str | None = None


# ==========================================================
# RESPONSE
# ==========================================================

class ContractResponse(ContractBase):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID

    created_at: datetime

    updated_at: datetime