"""Pytest configuration and fixtures."""
import pytest
import os
from fastapi.testclient import TestClient
from app.main import app


# Set test environment variables before importing app modules
os.environ.setdefault("DB_USERNAME", "test_user")
os.environ.setdefault("DB_PASSWORD", "test_password")
os.environ.setdefault("DB_DATABASE", "test_barcode_scanner")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("ALLOWED_ORIGINS", "*")


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


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "name": "Test User"
    }


@pytest.fixture
def valid_barcode():
    """Valid barcode for testing."""
    return "1234567890123"


@pytest.fixture
def invalid_barcode():
    """Invalid barcode for testing."""
    return "INVALID!@#$%"

