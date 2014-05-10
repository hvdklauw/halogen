import pytest

import halogen
import tests.deserialize.types


@pytest.fixture
def nested_data():
    return {
        "person": {
            "name": "Johann",
            "surname": "Gambolputty"
        },
        "is_friend": True,
        "price": {"currency": "EUR", "amount": "13.37"}
    }


@pytest.fixture
def broken_nested_data():
    return {
        "person": {
            "name": "hello",
            "surname": "bye"
        },
        "is_friend": True,
        "price": {"currency": "EUR", "amount": "wrong_amount"}
    }


@pytest.fixture
def broken_nested_error():
    return {
        "attr": "<root>",
        "errors": [{
            "attr": "price",
            "errors": [{"type": "InvalidOperation", "error": "Invalid literal for Decimal: 'wrong_amount'"}],
        }]
    }


@pytest.fixture
def nested_schema():
    class Person(halogen.Schema):
        name = halogen.Attr()
        surname = halogen.Attr()

    class NestedSchema(halogen.Schema):
        person = halogen.Attr(Person)
        is_friend = halogen.Attr()
        price = halogen.Attr(tests.deserialize.types.Amount)

    return NestedSchema
