"""User-related Pydantic schemas."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""
    name: str = Field(..., min_length=1, max_length=255, description="User name (1 to 255 characters)")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate user name is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("User name cannot be empty or whitespace only")
        return v.strip()


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    name: str = Field(..., min_length=1, max_length=255, description="User name (1 to 255 characters)")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate user name is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("User name cannot be empty or whitespace only")
        return v.strip()


class UserResponse(UserBase):
    """Schema for user response."""
    id: str
    added_at: str
    modified_at: Optional[str] = None
    
    class Config:
        from_attributes = True

