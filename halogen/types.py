
class Type(object):

    @classmethod
    def serialize(cls, value):
        return value

    @classmethod
    def deserialize(cls, value):
        return value


class List(Type):

    def __init__(self, item_type=None):
        super(List, self).__init__()
        self.item_type = item_type or Type

    def serialize(self, value):
        return [self.item_type.serialize(val) for val in value]
