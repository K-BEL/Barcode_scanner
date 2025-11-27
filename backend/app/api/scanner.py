"""Barcode scanning API routes."""
from fastapi import APIRouter, HTTPException, Depends

from app.schemas.product import ProductInfo
from app.services.barcode_service import BarcodeService
from app.core.dependencies import get_barcode_service

router = APIRouter(prefix="/scan", tags=["scanner"])


@router.get("/barcode", response_model=ProductInfo)
def scan_barcode(service: BarcodeService = Depends(get_barcode_service)):
    """
    Scan a barcode using the camera.
    
    Args:
        service: Barcode service dependency
        
    Returns:
        Product information if barcode is found
    """
    result = service.scan_barcode()
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result
