sphinx-c-autodoc
================

|build-status| |coverage| |black|

.. inclusion_begin

Use C with `autodoc`_.

This is a very basic attempt at extending `autodoc`_ to work with c files.

The idea is to add support for the same or similar directives that `autodoc`_
provides. i.e.
::

    .. autocfunction:: my_c_file.c::my_cool_function

.. _autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

Contributing
------------

The source code is available on github at
``https://github.com/speedyleion/sphinx-c-autodoc``

The main development of this project utilizes
`tox <https://tox.readthedocs.io/en/latest/>`_. The project itself does not
provide a libclang implementation so this must be installed and available on
your system. Some common tox environments are:

- ``tox -e py37`` to run the tests.
- ``tox -e py37-cov`` to run the tests for coverage.
- ``tox -e docs`` to generate the documentation.

.. note:: Prior to contributing via a pull request pleas ensure all tox
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
cheap. One should only be contributing funcionality that is desired and if
it's desired then there should be tests to help maintain its correctness.
There are times where edge cases may be harder to hit and in such cases it is
acceptable to have a ``# pragma: no cover`` with some form of documentation
describing why that coverage wasn't able to be covered in automated tests.


Similar Tools
-------------

* `hawkmoth <https://github.com/jnikula/hawkmoth>`_ a sphinx extension that
  will fully document a c file. This is probably where you should look if you
  want something functional at this time.
* `breathe <https://github.com/michaeljones/breathe>`_ A doxygen output to
  sphinx tool.

.. |build-status| image:: https://github.com/speedyleion/sphinx-c-autodoc/workflows/Python%20package/badge.svg
    :alt: Build Status
    :scale: 100%
    :target: https://github.com/speedyleion/sphinx-c-autodoc/actions?query=workflow%3A%22Python+package%22

.. |coverage| image:: https://codecov.io/gh/speedyleion/sphinx-c-autodoc/branch/master/graph/badge.svg
    :alt: Coverage
    :scale: 100%
    :target: https://codecov.io/gh/speedyleion/sphinx-c-autodoc

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Code Style
    :scale: 100%
    :target: https://github.com/psf/black

.. inclusion_end
