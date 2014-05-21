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


def test_link_namespace():
    """Check that link is serialized with namespace."""

    data = {
        "uid": "/test/123",
    }

    class Schema(halogen.Schema):
        self = halogen.Link(attr="uid", namespace="test")

    assert Schema.serialize(data) == {
        "_links": {
            "test:self": {"href": "/test/123"}
        }
    }


def test_curies():

    class Schema(halogen.Schema):

        curies = halogen.Curies([
            halogen.Curie(name="acme", href="/test/123")
        ])

    assert Schema.serialize({}) == {
        "_links": {
            "curies": [{
                "name": "acme",
                "href": "/test/123",
            }]
        }
    }
