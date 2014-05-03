

class Attr(object):

    def __init__(self, getter=None, setter=None):
        self.name = None
        self.getter = getter
        self.setter = setter

    def serialize(self, value):
        if callable(self.getter):
            return self.getter(value)
        attr = self.getter or self.name
        if isinstance(value, dict):
            return value[attr]
        else:
            return getattr(value, attr)

    def __repr__(self):
        return "<{0} '{1}'>".format(
            self.__class__.__name__,
            self.name,
        )


class Link(Attr):

    compartment = "_links"

    def serialize(self, value):
        link = {"href": super(Link, self).serialize(value)}
        #TODO: title, name, templated etc
        return link


class Embedded(Attr):

    compartment = "_embedded"

    def __init__(self, schema, *args, **kwargs):
        super(Embedded, self).__init__(*args, **kwargs)
        self.schema = schema

    def serialize(self, value):
        return [self.schema.serialize(val) for val in super(Embedded, self).serialize(value)]


class _Schema(object):

    @classmethod
    def serialize(cls, value):
        result = {}
        for attr in cls.__attrs__:
            compartment = result
            compartment_name = getattr(attr, "compartment", None)
            if compartment_name is not None:
                compartment = result.setdefault(compartment_name, {})
            compartment[attr.name] = attr.serialize(value)
        return result


class _SchemaType(type):
    def __init__(cls, name, bases, clsattrs):
        cls.__class_attrs__ = []

        for name, value in clsattrs.items():
            if isinstance(value, Attr):
                delattr(cls, name)
                value.name = name
                cls.__class_attrs__.append(value)

        cls.__attrs__ = []
        for base in reversed(cls.__mro__):
            cls.__attrs__.extend(getattr(base, "__class_attrs__", []))


Schema = _SchemaType("Schema", (_Schema, ), {"__doc__": _Schema.__doc__})
