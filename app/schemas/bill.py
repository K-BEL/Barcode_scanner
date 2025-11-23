"""Bill-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional


class BillResponse(BaseModel):
    """Schema for bill generation response."""
    message: str
    cashier: Optional[str] = None
    file_path: str
    total_amount: float

