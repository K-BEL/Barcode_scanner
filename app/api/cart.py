"""Cart management API routes."""
from typing import Dict
from fastapi import APIRouter, HTTPException

from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse
from app.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/products", response_model=CartItemResponse)
def add_product_cart(barcode: str, product: CartItemCreate):
    """
    Add a product to cart.
    
    Args:
        barcode: Product barcode
        product: Product data
        
    Returns:
        Created cart item information
    """
    service = CartService()
    cart_item = service.add_product(barcode, product.dict())
    
    timestamp = cart_item['timestamp']
    if hasattr(timestamp, 'isoformat'):
        timestamp = timestamp.isoformat()
    
    return CartItemResponse(
        barcode=cart_item['barcode'],
        product_name=cart_item['product_name'],
        price=cart_item['price'],
        quantity=cart_item['quantity'],
        details=cart_item['details'],
        timestamp=str(timestamp)
    )


@router.put("/products/{barcode}", response_model=CartItemResponse)
def modify_product_cart(barcode: str, product: CartItemUpdate):
    """
    Modify a product in cart.
    
    Args:
        barcode: Product barcode
        product: Updated product data
        
    Returns:
        Updated cart item information
    """
    service = CartService()
    cart_item = service.update_cart_item(
        barcode,
        {k: v for k, v in product.dict().items() if v is not None}
    )
    
    timestamp = cart_item['timestamp']
    if hasattr(timestamp, 'isoformat'):
        timestamp = timestamp.isoformat()
    
    return CartItemResponse(
        barcode=cart_item['barcode'],
        product_name=cart_item['product_name'],
        price=cart_item['price'],
        quantity=cart_item['quantity'],
        details=cart_item['details'],
        timestamp=str(timestamp)
    )


@router.delete("/products/{barcode}")
def delete_product_cart(barcode: str):
    """
    Delete a product from cart.
    
    Args:
        barcode: Product barcode
        
    Returns:
        Success message
    """
    service = CartService()
    deleted_item = service.delete_cart_item(barcode)
    
    return {
        "message": "Product deleted successfully",
        "deleted_product": {
            "barcode": deleted_item['barcode'],
            "product_name": deleted_item['product_name']
        }
    }


@router.get("/products", response_model=CartResponse)
def get_list_cart():
    """
    Get all products in cart.
    
    Returns:
        Dictionary of all cart items
    """
    service = CartService()
    cart_items = service.get_all_cart_items()
    
    if not cart_items:
        raise HTTPException(status_code=404, detail="Cart is empty.")
    
    products_dict = {}
    for item in cart_items:
        timestamp = item['timestamp']
        if hasattr(timestamp, 'isoformat'):
            timestamp = timestamp.isoformat()
        
        products_dict[item['barcode']] = CartItemResponse(
            barcode=item['barcode'],
            product_name=item['product_name'],
            price=item['price'],
            quantity=item['quantity'],
            details=item['details'],
            timestamp=str(timestamp)
        )
    
    return CartResponse(products=products_dict)


@router.delete("/clear")
def clear_cart():
    """
    Clear all products from cart.
    
    Returns:
        Success message
    """
    service = CartService()
    count = service.clear_cart()
    
    return {
        "message": "All products cleared from cart",
        "items_cleared": count
    }


# Legacy endpoint for backward compatibility
@router.get("/list", response_model=CartResponse)
def get_list_cart_legacy():
    """Legacy endpoint for getting cart list."""
    return get_list_cart()
