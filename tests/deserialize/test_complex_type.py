import copy
from decimal import Decimal

import pytest

import halogen
import halogen.types
import halogen.exceptions


def test_nested(nested_data, nested_schema):
    """Test deserialization of a nested type."""
    expected = copy.deepcopy(nested_data)
    expected["price"]["amount"] = Decimal(expected["price"]["amount"])
    deserialized = nested_schema.deserialize(nested_data)
    assert deserialized == expected


def test_invalid_value(nested_schema):
    """Test errors reported for a broken nested type."""
    data = {
        "person": {
            "name": "hello",
            "surname": "bye"
        },
        "is_friend": True,
        "price": {"currency": "EUR", "amount": "wrong_amount"}
    }

    errors = {
        "attr": "<root>",
        "errors": [{
            "attr": "price",
            "errors": [{"type": "InvalidOperation", "error": "Invalid literal for Decimal: 'wrong_amount'"}],
        }]
    }

    with pytest.raises(halogen.exceptions.ValidationError) as e:
        nested_schema.deserialize(data)
    assert e.value.to_dict() == errors


def test_missing_attribute(nested_schema):
    data = {
        "is_friend": True,
        "price": {"currency": "EUR", "amount": "wrong_amount"}
    }
    # TODO improve
    with pytest.raises(halogen.exceptions.ValidationError):
        nested_schema.deserialize(data)
