"""Product-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    """Base product schema."""
    product_name: str = Field(..., description="Product name")
    price: float = Field(..., ge=0, description="Product price")
    quantity: int = Field(default=1, ge=0, description="Product quantity")
    details: str = Field(default="to fill", description="Product details")


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass


class ProductUpdate(ProductBase):
    """Schema for updating a product."""
    product_name: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=0)
    details: Optional[str] = None


class ProductInfo(ProductBase):
    """Schema for product information response."""
    barcode: str
    timestamp: str
    
    class Config:
        from_attributes = True


class ProductResponse(ProductInfo):
    """Full product response schema."""
    pass

