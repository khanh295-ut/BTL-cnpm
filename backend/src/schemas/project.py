from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)


class ProjectUpdate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)


class ProjectStatusUpdate(BaseModel):
    status: str = Field(min_length=1)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    status: str
from pydantic import BaseModel


class ProjectCreate(BaseModel):
    title: str
    description: str


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str

    class Config:
        from_attributes = True