"""Product-related Pydantic schemas."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class ProductBase(BaseModel):
    """Base product schema."""
    product_name: str = Field(..., min_length=1, max_length=255, description="Product name")
    price: float = Field(..., ge=0, le=999999.99, description="Product price (0 to 999999.99)")
    quantity: int = Field(default=1, ge=0, le=999999, description="Product quantity (0 to 999999)")
    details: str = Field(default="to fill", max_length=5000, description="Product details (max 5000 chars)")
    reorder_point: int = Field(default=0, ge=0, description="Reorder point - alert when stock falls below this")
    category_id: Optional[int] = Field(None, description="Product category ID")
    
    @field_validator('product_name')
    @classmethod
    def validate_product_name(cls, v: str) -> str:
        """Validate product name is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Product name cannot be empty or whitespace only")
        return v.strip()
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Validate price precision."""
        if v < 0:
            raise ValueError("Price cannot be negative")
        # Round to 2 decimal places
        return round(v, 2)


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    price: Optional[float] = Field(None, ge=0, le=999999.99)
    quantity: Optional[int] = Field(None, ge=0, le=999999)
    details: Optional[str] = Field(None, max_length=5000)
    reorder_point: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = Field(None)
    
    @field_validator('product_name')
    @classmethod
    def validate_product_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate product name if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Product name cannot be empty or whitespace only")
            return v.strip()
        return v
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v: Optional[float]) -> Optional[float]:
        """Validate price precision if provided."""
        if v is not None:
            if v < 0:
                raise ValueError("Price cannot be negative")
            return round(v, 2)
        return v


class ProductInfo(ProductBase):
    """Schema for product information response."""
    barcode: str
    timestamp: str
    is_low_stock: Optional[bool] = Field(None, description="True if quantity is below reorder point")
    
    class Config:
        from_attributes = True


class ProductResponse(ProductInfo):
    """Full product response schema."""
    pass


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

