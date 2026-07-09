from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# =====================================================
# REGISTER
# =====================================================

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6)

    full_name: Optional[str] = None
    bio: Optional[str] = None


# =====================================================
# LOGIN
# =====================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


# =====================================================
# TOKEN RESPONSE
# =====================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# =====================================================
# FORGOT PASSWORD
# =====================================================

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# =====================================================
# RESET PASSWORD
# =====================================================

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=6)


# =====================================================
# USER RESPONSE
# =====================================================

class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: str

    username: str

    email: EmailStr

    full_name: Optional[str] = None

    bio: Optional[str] = None