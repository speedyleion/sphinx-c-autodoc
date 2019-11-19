sphinx-c-doc
============

Use C with `autodoc`_.

This is a very basic attempt at extending `autodoc`_ to work with c files.

The idea is to add support for the same or similar directives that `autodoc`_
provides. i.e. ``.. c:autofunction:: <some_file::some_function>``.

Similar Tools
-------------

* :ref:`hawkmoth https://github.com/jnikula/hawkmoth`_ a sphinx extension that
  will fully document a c file. This is probably where you should look if you
  want something functional at this time.
* :ref:`breathe https://github.com/michaeljones/breathe`_ A doxygen output to
  sphinx tool.

.. _autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
