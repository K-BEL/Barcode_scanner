"""Category-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional


class CategoryCreate(BaseModel):
    """Schema for creating a category."""
    name: str = Field(..., min_length=1, max_length=255, description="Category name")
    description: Optional[str] = Field(None, max_length=1000, description="Category description")


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: int
    name: str
    description: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True

