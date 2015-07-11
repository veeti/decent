decent
======

**Decent** is a data validation library for Python 2 & 3. There are many like it, but this one is mine.

Read the documentation_ for more details.

Quick example
-------------

.. code-block:: python

    from decent import *

    schema = Schema({
        'name': All(Strip(), NotEmpty()),
        'age': Range(min=0, max=200),
    })

    try:
        output = schema(input)
        ...
    except Invalid as e:
        print('\n'.join(e.messages))
        ...

Thanks
------

This library takes inspiration from Voluptuous_ and Good_, but doesn't implement many of their more magical features. You may be interested in them if you find yourself wanting more.

Links
-----

* Documentation_ on Read the Docs
* Decent on PyPI_

License
-------

MIT, see the ``LICENSE`` file.

.. _Documentation: https://decent.readthedocs.org/en/latest
.. _Voluptuous: https://github.com/alecthomas/voluptuous
.. _Good: https://github.com/kolypto/py-good
.. _PyPI: https://pypi.python.org/pypi/decent
