sphinx-c-doc
============
|build-status| |coverage|

.. inclusion_begin

Use C with `autodoc`_.

This is a very basic attempt at extending `autodoc`_ to work with c files.

The idea is to add support for the same or similar directives that `autodoc`_
provides. i.e.

    .. rst:directive:: .. autocfunction:: my_c_file.c::my_cool_function

.. _autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

.. inclusion_end

Similar Tools
-------------

* `hawkmoth <https://github.com/jnikula/hawkmoth>`_ a sphinx extension that
  will fully document a c file. This is probably where you should look if you
  want something functional at this time.
* `breathe <https://github.com/michaeljones/breathe>`_ A doxygen output to
  sphinx tool.

.. |build-status| image:: https://github.com/speedyleion/sphinx-c-doc/workflows/Python%20package/badge.svg
    :alt: build status
    :scale: 100%
    :target: https://github.com/speedyleion/sphinx-c-doc/actions?query=workflow%3A%22Python+package%22

.. |coverage| image:: https://codecov.io/gh/speedyleion/sphinx-c-doc/branch/master/graph/badge.svg
    :alt: Coverage
    :scale: 100%
    :target: https://codecov.io/gh/speedyleion/sphinx-c-doc
