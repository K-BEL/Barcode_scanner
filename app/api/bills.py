"""Bill generation API routes."""
from typing import Optional
from fastapi import APIRouter, Query

from app.schemas.bill import BillResponse
from app.services.bill_service import BillService

router = APIRouter(prefix="/bills", tags=["bills"])


@router.get("/generate", response_model=BillResponse)
def generate_bill(cashier_name: Optional[str] = Query(None, description="Cashier name")):
    """
    Generate a bill from cart items.
    
    Args:
        cashier_name: Optional cashier name
        
    Returns:
        Bill information including file path
    """
    service = BillService()
    result = service.generate_bill(cashier_name)
    
    return BillResponse(
        message=result["message"],
        cashier=result.get("cashier"),
        file_path=result["file_path"],
        total_amount=result["total_amount"]
    )


# Legacy endpoint for backward compatibility
@router.get("/generate-bill", response_model=BillResponse)
def generate_bill_legacy(cashier_name: Optional[str] = Query(None)):
    """Legacy endpoint for bill generation."""
    return generate_bill(cashier_name)
