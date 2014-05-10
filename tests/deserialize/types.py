import halogen.types
from decimal import Decimal, InvalidOperation
from halogen import exceptions


class Amount(halogen.types.Type):
    @classmethod
    def deserialize(cls, value):
        try:
            return dict(currency=value["currency"],
                        amount=Decimal(value["amount"]))
        except InvalidOperation as e:
            raise exceptions.ValidationError(e)
