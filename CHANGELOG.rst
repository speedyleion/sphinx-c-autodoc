==========
Change Log
==========

This document records all notable changes to `sphinx-c-autodoc <https://sphinx-c-autodoc.readthedocs.io/en/latest/>`_.
This project adheres to `Semantic Versioning <https://semver.org/>`_.


`v0.3.0-dev`_ (unreleased)
==========================

Fixes
-----

* typedef function and function pointers with unknown return types were not
  being properly handled.  These now get handled, but the unknown types are
  whatever clang provides, which is usually ``int``.
* typedef unions with unknown member types caused in index error.  This has been
  fixed and these unknown member types are evaluated by clang to be ``int``.
* Fix comments in function declarations showing up in documentation. When
  comments were placed inbetween parameter types and the parameter names, and
  the type was unknown to clang, the fallback parsing would take the
  declaration character for character (consolidating whitespace). This
  resulted in comments being pulled in to the documentation verbatim. Now
  comments will explicitly be skipped over when the fall back parsing for
  function declarations happens.

`v0.2.0`_ (2020-04-04)
==========================

Added
-----

* Viewcode functionality which allows for listing the source C files and
  providing links between the documentation and the C source listings.
* `:private-members:` and `:no-private-members:` option for the autocmodule
  directive. This option set allows for controlling the documentation of
  constructs based on what is visible outside of the module. For header
  files this means everything will still be documented. For standard source
  files only non static functions and non static variables will be auto
  documented if the :private-members: is not specified, or the
  :no-private-members: is specified.

Fixes
-----

* Anonymous enumerations which were contained in a typedef were being documented twice.
  Once as the typedef and once as anonymous. Now they are only documnted as
  part of the typedef.

`v0.1.1`_ (2020-03-15)
======================

Fixes
-----

* C module is not resolved relative to the document root,
  `#1 <https://github.com/speedyleion/sphinx-c-autodoc/issues/1>`_.
* C module can not be specified in a sub directory,
  `#2 <https://github.com/speedyleion/sphinx-c-autodoc/issues/2>`_.

`v0.1.0`_ (2020-03-07)
======================

* Initial public release


.. _v0.3.0-dev: https://github.com/speedyleion/sphinx-c-autodoc/compare/v0.1.1...master
.. _v0.2.0: https://github.com/speedyleion/sphinx-c-autodoc/compare/v0.1.1...v0.2.0
.. _v0.1.1: https://github.com/speedyleion/sphinx-c-autodoc/compare/v0.1.0...v0.1.1
.. _v0.1.0: https://github.com/speedyleion/sphinx-c-autodoc/commits/v0.1.0
