from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    login: str = Field(min_length=1)
    password: str = Field(min_length=1)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=6)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    password: str = Field(min_length=6)
    confirm_password: str = Field(min_length=6)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: str
    full_name: str | None = None
    bio: str | None = None


class AuthResponse(BaseModel):
    message: str
    user: UserRead


class MessageResponse(BaseModel):
    message: str


class ResetPasswordResponse(BaseModel):
    message: str
    reset_url: str | None = None
