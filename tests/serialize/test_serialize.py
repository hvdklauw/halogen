"""Tests for testing serialization of Halogen schemas."""

import pytest
import halogen


@pytest.fixture
def test_schema():
    """Test schema for serialization."""

    class TestSchema(halogen.Schema):
        self = halogen.Link(attr="uid")

    return TestSchema


@pytest.fixture
def test_content():
    """Test content for serialization."""
    return {
        "uid": "/test/123"
    }


def test_content_serialization(test_schema, test_content):
    """Check that test_content serialized into HAL+json format."""

    assert test_schema.serialize(test_content) == {
        "_links": {
            "self": {"href": "/test/123"}
        }
    }
