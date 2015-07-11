Introduction
============

*Decent* is a data validation library that can be used for many purposes. For example, a REST API can use it to validate and transform input data from the user.

Validation is designed around ordinary callable functions. A validator callable takes a single value as its argument. It must check it for validity and raise an error if necessary. Otherwise, it should return the result value: either a new value based on the input, or simply the input as it was.

To validate key-value data like dictionaries, the :class:`decent.schema.Schema` class is used. A schema can be built to validate specified keys using validators.

Decent comes with many useful :doc:`built-in validators <validators>` to be used in schemas or on their own. Of course, you can also create your own.

Example
-------

.. code-block:: python

    from decent import *

    User = Schema({
        'username': All(NotEmpty(), Strip(), Length(max=32)),
        'password': All(NotEmpty(), Length(min=10)),
        Optional('bio'): Length(max=1000),
    })

This is a schema with three fields: the username, password and bio. The bio key is optional, and can be omitted from input data without raising an error.

Every key must map to a validator callable. Here multiple validators are combined into one with the :func:`decent.validators.All` helper.

The resulting ``User`` schema is a validator callable like any other. It can be used with input data:

.. code-block:: python

    result = User({
        'username': " user",
        'password': "1234567890",
    })

The result is a dictionary of all the result values. For example, here the username is passed through the built-in :func:`decent.validators.Strip` validator. This removes extra whitespace from the username. We can look at the result value and find that it works as expected:

.. code-block:: python

    result['username']
    >>>> "user"

If any errors are encountered, an :class:`decent.error.Invalid` exception is raised. For example:

.. code-block:: python

    User({
        'username': "",
        'password': "short",
    })

    >>>> decent.error.Invalid: Must not be empty, Must have a length of at least 10

Simple, right?
