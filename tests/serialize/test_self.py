import halogen


def test_self():

    doc = {"uid": "/test/123"}

    class Doc(halogen.Schema):
        self = halogen.Link(attr="uid")

    result = Doc.serialize(doc)

    assert result == {
        "_links": {
            "self": {"href": "/test/123"}
        }
    }
