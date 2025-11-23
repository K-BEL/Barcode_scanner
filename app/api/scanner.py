"""Barcode scanning API routes."""
from fastapi import APIRouter, HTTPException

from app.schemas.product import ProductInfo
from app.services.barcode_service import BarcodeService

router = APIRouter(prefix="/scan", tags=["scanner"])


@router.get("/barcode", response_model=ProductInfo)
def scan_barcode():
    """
    Scan a barcode using the camera.
    
    Returns:
        Product information if barcode is found
    """
    service = BarcodeService()
    result = service.scan_barcode()
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result
