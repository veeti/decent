Validators
==========

Validators are ordinary callables that take a single argument (the input value) and return a transformed result value. They can also raise validation errors.

.. function:: IValidator(value)

    Validates the input ``value`` and possibly transforms it.
    
    Returns the new value. If the value is invalid, raises a :class:`decent.error.Error` or :class:`decent.error.Invalid` exception.

Validator callables can be used inside schemas, but also standalone.

Built-in validators
-------------------

Decent ships with many built-in validators that can be used and combined for usual tasks. Instances of them are built through the following constructors:

Helpers & Building blocks
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: decent.validators.All
    :noindex:
.. autofunction:: decent.validators.Any
    :noindex:
.. autofunction:: decent.validators.Default
    :noindex:
.. autofunction:: decent.validators.Maybe
    :noindex:
.. autofunction:: decent.validators.Msg
    :noindex:

Basics
^^^^^^

.. autofunction:: decent.validators.Eq
    :noindex:
.. autofunction:: decent.validators.Coerce
    :noindex:
.. autofunction:: decent.validators.Instance
    :noindex:
.. autofunction:: decent.validators.Type
    :noindex:

Collections
^^^^^^^^^^^

.. autofunction:: decent.validators.List
    :noindex:
.. autofunction:: decent.validators.Length
    :noindex:

Booleans
^^^^^^^^

.. autofunction:: decent.validators.Boolean
    :noindex:

Numbers
^^^^^^^

.. autofunction:: decent.validators.Range
    :noindex:
.. autofunction:: decent.validators.Length
    :noindex:

Strings
^^^^^^^

.. autofunction:: decent.validators.Lower
    :noindex:
.. autofunction:: decent.validators.Upper
    :noindex:
.. autofunction:: decent.validators.Strip
    :noindex:
.. autofunction:: decent.validators.Length
    :noindex:

String conversions
^^^^^^^^^^^^^^^^^^

.. autofunction:: decent.validators.Uuid
    :noindex:
