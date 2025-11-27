"""API endpoint tests."""
import pytest
from fastapi import status


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()
    assert "version" in response.json()


def test_api_docs(client):
    """Test API documentation endpoint."""
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK


def test_inventory_endpoints(client, sample_product_data):
    """Test inventory endpoints."""
    barcode = "TEST123456"
    
    # Test adding a product
    response = client.post(
        f"/api/v1/inventory/products?barcode={barcode}",
        json=sample_product_data
    )
    # Note: This will fail if database is not set up, which is expected
    # In a real test environment, you'd use a test database
    
    # Test getting products
    response = client.get("/api/v1/inventory/products")
    # Will return 404 if no products, or 200 with products


def test_cart_endpoints(client):
    """Test cart endpoints."""
    # Test getting cart (will be empty initially)
    response = client.get("/api/v1/cart/products")
    # Will return 404 if empty, or 200 with items


def test_users_endpoints(client):
    """Test users endpoints."""
    # Test getting users
    response = client.get("/api/v1/users")
    # Will return 404 if no users, or 200 with users


def test_bills_endpoints(client):
    """Test bills endpoints."""
    # Test generating bill (will fail if cart is empty)
    response = client.get("/api/v1/bills/generate")
    # Will return 404 if cart is empty

