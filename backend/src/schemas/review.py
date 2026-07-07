from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    project_id: int
    expert_id: int
    rating: int = Field(ge=1, le=5)
    comment: str


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    expert_id: int
    rating: int
    comment: str
from pydantic import BaseModel

class ReviewCreate(BaseModel):
    project_id: int
    expert_id: int
    rating: int
    comment: str