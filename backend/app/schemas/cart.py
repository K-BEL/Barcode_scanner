"""Cart-related Pydantic schemas."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
from datetime import datetime


class CartItemBase(BaseModel):
    """Base cart item schema."""
    product_name: str = Field(..., min_length=1, max_length=255, description="Product name")
    price: float = Field(..., ge=0, le=999999.99, description="Product price (0 to 999999.99)")
    quantity: int = Field(default=1, ge=1, le=999999, description="Product quantity (1 to 999999)")
    details: str = Field(default="to fill", max_length=5000, description="Product details (max 5000 chars)")
    
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
        return round(v, 2)


class CartItemCreate(CartItemBase):
    """Schema for creating a cart item."""
    pass


class CartItemUpdate(BaseModel):
    """Schema for updating a cart item."""
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    price: Optional[float] = Field(None, ge=0, le=999999.99)
    quantity: Optional[int] = Field(None, ge=1, le=999999)
    details: Optional[str] = Field(None, max_length=5000)
    
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

