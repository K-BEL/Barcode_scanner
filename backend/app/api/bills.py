"""Bill generation API routes."""
from typing import Optional, Dict, List
from fastapi import APIRouter, Query, Depends, HTTPException

from app.schemas.bill import BillResponse, BillListItem, BillDetailResponse
from app.services.bill_service import BillService
from app.core.dependencies import get_bill_service
from app.utils.datetime_utils import serialize_datetime_optional

router = APIRouter(prefix="/bills", tags=["bills"])


@router.get("/generate", response_model=BillResponse)
def generate_bill(
    cashier_name: Optional[str] = Query(None, description="Cashier name"),
    service: BillService = Depends(get_bill_service)
):
    """
    Generate a bill from cart items.
    
    Args:
        cashier_name: Optional cashier name
        service: Bill service dependency
        
    Returns:
        Bill information including file path
    """
    result = service.generate_bill(cashier_name)
    
    return BillResponse(
        message=result["message"],
        bill_id=result.get("bill_id"),
        cashier=result.get("cashier"),
        file_path=result["file_path"],
        pdf_path=result.get("pdf_path"),
        total_amount=result["total_amount"]
    )


@router.get("", response_model=Dict[str, BillListItem])
def get_bills(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Items per page"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    cashier_name: Optional[str] = Query(None, description="Filter by cashier name"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum amount filter"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum amount filter"),
    service: BillService = Depends(get_bill_service)
):
    """
    Get all bills with optional filtering and pagination.
    
    Args:
        page: Page number (1-indexed)
        page_size: Number of items per page
        start_date: Start date filter (YYYY-MM-DD format)
        end_date: End date filter (YYYY-MM-DD format)
        cashier_name: Filter by cashier name
        min_amount: Minimum total amount filter
        max_amount: Maximum total amount filter
        service: Bill service dependency
        
    Returns:
        Dictionary of bills
    """
    bills = service.get_bills(
        page=page,
        page_size=page_size,
        start_date=start_date,
        end_date=end_date,
        cashier_name=cashier_name,
        min_amount=min_amount,
        max_amount=max_amount
    )
    
    result = {}
    for bill in bills:
        result[str(bill['bill_id'])] = BillListItem(
            bill_id=bill['bill_id'],
            cashier=bill.get('cashier_name'),
            total_amount=bill['total_amount'],
            created_at=bill['created_at'],
            file_path=bill.get('file_path')
        )
    
    return result


@router.get("/{bill_id}", response_model=BillDetailResponse)
def get_bill(
    bill_id: int,
    service: BillService = Depends(get_bill_service)
):
    """
    Get a specific bill by ID.
    
    Args:
        bill_id: Bill ID
        service: Bill service dependency
        
    Returns:
        Detailed bill information
    """
    bill = service.get_bill(bill_id)
    
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    return BillDetailResponse(
        bill_id=bill['bill_id'],
        bill_text=bill['bill_text'],
        cashier=bill.get('cashier_name'),
        total_amount=bill['total_amount'],
        created_at=bill['created_at'],
        file_path=bill.get('file_path')
    )


# Legacy endpoint for backward compatibility
@router.get("/generate-bill", response_model=BillResponse)
def generate_bill_legacy(cashier_name: Optional[str] = Query(None)):
    """Legacy endpoint for bill generation."""
    return generate_bill(cashier_name)
