"""Bill-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BillGenerateRequest(BaseModel):
    """Schema for bill generation request."""
    cashier_name: Optional[str] = None
    discount_percent: Optional[float] = Field(None, ge=0, le=100, description="Discount percentage (0-100)")
    discount_amount: Optional[float] = Field(None, ge=0, description="Fixed discount amount")
    tax_percent: Optional[float] = Field(None, ge=0, le=100, description="Tax percentage (0-100)")
    payment_method: str = Field(default="cash", description="Payment method: cash, card, mobile, etc.")


class BillResponse(BaseModel):
    """Schema for bill generation response."""
    message: str
    bill_id: Optional[int] = None
    cashier: Optional[str] = None
    file_path: str
    pdf_path: Optional[str] = None
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    payment_method: str


class BillListItem(BaseModel):
    """Schema for bill list item."""
    bill_id: int
    cashier: Optional[str] = None
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    payment_method: str
    created_at: str
    file_path: Optional[str] = None


class BillDetailResponse(BaseModel):
    """Schema for detailed bill response."""
    bill_id: int
    bill_text: str
    cashier: Optional[str] = None
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    payment_method: str
    created_at: str
    file_path: Optional[str] = None

