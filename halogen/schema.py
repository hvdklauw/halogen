
from . import types
from . import exceptions


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

    def set(self, result, value):
        assert self.setter is not None, "Setter accessor is not specified."
        if callable(self.setter):
            return self.setter(value)

        assert isinstance(self.setter, basestring), "Accessor must be a function or a dot-separated string."

        def setdefault(result, attr, value):
            if isinstance(result, dict):
                result.setdefault(attr, value)
            else:
                setattr(result, attr, value)
            return value

        path = self.setter.split(".")
        for attr in path[:-1]:
            result = setdefault(result, attr, {})
        setdefault(result, path[-1], value)

    def __repr__(self):
        return "<{0} getter='{1}', setter='{1}>".format(
            self.__class__.__name__,
            self.getter,
            self.setter,
        )


class Attr(object):

    def __init__(self, attr_type=None, attr=None):
        self.attr_type = attr_type or types.Type
        self.name = None
        self.attr = attr

    @property
    def compartment(self):
        return None

    @property
    def accessor(self):
        attr = self.attr or self.name

        if isinstance(attr, Accessor):
            return attr

        return Accessor(getter=attr, setter=attr)

    def serialize(self, value):
        return self.attr_type.serialize(self.accessor.get(value))

    def deserialize(self, value):
        compartment = value
        if self.compartment is not None:
            compartment = value[self.compartment]
        return self.attr_type.deserialize(compartment[self.name])

    def __repr__(self):
        return "<{0} '{1}'>".format(
            self.__class__.__name__,
            self.name,
        )


class Link(Attr):

    @property
    def compartment(self):
        return "_links"

    def serialize(self, value):
        link = {"href": super(Link, self).serialize(value)}
        #TODO: title, name, templated etc
        return link


class Embedded(Attr):

    @property
    def compartment(self):
        return "_embedded"

    # TODO: need implementation for case when we need only link from objects.
    def serialize(self, value):
        return super(Embedded, self).serialize(value)


class _Schema(types.Type):

    @classmethod
    def serialize(cls, value):
        result = {}
        for attr in cls.__attrs__:
            compartment = result
            if attr.compartment is not None:
                compartment = result.setdefault(attr.compartment, {})
            compartment[attr.name] = attr.serialize(value)
        return result

    @classmethod
    def deserialize(cls, value, result):
        errors = []

        cleaned_data = []
        [(attr, attr.deserialize(value)) for attr in cls.__attrs__]
        for attr in cls.__attrs__:
            try:
                cleaned_data.append((attr, attr.deserialize(value)))
            except exceptions.ValidationError as e:
                errors.append(e)
                # TODO: record an error
        for attr, cleaned_value in cleaned_data:
            attr.accessor.set(result, cleaned_value)


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
