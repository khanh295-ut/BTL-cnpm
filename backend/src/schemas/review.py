from pydantic import BaseModel

class ReviewCreate(BaseModel):
    project_id: int
    expert_id: int
    rating: int
    comment: str