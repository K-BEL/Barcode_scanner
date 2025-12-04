"""Authentication-related Pydantic schemas."""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str = Field(..., min_length=1, max_length=255, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class UserRegister(BaseModel):
    """Schema for user registration."""
    username: str = Field(..., min_length=1, max_length=255, description="Username")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    email: Optional[EmailStr] = Field(None, description="Email address")
    name: str = Field(..., min_length=1, max_length=255, description="Full name")


class UserAuthResponse(BaseModel):
    """Schema for authentication response."""
    user_id: str
    username: str
    name: str
    email: Optional[str] = None
    roles: list[str] = []
    access_token: Optional[str] = None


class PasswordChange(BaseModel):
    """Schema for password change."""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, description="New password (min 6 characters)")

