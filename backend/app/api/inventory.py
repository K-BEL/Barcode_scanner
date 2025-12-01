"""Inventory management API routes."""
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.inventory_service import InventoryService
from app.core.dependencies import get_inventory_service
from app.utils.datetime_utils import serialize_datetime
from app.utils.validators import validate_barcode

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("/products", response_model=ProductResponse)
def add_product(
    barcode: str,
    product: ProductCreate,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Add a new product to inventory.
    
    Args:
        barcode: Product barcode
        product: Product data
        service: Inventory service dependency
        
    Returns:
        Created product information
    """
    # Validate barcode format
    try:
        barcode = validate_barcode(barcode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    created_product = service.add_product(barcode, product.dict())
    
    return ProductResponse(
        barcode=created_product['barcode'],
        product_name=created_product['product_name'],
        price=created_product['price'],
        quantity=created_product['quantity'],
        details=created_product['details'],
        timestamp=serialize_datetime(created_product['timestamp'])
    )


@router.put("/products/{barcode}", response_model=ProductResponse)
def modify_product(
    barcode: str,
    product: ProductUpdate,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Modify an existing product in inventory.
    
    Args:
        barcode: Product barcode
        product: Updated product data
        service: Inventory service dependency
        
    Returns:
        Updated product information
    """
    # Validate barcode format
    try:
        barcode = validate_barcode(barcode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    updated_product = service.update_product(
        barcode,
        {k: v for k, v in product.dict().items() if v is not None}
    )
    
    return ProductResponse(
        barcode=updated_product['barcode'],
        product_name=updated_product['product_name'],
        price=updated_product['price'],
        quantity=updated_product['quantity'],
        details=updated_product['details'],
        timestamp=serialize_datetime(updated_product['timestamp'])
    )


@router.delete("/products/{barcode}")
def delete_product(
    barcode: str,
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Delete a product from inventory.
    
    Args:
        barcode: Product barcode
        service: Inventory service dependency
        
    Returns:
        Success message
    """
    # Validate barcode format
    try:
        barcode = validate_barcode(barcode)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    deleted_product = service.delete_product(barcode)
    
    return {
        "message": "Product deleted successfully",
        "deleted_product": {
            "barcode": deleted_product['barcode'],
            "product_name": deleted_product['product_name']
        }
    }


@router.get("/products", response_model=Dict[str, ProductResponse])
def get_list_inventory(
    search: Optional[str] = Query(None, description="Search by product name"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Items per page"),
    service: InventoryService = Depends(get_inventory_service)
):
    """
    Get all products in inventory with optional search and filtering.
    
    Args:
        search: Search term for product name
        min_price: Minimum price filter
        max_price: Maximum price filter
        page: Page number (1-indexed)
        page_size: Number of items per page
        service: Inventory service dependency
        
    Returns:
        Dictionary of products matching filters
    """
    products = service.get_all_products(
        search=search,
        min_price=min_price,
        max_price=max_price,
        page=page,
        page_size=page_size
    )
    
    result = {}
    for product in products:
        result[product['barcode']] = ProductResponse(
            barcode=product['barcode'],
            product_name=product['product_name'],
            price=product['price'],
            quantity=product['quantity'],
            details=product['details'],
            timestamp=serialize_datetime(product['timestamp'])
        )
    
    return result


# Legacy endpoint for backward compatibility
@router.put("/list", response_model=Dict[str, ProductResponse])
def get_list_inventory_legacy():
    """Legacy endpoint for getting inventory list."""
    return get_list_inventory()
