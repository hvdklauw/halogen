"""Halogen schema basics types."""

from . import types
from . import exceptions


class Accessor(object):
    """Gives possiblity to write your own setter and getter for your attribute."""

    def __init__(self, getter=None, setter=None):
        self.getter = getter
        self.setter = setter

    def get(self, value):
        """Get attribute from value.
        :param value: object from which we should get attribute in self.getter

        :returns: value of object's attribute
        """
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
        """Set value for result's attribute.
        :param result: Dict of values. Where keys are names of attributes and values are deserialized values from input.
        :param value: Deserialized value from input.
        """
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
    """Schema attribute."""

    def __init__(self, attr_type=None, attr=None):
        self.attr_type = attr_type or types.Type
        self.name = None
        self.attr = attr

    @property
    def compartment(self):
        """Place in which attribute will be placed. For example: _links or _embedded"""
        return None

    @property
    def accessor(self):
        """Get accessor with getter and setter of attribute.

        :returns: instance of Accessor class.
        """
        attr = self.attr or self.name

        if isinstance(attr, Accessor):
            return attr

        return Accessor(getter=attr, setter=attr)

    def serialize(self, value):
        """Serialize type of attribute."""
        return self.attr_type.serialize(self.accessor.get(value))

    def deserialize(self, value):
        """Deserialize type of attribute."""
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
    """Link attribute of schema."""

    @property
    def compartment(self):
        return "_links"

    def serialize(self, value):
        link = {"href": super(Link, self).serialize(value)}
        # TODO: title, name, templated etc
        return link


class Embedded(Attr):
    """Embedded attribute of schema."""

    @property
    def compartment(self):
        return "_embedded"

    # TODO: need implementation for case when we need only link from objects.
    def serialize(self, value):
        return super(Embedded, self).serialize(value)


class _Schema(types.Type):
    """Type for creating schema."""

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
    def deserialize(cls, value):
        """Deserialize input.

        :param value: Dict of already loaded json which will be deserialized by schema attributes.

        :returns: Dict of deserialized value for attributes. Where key is name of schema's attribute and value is
        deserialized value from value dict.
        """
        errors = []
        result = {}
        for attr in cls.__attrs__:
            try:
                result[attr.name] = attr.deserialize(value)
            except exceptions.ValidationError as e:
                e.attr = attr.name
                errors.append(e)

        if errors:
            raise exceptions.ValidationError(errors)
        return result

    @classmethod
    def apply(cls, value, result):
        for attr in cls.__attrs__:
            attr.accessor.set(result, value[attr.name])


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
