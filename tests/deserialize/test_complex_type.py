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


def test_broken_nested(broken_nested_data, broken_nested_error, nested_schema):
    """Test errors reported for a broken nested type."""
    with pytest.raises(halogen.exceptions.ValidationError) as e:
        nested_schema.deserialize(broken_nested_data)
    assert e.value.to_dict() == broken_nested_error
