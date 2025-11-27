"""User-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    name: str = Field(..., min_length=1, description="User name")


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    name: str = Field(..., min_length=1, description="User name")


class UserResponse(UserBase):
    """Schema for user response."""
    id: str
    added_at: str
    modified_at: Optional[str] = None
    
    class Config:
        from_attributes = True

