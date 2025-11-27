"""Custom exceptions for the application."""
from fastapi import HTTPException, status


class AppException(Exception):
    """Base exception for application errors."""
    pass


class DatabaseError(AppException):
    """Database operation error."""
    pass


class ProductNotFoundError(AppException):
    """Product not found error."""
    pass


class ProductAlreadyExistsError(AppException):
    """Product already exists error."""
    pass


class CartItemNotFoundError(AppException):
    """Cart item not found error."""
    pass


class CartItemAlreadyExistsError(AppException):
    """Cart item already exists error."""
    pass


class UserNotFoundError(AppException):
    """User not found error."""
    pass


class EmptyCartError(AppException):
    """Cart is empty error."""
    pass


class BarcodeScanError(AppException):
    """Barcode scanning error."""
    pass


def handle_app_exception(exception: AppException) -> HTTPException:
    """Convert application exception to HTTP exception."""
    exception_map = {
        ProductNotFoundError: (status.HTTP_404_NOT_FOUND, "Product not found."),
        ProductAlreadyExistsError: (status.HTTP_400_BAD_REQUEST, "Product with this barcode already exists."),
        CartItemNotFoundError: (status.HTTP_404_NOT_FOUND, "Product not found in cart."),
        CartItemAlreadyExistsError: (status.HTTP_400_BAD_REQUEST, "Product already in cart."),
        UserNotFoundError: (status.HTTP_404_NOT_FOUND, "User not found."),
        EmptyCartError: (status.HTTP_404_NOT_FOUND, "Cart is empty."),
        BarcodeScanError: (status.HTTP_400_BAD_REQUEST, "Error scanning barcode."),
        DatabaseError: (status.HTTP_500_INTERNAL_SERVER_ERROR, "Database operation failed."),
    }
    
    status_code, detail = exception_map.get(
        type(exception),
        (status.HTTP_500_INTERNAL_SERVER_ERROR, str(exception))
    )
    
    return HTTPException(status_code=status_code, detail=detail)

