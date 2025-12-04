"""Sales reporting API routes."""
from typing import Optional
from fastapi import APIRouter, Query, Depends

from app.services.report_service import ReportService
from app.core.dependencies import get_report_service

router = APIRouter(prefix="/reports", tags=["reports"])


def get_report_service() -> ReportService:
    """Get report service instance."""
    return ReportService()


@router.get("/daily")
def get_daily_sales(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format (defaults to today)"),
    cashier_name: Optional[str] = Query(None, description="Filter by cashier name"),
    service: ReportService = Depends(get_report_service)
):
    """
    Get daily sales report.
    
    Args:
        date: Date in YYYY-MM-DD format
        cashier_name: Optional cashier name filter
        service: Report service dependency
        
    Returns:
        Daily sales summary
    """
    return service.get_daily_sales(date=date, cashier_name=cashier_name)


@router.get("/weekly")
def get_weekly_sales(
    week_start: Optional[str] = Query(None, description="Week start date in YYYY-MM-DD format"),
    cashier_name: Optional[str] = Query(None, description="Filter by cashier name"),
    service: ReportService = Depends(get_report_service)
):
    """
    Get weekly sales report.
    
    Args:
        week_start: Week start date in YYYY-MM-DD format
        cashier_name: Optional cashier name filter
        service: Report service dependency
        
    Returns:
        Weekly sales summary
    """
    return service.get_weekly_sales(week_start=week_start, cashier_name=cashier_name)


@router.get("/monthly")
def get_monthly_sales(
    year: int = Query(..., description="Year (e.g., 2024)"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    cashier_name: Optional[str] = Query(None, description="Filter by cashier name"),
    service: ReportService = Depends(get_report_service)
):
    """
    Get monthly sales report.
    
    Args:
        year: Year
        month: Month (1-12)
        cashier_name: Optional cashier name filter
        service: Report service dependency
        
    Returns:
        Monthly sales summary
    """
    return service.get_monthly_sales(year=year, month=month, cashier_name=cashier_name)

