class DecentError(Exception):
    pass


class SchemaError(DecentError):
    pass


class Error(DecentError):
    """
    A single validation error.

    The ``message`` contains an explanation for the error: for example, "this
    value must be at least 10 characters long".

    The ``path`` is a list of keys to the field this error is for. This is
    usually automatically set by the :class:`decent.schema.Schema` and/or
    validator callable being used.
    """

    def __init__(self, message, path=None):
        self.message = message
        if path:
            self.path = path[:]
        else:
            self.path = []

    def as_dict(self, join='.'):
        """
        Returns the error as a path to message dictionary. Paths are joined
        with the ``join`` string.
        """
        if self.path:
            path = [str(node) for node in self.path]
        else:
            path = ''
        return { join.join(path): self.message }

    @property
    def messages(self):
        return [self.message]

    @property
    def paths(self):
        return [self.path]

    def __str__(self):
        return str(self.message)


class Invalid(Error):
    """
    A collection of one or more validation errors for a schema.
    """

    def __init__(self, errors=None):
        self.errors = []
        if errors:
            self.errors.extend(errors[:])

    def append(self, error):
        self.errors.append(error)

    def as_dict(self, join='.'):
        """
        Returns all the errors in this collection as a path to message
        dictionary. Paths are joined with the ``join`` string.
        """
        result = {}
        for e in self.errors:
            result.update(e.as_dict(join))
        return result

    @property
    def message(self):
        """
        The first error message in this collection.
        """
        if self.errors:
            return self.errors[0].message

    @property
    def path(self):
        """
        The first error path in this collection.
        """
        if self.errors:
            return self.errors[0].path

    @property
    def messages(self):
        """
        The list of error messages in this collection.
        """
        return [e.message for e in self.errors]

    @property
    def paths(self):
        """
        The list of error paths in this collection.
        """
        return [e.path for e in self.errors]

    def __str__(self):
        return ', '.join(self.messages)

    def __getitem__(self, i):
        return self.errors[i]

    def __len__(self):
        return len(self.errors)
