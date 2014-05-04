

class Type(object):

    def serialize(self, value):
        return value

    def deserialize(self, value):
        return value


class Accessor(object):
    def __init__(self, getter=None, setter=None):
        self.getter = getter
        self.setter = setter

    def get(self, value):
        assert self.getter is not None, "Getter accessor is not specified."
        if callable(self.getter):
            return self.getter(value)

        assert isinstance(self.getter, basestring), "Accessor must be a function or a dot-separated string."

        for attr in self.getter.split("."):
            if isinstance(value, dict):
                value = value[attr]
            else:
                value = getattr(value, attr)
        return value

    def __repr__(self):
        return "<{0} getter='{1}', setter='{1}>".format(
            self.__class__.__name__,
            self.getter,
            self.setter,
        )


class Attr(object):
    default_type = Type()

    def __init__(self, attr_type=None, attr=None):
        self.attr_type = attr_type or self.default_type
        self.name = None
        self.attr = attr

    @property
    def accessor(self):
        attr = self.attr or self.name

        if isinstance(attr, Accessor):
            return attr

        return Accessor(getter=attr)

    def serialize(self, value):
        return self.accessor.get(value)

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
                # Collect the attribute and set it's name.
                delattr(cls, name)
                cls.__class_attrs__.append(value)
                value.name = name

        cls.__attrs__ = []
        for base in reversed(cls.__mro__):
            cls.__attrs__.extend(getattr(base, "__class_attrs__", []))


Schema = _SchemaType("Schema", (_Schema, ), {"__doc__": _Schema.__doc__})
