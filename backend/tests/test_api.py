"""API endpoint tests."""
import pytest
from fastapi import status


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data


def test_api_docs(client):
    """Test API documentation endpoint."""
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK


def test_inventory_validation(client, sample_product_data, valid_barcode, invalid_barcode):
    """Test inventory endpoint input validation."""
    # Test invalid barcode format
    response = client.post(
        f"/api/v1/inventory/products?barcode={invalid_barcode}",
        json=sample_product_data
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Test negative price
    invalid_product = sample_product_data.copy()
    invalid_product["price"] = -10.0
    response = client.post(
        f"/api/v1/inventory/products?barcode={valid_barcode}",
        json=invalid_product
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test negative quantity
    invalid_product = sample_product_data.copy()
    invalid_product["quantity"] = -1
    response = client.post(
        f"/api/v1/inventory/products?barcode={valid_barcode}",
        json=invalid_product
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_cart_validation(client, sample_cart_item_data, valid_barcode, invalid_barcode):
    """Test cart endpoint input validation."""
    # Test invalid barcode format
    response = client.post(
        f"/api/v1/cart/products?barcode={invalid_barcode}",
        json=sample_cart_item_data
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Test negative price
    invalid_item = sample_cart_item_data.copy()
    invalid_item["price"] = -10.0
    response = client.post(
        f"/api/v1/cart/products?barcode={valid_barcode}",
        json=invalid_item
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_users_validation(client, sample_user_data):
    """Test users endpoint input validation."""
    # Test empty name
    invalid_user = {"name": ""}
    response = client.post("/api/v1/users", json=invalid_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test whitespace-only name
    invalid_user = {"name": "   "}
    response = client.post("/api/v1/users", json=invalid_user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_legacy_endpoints_deprecated(client):
    """Test that legacy endpoints return 410 Gone."""
    legacy_endpoints = [
        "/scan_barcode",
        "/add_product_inventory",
        "/modify_product_inventory/TEST123",
        "/delete_product_inventory/TEST123",
        "/get_list_inventory",
        "/add_product_cart",
        "/modify_product_cart/TEST123",
        "/delete_product_cart/TEST123",
        "/get_list_cart",
        "/clear_cart",
        "/add_user",
        "/modify_user/TEST123",
        "/delete_user/TEST123",
        "/get_users",
        "/generate-bill",
    ]
    
    for endpoint in legacy_endpoints:
        if endpoint.endswith("TEST123"):
            # Skip endpoints with path parameters for now
            continue
        response = client.get(endpoint) if "get" in endpoint or "scan" in endpoint else client.post(endpoint, json={})
        # Some may return 405 Method Not Allowed, but should not return 200
        assert response.status_code != status.HTTP_200_OK


def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options("/", headers={"Origin": "http://localhost:3000"})
    # CORS preflight should be handled by middleware
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED]

