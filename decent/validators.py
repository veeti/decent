from functools import wraps
import numbers
import uuid

import six

from decent.error import Error, Invalid

## Helpers

def All(*validators):
    """
    Combines all the given validator callables into one, running all the
    validators in sequence on the given value.
    """
    @wraps(All)
    def built(value):
        for validator in validators:
            value = validator(value)
        return value
    return built

def Any(*validators):
    """
    Combines all the given validator callables into one, running the given
    value through them in sequence until a valid result is given.
    """
    @wraps(Any)
    def built(value):
        error = None
        for validator in validators:
            try:
                return validator(value)
            except Error as e:
                error = e
        raise error
    return built

def Maybe(validator):
    """
    Wraps the given validator callable, only using it for the given value if it
    is not ``None``.
    """
    @wraps(Maybe)
    def built(value):
        if value != None:
            return validator(value)
    return built

def Msg(validator, message):
    """
    Wraps the given validator callable, replacing any error messages raised.
    """
    @wraps(Msg)
    def built(value):
        try:
            return validator(value)
        except Error as e:
            e.message = message
            raise e
    return built

def Default(default):
    """
    Creates a validator callable that replaces ``None`` with the specified
    default value.
    """
    @wraps(Default)
    def built(value):
        if value == None:
            return default
        return value
    return built

## Basics

def Eq(value, message="Not equal to {!s}"):
    """
    Creates a validator that compares the equality of the given value to
    ``value``.

    A custom message can be specified with ``message``. It will be formatted
    with ``value``.
    """
    @wraps(Eq)
    def built(_value):
        if _value != value:
            raise Error(message.format(value))
        return _value
    return built

def Type(expected, message="Not of type {}"):
    """
    Creates a validator that compares the type of the given value to
    ``expected``. This is a direct type() equality check. Also see
    ``Instance``, which is an isinstance() check.

    A custom message can be specified with ``message``.
    """
    @wraps(Type)
    def built(value):
        if type(value) != expected:
            raise Error(message.format(expected.__name__))
        return value
    return built

def Instance(expected, message="Not an instance of {}"):
    """
    Creates a validator that checks if the given value is an instance of
    ``expected``.

    A custom message can be specified with ``message``.
    """
    @wraps(Instance)
    def built(value):
        if not isinstance(value, expected):
            raise Error(message.format(expected.__name__))
        return value
    return built

def Coerce(type, message="Not a valid {} value"):
    """
    Creates a validator that attempts to coerce the given value to the
    specified ``type``. Will raise an error if the coercion fails.

    A custom message can be specified with ``message``.
    """
    @wraps(Coerce)
    def built(value):
        try:
            return type(value)
        except (TypeError, ValueError) as e:
            raise Error(message.format(type.__name__))
    return built

## Collections

def List(validator):
    """
    Creates a validator that runs the given validator on every item in a list
    or other collection. The validator can mutate the values.

    Any raised errors will be collected into a single ``Invalid`` error. Their
    paths will be replaced with the index of the item. Will raise an error if
    the input value is not iterable.
    """
    @wraps(List)
    def built(value):
        if not hasattr(value, '__iter__'):
            raise Error("Must be a list")

        invalid = Invalid()
        for i, item in enumerate(value):
            try:
                value[i] = validator(item)
            except Invalid as e:
                for error in e:
                    error.path.insert(0, i)
                    invalid.append(error)
            except Error as e:
                e.path.insert(0, i)
                invalid.append(e)

        if len(invalid):
            raise invalid
        return value
    return built

## Booleans

def Boolean():
    """
    Creates a validator that attempts to convert the given value to a boolean
    or raises an error. The following rules are used:

    ``None`` is converted to ``False``.

    ``int`` values are ``True`` except for ``0``.

    ``str`` values converted in lower- and uppercase:

    * ``y, yes, t, true``
    * ``n, no, f, false``
    """
    @wraps(Boolean)
    def built(value):
        # Already a boolean?
        if isinstance(value, bool):
            return value

        # None
        if value == None:
            return False

        # Integers
        if isinstance(value, int):
            return not value == 0

        # Strings
        if isinstance(value, str):
            if value.lower() in { 'y', 'yes', 't', 'true' }:
                return True
            elif value.lower() in { 'n', 'no', 'f', 'false' }:
                return False

        # Nope
        raise Error("Not a boolean value.")
    return built

## Numbers

def Range(min=None, max=None, min_message="Must be at least {min}", max_message="Must be at most {max}"):
    """
    Creates a validator that checks if the given numeric value is in the
    specified range, inclusive.

    Accepts values specified by ``numbers.Number`` only, excluding booleans.

    The error messages raised can be customized with ``min_message`` and
    ``max_message``. The ``min`` and ``max`` arguments are formatted.
    """
    @wraps(Range)
    def built(value):
        if not isinstance(value, numbers.Number) or isinstance(value, bool):
            raise Error("Not a number")
        if min is not None and min > value:
            raise Error(min_message.format(min=min, max=max))
        if max is not None and value > max:
            raise Error(max_message.format(min=min, max=max))
        return value
    return built

def Length(min=None, max=None, min_message="Must have a length of at least {min}", max_message="Must have a length of at most {max}"):
    """
    Creates a validator that checks if the given value's length is in the
    specified range, inclusive. (Returns the original value.)

    See :func:`.Range`.
    """
    validator = Range(min, max, min_message, max_message)
    @wraps(Length)
    def built(value):
        if not hasattr(value, '__len__'):
            raise Error("Does not have a length")
        validator(len(value))
        return value
    return built

## Strings

def _string_function(value, name):
    if not isinstance(value, six.string_types):
        raise Error("Must be a string")
    return getattr(value, name)()

def Lower():
    """
    Creates a validator that converts the input string to lowercase. Will raise
    an error for non-string types.
    """
    @wraps(Lower)
    def built(value):
        return _string_function(value, 'lower')
    return built

def Upper():
    """
    Creates a validator that converts the input string to UPPERCASE. Will raise
    an error for non-string types.
    """
    @wraps(Upper)
    def built(value):
        return _string_function(value, 'upper')
    return built

def Strip():
    """
    Creates a validator that strips the input string of whitespace. Will raise
    an error for non-string types.
    """
    @wraps(Strip)
    def built(value):
        return _string_function(value, 'strip')
    return built

def NotEmpty():
    """
    Creates a validator that validates the given string is not empty. Will
    raise an error for non-string types.
    """
    @wraps(NotEmpty)
    def built(value):
        if not isinstance(value, six.string_types) or not value:
            raise Error("Must not be empty")
        return value
    return built

## String conversions

def Uuid(to_uuid=True):
    """
    Creates a UUID validator. Will raise an error for non-string types and
    non-UUID values.

    The given value will be converted to an instance of ``uuid.UUID`` unless
    ``to_uuid`` is ``False``.
    """
    @wraps(Uuid)
    def built(value):
        invalid = Error("Not a valid UUID")

        if isinstance(value, uuid.UUID):
            return value
        elif not isinstance(value, six.string_types):
            raise invalid

        try:
            as_uuid = uuid.UUID(value)
        except (ValueError, AttributeError) as e:
            raise invalid

        if to_uuid:
            return as_uuid
        return value
    return built
