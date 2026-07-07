from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    bio: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=6)


class ChangeRoleRequest(BaseModel):
    role: str



class UserRead(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    username: str

    email: str

    role: str

    roles: list[str] = []

    full_name: str | None = None

    bio: str | None = None



class UserListResponse(BaseModel):

    users: list[UserRead]