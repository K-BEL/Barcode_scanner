"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "product_name": "Test Product",
        "price": 10.99,
        "quantity": 5,
        "details": "Test product details"
    }


@pytest.fixture
def sample_cart_item_data():
    """Sample cart item data for testing."""
    return {
        "product_name": "Test Product",
        "price": 10.99,
        "quantity": 2,
        "details": "Test product details"
    }

