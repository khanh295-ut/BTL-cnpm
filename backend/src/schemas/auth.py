from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# =====================================================
# REGISTER
# =====================================================

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    bio: Optional[str] = None


# =====================================================
# LOGIN
# =====================================================

class LoginRequest(BaseModel):
    login: str
    password: str = Field(min_length=8)


# =====================================================
# REGISTER ALIAS
# =====================================================

class RegisterRequest(UserCreate):
    pass


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
    roles: list[str] = []


# =====================================================
# TOKEN RESPONSE
# =====================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


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
    new_password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)