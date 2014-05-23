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


def test_link_curie():
    """Check that link is serialized with curie."""

    data = {
        "uid": "/test/123",
    }

    class Schema(halogen.Schema):
        self = halogen.Link(attr="uid", curie="test")

    assert Schema.serialize(data) == {
        "_links": {
            "test:self": {"href": "/test/123"}
        }
    }


def test_curies():

    class Schema(halogen.Schema):

        class Curies(halogen.Curies):
            acme = halogen.Curie(href="/test/123")

        curies = Curies()

    assert Schema.serialize({}) == {
        "_links": {
            "curies": [{
                "name": "acme",
                "href": "/test/123",
            }]
        }
    }
