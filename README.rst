sphinx-c-autodoc
================

|build-status| |coverage| |black| |docs|

Dual-licensed under MIT or the `UNLICENSE <https://unlicense.org>`_.

.. inclusion_begin

A basic attempt at extending `Sphinx`_ and `autodoc`_ to work with C files.

The idea is to add support for similar directives that `autodoc`_ provides. i.e.

A function in ``my_c_file.c``:

.. code-block:: c

    /**
     * A simple function that adds.
     *
     * @param a: The initial value
     * @param b: The value to add to `a`
     *
     * @returns The sum of `a` and `b`.
     *
     *
    int my_adding_function(int a, int b) {
        return a + b;
        }

Could be referenced in documentation as:

.. code-block:: rst

    .. autocfunction:: my_c_file.c::my_adding_function

With the resulting documentation output of:

.. c:function:: int my_adding_function(int a, int b)

    A simple function that adds.

    :param a: The initial value
    :param b: The value to add to `a`
    :returns: The sum of `a` and `b`

.. _autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
.. _Sphinx: https://www.sphinx-doc.org/en/master/index.html

Requires
--------

* `clang <https://pypi.org/project/clang/>`_
* `beautifulsoup4 <https://www.crummy.com/software/BeautifulSoup/bs4/doc/>`_

Similar Tools
-------------

* `hawkmoth <https://github.com/jnikula/hawkmoth>`_ a sphinx extension that
  which will document all of a C file. It supports being able to regex list
  files and have those files be documented.
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

.. |docs| image:: https://readthedocs.org/projects/sphinx-c-autodoc/badge/?version=latest
    :alt: Documentation Status
    :target: https://sphinx-c-autodoc.readthedocs.io/en/latest/?badge=latest

.. inclusion_end

Full Documentation
------------------

The complete documentation can be found at https://sphinx-c-autodoc.readthedocs.io/en/latest
