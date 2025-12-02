"""Bill-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BillResponse(BaseModel):
    """Schema for bill generation response."""
    message: str
    bill_id: Optional[int] = None
    cashier: Optional[str] = None
    file_path: str
    pdf_path: Optional[str] = None
    total_amount: float


class BillListItem(BaseModel):
    """Schema for bill list item."""
    bill_id: int
    cashier: Optional[str] = None
    total_amount: float
    created_at: str
    file_path: Optional[str] = None


class BillDetailResponse(BaseModel):
    """Schema for detailed bill response."""
    bill_id: int
    bill_text: str
    cashier: Optional[str] = None
    total_amount: float
    created_at: str
    file_path: Optional[str] = None

