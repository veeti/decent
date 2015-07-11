Schemas
=======

The :class:`decent.schema.Schema` class validates key-to-value mappings (typically ``dict`` instances), collecting result values and possible errors.

Creating and using a schema
---------------------------

The only required argument for constructing a schema is, well, a ``schema``. It must be a ``dict`` mapping expected keys to :doc:`validator callables <validators>`. A created schema is a validator callable like any other:

.. code-block:: python

    schema = Schema({
        'number': Is(int),
    })

    schema(123)
    >>>> 123

This allows for easy nesting of schemas inside schemas.

Default values
--------------

Keys can be wrapped with the :class:`decent.schema.Default` marker to give them a default value:

.. code-block:: python

    Schema({
        Default('name', default='John Doe'): validator,
    })

This value will be used if the key is not present. The ``default`` argument is also available in other key markers.

Optional keys
-------------

Keys can be wrapped with the :class:`decent.schema.Optional` marker to make them optional:

.. code-block:: python

    Schema({
        Optional('name'): validator,
    })

The given validator will only be called if the name key is present in the input data.

Extra keys
----------

If the schema encounters unknown keys, it will silently drop them from the output by default. It can also be configured to pass them through as-is or raise an error: see the ``extra_keys`` constructor argument.

Validating the entire result
----------------------------

The schema can also have a so-called ``entire`` validator that can be used to further validate and/or change the resulting data. For example, this can be useful if a validation depends on multiple fields.

.. code-block:: python

    def entire(data):
        # data is the result dictionary after all keys have been processed
        # and validated. Extra validation errors can be raised here, and
        # the data can be modified.
        return data
    schema = Schema({ ... }, entire=entire)

The validator is always called: even if individual fields have failed earlier. In this case, failed fields will not be included in the data.
