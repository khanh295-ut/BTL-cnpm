from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


# ==========================================================
# Base
# ==========================================================

class EnterpriseBase(BaseModel):

    name: str

    email: EmailStr | None = None

    description: str | None = None


# ==========================================================
# Create
# ==========================================================

class EnterpriseCreate(EnterpriseBase):
    pass


# ==========================================================
# Update
# ==========================================================

class EnterpriseUpdate(BaseModel):

    name: str | None = None

    email: EmailStr | None = None

    description: str | None = None


# ==========================================================
# Response
# ==========================================================

class EnterpriseResponse(EnterpriseBase):

    id: UUID

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================================================
# Simple Response
# ==========================================================

class EnterpriseSimple(BaseModel):

    id: UUID

    name: str

    model_config = ConfigDict(
        from_attributes=True
    )