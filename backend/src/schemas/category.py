from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ==========================================================
# Base
# ==========================================================

class CategoryBase(BaseModel):

    name: str

    description: str | None = None


# ==========================================================
# Create
# ==========================================================

class CategoryCreate(CategoryBase):
    pass


# ==========================================================
# Update
# ==========================================================

class CategoryUpdate(BaseModel):

    name: str | None = None

    description: str | None = None


# ==========================================================
# Response
# ==========================================================

class CategoryResponse(CategoryBase):

    id: UUID

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# Simple Response
# ==========================================================

class CategorySimple(BaseModel):

    id: UUID

    name: str

    model_config = ConfigDict(
        from_attributes=True
    )