halogen
=======

.. image:: https://api.travis-ci.org/olegpidsadnyi/halogen.png
   :target: https://travis-ci.org/olegpidsadnyi/halogen

.. image:: https://pypip.in/v/halogen/badge.png
   :target: https://crate.io/packages/halogen/

.. image:: https://coveralls.io/repos/olegpidsadnyi/halogen/badge.png?branch=master
   :target: https://coveralls.io/r/olegpidsadnyi/halogen


Python HAL generation/parsing library.

Schemas can be defined to specify attributes to be exposed and a structure 

Serialization
-------------

.. code-block:: python

    import halogen

    spell = {
        "uid": "abracadabra",
        "name": "Abra Cadabra",
        "cost": 10,
    }

    class Spell(halogen.Schema):

        self = halogen.Link(URI("spells"), attr="uid")
        name = halogen.Attr()

    serialized = Spell.serialize(spell)


This will produce HAL-like dictionary which can be serialized to json for the hal+json content type
or to XML for the hal+xml content type.

.. code-block:: json

    {
        "_links": {
            "self": {"href": "spells/abracadabra"}
        },
        "name": "Abra Cadabra"
        // The extra wasn't in the schema and this way ignored
    }


Deserialization
---------------

In order to collect all potential validation errors before the assigning the attributes.


.. code-block:: python

    import halogen

    hal = {
        "_links": {
            "self": {"href": "spells/abracadabra"}
        },
        "name": "Abra Cadabra",
    }

    class Spell(halogen.Schema):

        self = halogen.Link(URI("spells"), attr="uid")
        name = halogen.Attr()

    deserialized = Spell.deserialize(hal)


The deserialized data will look like this:

.. code-block:: python

    {
        "self": "abracadabra",
        "name": "Abra Cadabra",
    }

And when the `apply` method is called on the deserialized data:

.. code-block:: python

    spell = {}
    Spell.apply(deserialized, spell)


The deserialized values will be mapped to the resulting object using setter acessors of
the schema attributes.

.. code-block:: python

    {
        "uid": "abracadabra",
        "name": "Abra Cadabra",
    }
