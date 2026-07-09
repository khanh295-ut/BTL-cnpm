# backend/src/schemas/contract.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class ContractBase(BaseModel):
    project_id: UUID
    expert_id: UUID
    terms: str
    status: str = "PENDING"

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    terms: str | None = None
    status: str | None = None

class ContractResponse(ContractBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True
