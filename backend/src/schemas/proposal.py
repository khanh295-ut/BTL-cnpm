from pydantic import BaseModel, ConfigDict, Field


class ProposalCreate(BaseModel):
    project_id: int
    expert_id: int
    price: int = Field(ge=0)
    comment: str | None = None


class ProposalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    expert_id: int
    price: int
    comment: str | None = None
    status: str
from pydantic import BaseModel

class ProposalCreate(BaseModel):
    project_id: int
    expert_id: int
    price: int