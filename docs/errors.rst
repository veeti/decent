Errors
======

The main error type in Decent is :class:`decent.error.Error`. It contains an error ``message`` as a description of the validation failure and a ``path`` list pointing to the erroneous field.

A subclass of :class:`Error` called :class:`decent.error.Invalid` can contain multiple errors. If you're working with schemas, you'll probably want to catch this error.

Error paths
-----------

The ``path`` field of an error is a list of nodes leading to the erroneous field. For example, a validation error on a field called ``password`` inside a ``user`` schema would have a path of ``['user', 'field']``.

Error paths are typically populated automatically. For example, :class:`decent.schema.Schema` automatically sets error paths for raised errors. Likewise, the built-in :func:`decent.validators.List` validator will prepend list indexes to all raised errors.

Overriding messages
-------------------

You can use the built-in :func:`decent.validators.Msg` helper to override the error messages raised by any validator. For example:

.. code-block:: python

    password_validator = Msg(
        Length(min=10),
        "Pick a passwords with 10 characters or more to be safe."
    )

Many built-in validators also have granular arguments for overriding their messages.
