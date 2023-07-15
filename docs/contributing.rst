Contributing
============

The source code is available on github at
``https://github.com/speedyleion/sphinx-c-autodoc``

The main development of this project utilizes
`tox <https://tox.readthedocs.io/en/latest/>`_. The project itself does not
provide a libclang implementation so this must be installed and available on
your system. Some common tox environments are:

- ``tox -e py38`` to run the tests.
- ``tox -e py38-cov`` to run the tests for coverage.
- ``tox -e docs`` to generate the documentation.

.. note:: Prior to contributing via a pull request please ensure all tox
    environments pass by running ``tox``, with no additional arguments.

Coverage
~~~~~~~~

The tests should currently have 100% coverage, |coverage|. This means any
contributions should maintain that level of coverage. It is understandable
that the amount of coverage can be a touchy topic and that some feel 100% is
`gold plating <https://en.wikipedia.org/wiki/Gold_plating_(project_management)>`_.
To be perfectly honest 80-90% was what this author used to target, until a
peer made the convincing argument:

    It is better to have a 100% coverage report with known coverage
    exceptions than to have 10-20% of the code in an unknown state.

Once a project has 100% coverage keeping that coverage is usually fairly
cheap. One should only be contributing functionality that is desired and if
it's desired then there should be tests to help maintain its correctness.
There are times where edge cases may be harder to hit and in such cases it is
acceptable to have a ``# pragma: no cover`` with some form of documentation
describing why that coverage wasn't able to be covered in automated tests.

.. |coverage| image:: https://codecov.io/gh/speedyleion/sphinx-c-autodoc/branch/master/graph/badge.svg
    :alt: Coverage
    :target: https://codecov.io/gh/speedyleion/sphinx-c-autodoc
