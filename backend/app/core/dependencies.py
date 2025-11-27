"""Dependency injection for services."""
from app.services.inventory_service import InventoryService
from app.services.cart_service import CartService
from app.services.user_service import UserService
from app.services.bill_service import BillService
from app.services.barcode_service import BarcodeService


def get_inventory_service() -> InventoryService:
    """Get inventory service instance."""
    return InventoryService()


def get_cart_service() -> CartService:
    """Get cart service instance."""
    return CartService()


def get_user_service() -> UserService:
    """Get user service instance."""
    return UserService()


def get_bill_service() -> BillService:
    """Get bill service instance."""
    return BillService()


def get_barcode_service() -> BarcodeService:
    """Get barcode service instance."""
    return BarcodeService()

