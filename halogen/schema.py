"""Halogen schema basics types."""

from . import types
from . import exceptions


class Accessor(object):

    """Object that incapsulates the getter and the setter of the attribute."""

    def __init__(self, getter=None, setter=None):
        self.getter = getter
        self.setter = setter

    def get(self, value):
        """Get an attribute from a value.

        :param value: Object to get the attribute value from.
        :return: Value of object's attribute.
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

        :param result: Result object or dict to assign the attribute to.
        :param value: Value to be assigned.
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
        """Accessor representation."""
        return "<{0} getter='{1}', setter='{1}>".format(
            self.__class__.__name__,
            self.getter,
            self.setter,
        )


class Attr(object):

    """Schema attribute."""

    def __init__(self, attr_type=None, attr=None, required=True):
        """Attribute constructor.

        :param attr_type: Type or Schema that does the type conversion of the attribute.
        :param attr: Attribute name, dot-separated attribute path or an `Accessor` instance.
        :param required: Is attribute required to be present.
        """
        self.attr_type = attr_type or types.Type
        self.name = None
        self.attr = attr
        self.required = required

    @property
    def compartment(self):
        """A key this attribute will be placed into (for example: _links or _embedded)."""
        return None

    @property
    def accessor(self):
        """Get an attribute's accessor with the getter and the setter.

        :return: `Accessor` instance.
        """
        attr = self.attr or self.name

        if isinstance(attr, Accessor):
            return attr

        return Accessor(getter=attr, setter=attr)

    def serialize(self, value):
        """Serialize the attribute of the input data.

        Gets the attribute value with accessor and converts it using the
        type serialization. Schema will place this serialized value into
        corresponding compartment of the HAL structure with the name of the
        attribute as a key.

        :param value: Value to get the attribute value from.
        :return: Serialized attribute value.
        """
        return self.attr_type.serialize(self.accessor.get(value))

    def deserialize(self, value):
        """Deserialize the attribute from a HAL structure.

        Get the value from the HAL structure from the attribute's compartment
        using the attribute's name as a key, convert it using the attribute's
        type. Schema will either return it to the parent schema or will assign
        to the output value if specified using the attribute's accessor setter.

        :param value: HAL structure to get the value from.
        :return: Deserialized attribute value.
        """
        compartment = value
        if self.compartment is not None:
            compartment = value[self.compartment]
        if self.name in compartment:
            return self.attr_type.deserialize(compartment[self.name])
        elif self.required:
            raise exceptions.ValidationError("missing attribute", self.name)
        else:
            return None

    def __repr__(self):
        """Attribute representation."""
        return "<{0} '{1}'>".format(
            self.__class__.__name__,
            self.name,
        )


class Link(Attr):

    """Link attribute of schema."""

    @property
    def compartment(self):
        """Links are placed in the _links."""
        return "_links"

    def serialize(self, value):
        link = {"href": super(Link, self).serialize(value)}
        # TODO: title, name, templated etc
        return link


class Embedded(Attr):

    """Embedded attribute of schema."""

    @property
    def compartment(self):
        """Embedded objects are placed in the _objects."""
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
    def deserialize(cls, value, output=None):
        """Deserialize the HAL structure into output value.

        :param value: Dict of already loaded json which will be deserialized by schema attributes.
        :param output: If present, the output object will be updated instead of returning the deserialized data.

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

        if output is None:
            return result
        for attr in cls.__attrs__:
            attr.accessor.set(output, result[attr.name])


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
