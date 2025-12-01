"""Cart management API routes."""
<<<<<<< HEAD:backend/app/api/cart.py
from typing import Dict
from fastapi import APIRouter, HTTPException, Depends
=======
from fastapi import APIRouter
>>>>>>> 6ee6f1d48ec387ee4f167c258872756aab4d6efe:app/api/cart.py

from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse
from app.services.cart_service import CartService
from app.core.dependencies import get_cart_service
from app.utils.datetime_utils import serialize_datetime

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/products", response_model=CartItemResponse)
def add_product_cart(
    barcode: str,
    product: CartItemCreate,
    service: CartService = Depends(get_cart_service)
):
    """
    Add a product to cart.
    
    Args:
        barcode: Product barcode
        product: Product data
        service: Cart service dependency
        
    Returns:
        Created cart item information
    """
    cart_item = service.add_product(barcode, product.dict())
    
    return CartItemResponse(
        barcode=cart_item['barcode'],
        product_name=cart_item['product_name'],
        price=cart_item['price'],
        quantity=cart_item['quantity'],
        details=cart_item['details'],
        timestamp=serialize_datetime(cart_item['timestamp'])
    )


@router.put("/products/{barcode}", response_model=CartItemResponse)
def modify_product_cart(
    barcode: str,
    product: CartItemUpdate,
    service: CartService = Depends(get_cart_service)
):
    """
    Modify a product in cart.
    
    Args:
        barcode: Product barcode
        product: Updated product data
        service: Cart service dependency
        
    Returns:
        Updated cart item information
    """
    cart_item = service.update_cart_item(
        barcode,
        {k: v for k, v in product.dict().items() if v is not None}
    )
    
    return CartItemResponse(
        barcode=cart_item['barcode'],
        product_name=cart_item['product_name'],
        price=cart_item['price'],
        quantity=cart_item['quantity'],
        details=cart_item['details'],
        timestamp=serialize_datetime(cart_item['timestamp'])
    )


@router.delete("/products/{barcode}")
def delete_product_cart(
    barcode: str,
    service: CartService = Depends(get_cart_service)
):
    """
    Delete a product from cart.
    
    Args:
        barcode: Product barcode
        service: Cart service dependency
        
    Returns:
        Success message
    """
    deleted_item = service.delete_cart_item(barcode)
    
    return {
        "message": "Product deleted successfully",
        "deleted_product": {
            "barcode": deleted_item['barcode'],
            "product_name": deleted_item['product_name']
        }
    }


@router.get("/products", response_model=CartResponse)
def get_list_cart(service: CartService = Depends(get_cart_service)):
    """
    Get all products in cart.
    
    Args:
        service: Cart service dependency
        
    Returns:
        Dictionary of all cart items
    """
    cart_items = service.get_all_cart_items()
    
    products_dict = {}
    for item in cart_items:
        products_dict[item['barcode']] = CartItemResponse(
            barcode=item['barcode'],
            product_name=item['product_name'],
            price=item['price'],
            quantity=item['quantity'],
            details=item['details'],
            timestamp=serialize_datetime(item['timestamp'])
        )
    
    return CartResponse(products=products_dict)


@router.delete("/clear")
def clear_cart(service: CartService = Depends(get_cart_service)):
    """
    Clear all products from cart.
    
    Args:
        service: Cart service dependency
        
    Returns:
        Success message
    """
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
