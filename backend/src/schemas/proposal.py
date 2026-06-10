from pydantic import BaseModel

class ProposalCreate(BaseModel):
    project_id: int
    expert_id: int
    price: int