"""Inventory management API routes."""
from typing import Dict
from fastapi import APIRouter

from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("/products", response_model=ProductResponse)
def add_product(barcode: str, product: ProductCreate):
    """
    Add a new product to inventory.
    
    Args:
        barcode: Product barcode
        product: Product data
        
    Returns:
        Created product information
    """
    service = InventoryService()
    created_product = service.add_product(barcode, product.dict())
    
    # Convert datetime to string if needed
    timestamp = created_product['timestamp']
    if hasattr(timestamp, 'isoformat'):
        timestamp = timestamp.isoformat()
    
    return ProductResponse(
        barcode=created_product['barcode'],
        product_name=created_product['product_name'],
        price=created_product['price'],
        quantity=created_product['quantity'],
        details=created_product['details'],
        timestamp=str(timestamp)
    )


@router.put("/products/{barcode}", response_model=ProductResponse)
def modify_product(barcode: str, product: ProductUpdate):
    """
    Modify an existing product in inventory.
    
    Args:
        barcode: Product barcode
        product: Updated product data
        
    Returns:
        Updated product information
    """
    service = InventoryService()
    updated_product = service.update_product(
        barcode,
        {k: v for k, v in product.dict().items() if v is not None}
    )
    
    timestamp = updated_product['timestamp']
    if hasattr(timestamp, 'isoformat'):
        timestamp = timestamp.isoformat()
    
    return ProductResponse(
        barcode=updated_product['barcode'],
        product_name=updated_product['product_name'],
        price=updated_product['price'],
        quantity=updated_product['quantity'],
        details=updated_product['details'],
        timestamp=str(timestamp)
    )


@router.delete("/products/{barcode}")
def delete_product(barcode: str):
    """
    Delete a product from inventory.
    
    Args:
        barcode: Product barcode
        
    Returns:
        Success message
    """
    service = InventoryService()
    deleted_product = service.delete_product(barcode)
    
    return {
        "message": "Product deleted successfully",
        "deleted_product": {
            "barcode": deleted_product['barcode'],
            "product_name": deleted_product['product_name']
        }
    }


@router.get("/products", response_model=Dict[str, ProductResponse])
def get_list_inventory():
    """
    Get all products in inventory.
    
    Returns:
        Dictionary of all products
    """
    service = InventoryService()
    products = service.get_all_products()
    
    result = {}
    for product in products:
        timestamp = product['timestamp']
        if hasattr(timestamp, 'isoformat'):
            timestamp = timestamp.isoformat()
        
        result[product['barcode']] = ProductResponse(
            barcode=product['barcode'],
            product_name=product['product_name'],
            price=product['price'],
            quantity=product['quantity'],
            details=product['details'],
            timestamp=str(timestamp)
        )
    
    return result


# Legacy endpoint for backward compatibility
@router.put("/list", response_model=Dict[str, ProductResponse])
def get_list_inventory_legacy():
    """Legacy endpoint for getting inventory list."""
    return get_list_inventory()
