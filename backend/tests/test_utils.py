"""Utility function tests."""
from datetime import datetime
from app.utils.datetime_utils import serialize_datetime, serialize_datetime_optional


def test_serialize_datetime():
    """Test datetime serialization."""
    dt = datetime(2024, 1, 1, 12, 0, 0)
    result = serialize_datetime(dt)
    assert isinstance(result, str)
    assert "2024-01-01" in result


def test_serialize_datetime_string():
    """Test datetime serialization with string input."""
    dt_str = "2024-01-01T12:00:00"
    result = serialize_datetime(dt_str)
    assert result == dt_str


def test_serialize_datetime_optional_none():
    """Test optional datetime serialization with None."""
    result = serialize_datetime_optional(None)
    assert result is None


def test_serialize_datetime_optional():
    """Test optional datetime serialization."""
    dt = datetime(2024, 1, 1, 12, 0, 0)
    result = serialize_datetime_optional(dt)
    assert isinstance(result, str)

