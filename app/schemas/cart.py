"""Cart-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class CartItemBase(BaseModel):
    """Base cart item schema."""
    product_name: str = Field(..., description="Product name")
    price: float = Field(..., ge=0, description="Product price")
    quantity: int = Field(default=1, ge=1, description="Product quantity")
    details: str = Field(default="to fill", description="Product details")


class CartItemCreate(CartItemBase):
    """Schema for creating a cart item."""
    pass


class CartItemUpdate(CartItemBase):
    """Schema for updating a cart item."""
    product_name: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=1)
    details: Optional[str] = None


class CartItemResponse(CartItemBase):
    """Schema for cart item response."""
    barcode: str
    timestamp: str
    
    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Schema for cart response."""
    products: Dict[str, CartItemResponse]
    
    class Config:
        from_attributes = True

