import copy

import six

from .error import SchemaError, Error, Invalid


class Schema(object):
    """
    A schema that validates data given to it using the specified rules.

    The ``schema`` must be a dictionary of key-value mappings. Values must
    be callable validators. See ``XX``.

    The ``entire`` argument allows specifying a callable validator that runs on
    the entire input after every field is validated. If provided, the validator
    will always run, even if validation errors are raised beforehand. Failed
    keys will not be included in the given data.

    The ``extra_keys`` argument must be one of :attr:`.ACCEPT`, :attr:`.IGNORE`
    or :attr:`.REJECT`.

    The ``required_error`` argument specifies the error message used when a
    key is missing. :attr:`.REQUIRED_ERROR` is the default.
    """

    ACCEPT = 'ACCEPT'
    IGNORE = 'IGNORE'
    REJECT = 'REJECT'

    REQUIRED_ERROR = "This field is required."
    """
    The default error message for a missing required key.
    """

    REJECT_ERROR = "This field is unknown."
    """
    The default error message for an unknown rejected key.
    """

    def __init__(self, schema, entire=None, extra_keys=IGNORE, required_error=None):
        self.extra_keys = extra_keys
        self.entire = entire
        self.required_error = required_error or self.REQUIRED_ERROR

        if not isinstance(schema, dict):
            raise SchemaError("The provided schema must be a dictionary.")
        self.schema = schema
        self.validator = self._build(schema)

    def __call__(self, data):
        """
        Validates the given ``data`` dictionary and returns transformed values.

        Will raise :class:`decent.error.Invalid` if any validation errors are
        encountered.
        """
        return self.validator(copy.deepcopy(data))

    def _build(self, schema):
        extra_keys = self.extra_keys
        entire = self.entire

        # Enumerate all the keys in the schema.
        all_keys = set(schema.keys())
        _required_keys = set([key for key in all_keys if not isinstance(key, Optional)])

        # Enumerate default key values.
        defaults = {}
        for key in all_keys:
            if isinstance(key, Marker) and key.default != None:
                defaults[key] = key.default

        # Make sure all validators are callable.
        for key, value in six.iteritems(schema):
            if not hasattr(value, '__call__'):
                raise SchemaError("Validator {!r} for key '{!s}' is not callable.".format(value, key))

        def validator(data):
            # Sanity check.
            if not isinstance(data, dict):
                raise Invalid([Error("Data must be a dictionary.")])

            # Track which required keys are not present.
            required_keys = _required_keys.copy()

            # Fill available defaults before validating.
            missing = all_keys.copy() - set(data.keys())
            for key in missing:
                if key in defaults:
                    data[key] = defaults[key]

            errors = []
            result = {}

            for key, value in six.iteritems(data):
                # If this key is not in the schema, decide what to do with it.
                if key not in all_keys:
                    if extra_keys == self.ACCEPT:
                        # Pass through as is.
                        result[key] = value
                    elif extra_keys == self.REJECT:
                        # Reject with error.
                        errors.append(Error(self.REJECT_ERROR, [key]))
                    continue # pragma: no cover

                # Validate.
                validator = schema[key]
                result_value = self._run_validator(validator, value, errors, key)
                if result_value:
                    result[key] = result_value

                # Track required keys.
                if key in required_keys:
                    required_keys.remove(key)

            # Add an error for every missing key.
            for key in required_keys:
                errors.append(Error(self.required_error, [key]))

            # Run the validator for the entire schema.
            if entire:
                result = self._run_validator(entire, result, errors)

            if errors:
                raise Invalid(errors)

            return result

        return validator

    def _run_validator(self, validator, data, errors, key=None):
        try:
            return validator(data)
        except Invalid as all:
            for e in all:
                self._add_error(e, errors, key)
        except Error as e:
            self._add_error(e, errors, key)

    def _add_error(self, error, errors, key=None):
        if key:
            error.path.insert(0, key)
        errors.append(error)

class Marker(object):
    """
    A base class for key markers that wrap a key.
    """

    def __init__(self, key, default=None):
        self.key = key
        self.default = default

    def __str__(self):
        return str(self.key)

    def __eq__(self, other):
        return self.key == other

    def __hash__(self):
        return hash(self.key)

    __repr__ = __str__


class Default(Marker):
    """
    A marker for specifying a default value for a key.
    """
    pass


class Optional(Marker):
    """
    A marker for specifying a key as optional. The schema will validate data
    without the key present.
    """
    pass


__all__ = ('Schema', 'Marker', 'Default', 'Optional',)
