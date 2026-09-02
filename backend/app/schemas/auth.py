from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """Validate user registration input."""
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(BaseModel):
    """Validate user login input."""
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    """Public representation of an authenticated user."""
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    role: str


class TokenResponse(BaseModel):
    """JWT access-token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse