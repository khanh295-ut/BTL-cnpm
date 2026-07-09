from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# =====================================================
# CREATE USER
# =====================================================

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6)

    full_name: Optional[str] = None
    bio: Optional[str] = None


# =====================================================
# UPDATE USER
# =====================================================

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None


# =====================================================
# PROFILE UPDATE
# =====================================================

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None


# =====================================================
# CHANGE PASSWORD
# =====================================================

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=6)


# =====================================================
# CHANGE ROLE
# =====================================================

class ChangeRoleRequest(BaseModel):
    role: str


# =====================================================
# LOGIN
# =====================================================

class LoginRequest(BaseModel):
    username: str
    password: str


# =====================================================
# USER RESPONSE
# =====================================================

class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    username: str

    email: EmailStr

    full_name: Optional[str] = None

    bio: Optional[str] = None


# =====================================================
# USER READ
# =====================================================

class UserRead(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    username: str

    email: EmailStr

    role: Optional[str] = None

    roles: list[str] = []

    full_name: Optional[str] = None

    bio: Optional[str] = None


# =====================================================
# USER LIST
# =====================================================

class UserListResponse(BaseModel):
    users: list[UserRead]


# =====================================================
# PASSWORD RESET
# =====================================================

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=6)


# =====================================================
# TOKEN RESPONSE
# =====================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"