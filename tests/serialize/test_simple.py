"""Tests for testing serialization of Halogen schemas."""

import halogen


def test_link_simple():
    """Check that link is serialized in the simple case."""

    data = {
        "uid": "/test/123",
    }

    class Schema(halogen.Schema):
        self = halogen.Link(attr="uid")

    assert Schema.serialize(data) == {
        "_links": {
            "self": {"href": "/test/123"}
        }
    }
