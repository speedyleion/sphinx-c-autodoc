==========
Change Log
==========

This document records all notable changes to `sphinx-c-autodoc <https://sphinx-c-autodoc.readthedocs.io/en/latest/>`_.
This project adheres to `Semantic Versioning <https://semver.org/>`_.

`v1.5.1-dev`_ (unreleased)
==========================

`v1.5.0`_ (2025-03-31)
==========================

Added
-----

* Support for Sphinx 8.2

`v1.4.0`_ (2024-10-16)
==========================

Removed
-------

* Support for python 3.8
* Support for Sphinx 3
* Support for Clang 6 through Clang 10


`v1.3.0`_ (2023-09-21)
==========================

Added
-----

* Support for Sphinx 7

Removed
-------

* Support for python 3.7

`v1.2.2`_ (2023-06-28)
==========================

Fixed
-----

* Failed parsing of enumerators which were defined based on macros `#174`_

.. _#174: https://github.com/speedyleion/sphinx-c-autodoc/issues/174

`v1.2.1`_ (2023-06-12)
==========================

Fixed
-----

* Regression for processing anonymous structs in versions of Clang prior to
  Clang 16. `#166`_

.. _#166: https://github.com/speedyleion/sphinx-c-autodoc/issues/166

`v1.2.0`_ (2023-06-11)
==========================

Added
-----

* Support for Clang 16. Clang 16 changed the way anonymous constructs are
  represented when walking the AST. These differences are now accounted for.

`v1.1.1`_ (2022-12-21)
==========================

Fixed
-----

* Packaging
  * Incorrectly pinned Sphinx, Clang, BeautifulSoup4
  * Was missing `sphinx-c-apidoc` entry point

`v1.1.0`_ (2022-12-20)
==========================

Added
-----

* Support for Sphinx 5

`v1.0.0`_ (2021-09-12)
==========================

Added
-----

* Dual licensing with MIT license.

* Support for global compilation args.
  Compilation args can now be specified with the
  ``c_autodoc_compilation_args`` configuration value.

Fixes
-----

* Fix parsing of multi-paragraph function documentation that used doxygen style
  markup.  Previously multi-paragraph function documentation which used doxygen
  style markup would get merged in to one paragraph.  Now the multi-paragraph
  nature is preserved.

`v0.4.0`_ (2020-12-27)
==========================

Changed
-------

* Undocumented constructs are no longer added to the documentation by default.
  To maintain previous behavior add `:undoc-members:` to the project's
  `autodoc_default_options`_.

Added
-----

* `:undoc-members:` and `:no-undoc-members:` option for the autocmodule
  directive. This option set allows for controlling the listing of undocumented
  constructs.  The default is to not list undocumented constructs.

Fixes
-----

* Fix file level variables with unknown types.  Previously variables with
  unknown types would cause an error in Sphinx processing.
* Fix documentation of members that are arrays. Previously struct members that
  were array types would cause an error as the array size was put between the
  type and the member name.
* Fix viewcode processing of empty files. Previously an exception would be
  raised when the viewcode extension tried to process empty files.
* Call out Sphinx 3.1 as minimum version in ``setup.py``. Previously the Sphinx
  version in setup.py called out 3.0 or greater. This was incorrect as features
  from Sphinx 3.1 are being utilized.

`v0.3.1`_ (2020-10-24)
==========================

Added
-----

* The ``sphinx-c-apidoc`` command.  This command provides users the ability to quickly
  build up a set of documentation files for a C directory.

* Support for compile flags via a 
  `compilation database <https://clang.llvm.org/docs/JSONCompilationDatabase.html>`_.
  A compilation database can now be specified with the
  ``c_autodoc_compilation_database`` configuration value.

Fixes
-----

* No longer passing `typedef` to auto documentation of types.
  Previously the `typedef` keyword was being provided to sphinx as part of the
  signature. This resulted in losing the ability to link to the type in html
  documentation.

* Display of function arguments with unknown array types.
  Previously when a function had an argument that was an array and an unknown type, it
  would result in being empty in the output documentation.  Now the full function
  signature is provided token by token, with the exception of comments.

`v0.3.0`_ (2020-08-22)
==========================

Changed
-------

* Changed to support sphinx version 3.  Due to significant changes between
  sphinx 2 and 3, sphinx 2 is no longer supported.

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


.. _v1.5.1-dev: https://github.com/speedyleion/sphinx-c-autodoc/compare/v1.5.0...main
.. _v1.5.0: https://github.com/speedyleion/sphinx-c-autodoc/compare/v1.4.0...v1.5.0
.. _v1.4.0: https://github.com/speedyleion/sphinx-c-autodoc/compare/v1.3.0...v1.4.0
.. _v1.3.0: https://github.com/speedyleion/sphinx-c-autodoc/compare/v1.2.2...v1.3.0
.. _v1.2.2: https://github.com/speedyleion/sphinx-c-autodoc/compare/v1.2.1...v1.2.2
.. _v1.2.1: https://github.com/speedyleion/sphinx-c-autodoc/compare/v1.2.0...v1.2.1
.. _v1.2.0: https://github.com/speedyleion/sphinx-c-autodoc/compare/v1.1.1...v1.2.0
.. _v1.1.1: https://github.com/speedyleion/sphinx-c-autodoc/compare/v1.1.0...v1.1.1
.. _v1.1.0: https://github.com/speedyleion/sphinx-c-autodoc/compare/v1.0.0...v1.1.0
.. _v1.0.0: https://github.com/speedyleion/sphinx-c-autodoc/compare/v0.4.0...v1.0.0
.. _v0.4.0: https://github.com/speedyleion/sphinx-c-autodoc/compare/v0.3.1...v0.4.0
.. _v0.3.1: https://github.com/speedyleion/sphinx-c-autodoc/compare/v0.3.0...v0.3.1
.. _v0.3.0: https://github.com/speedyleion/sphinx-c-autodoc/compare/v0.2.0...v0.3.0
.. _v0.2.0: https://github.com/speedyleion/sphinx-c-autodoc/compare/v0.1.1...v0.2.0
.. _v0.1.1: https://github.com/speedyleion/sphinx-c-autodoc/compare/v0.1.0...v0.1.1
.. _v0.1.0: https://github.com/speedyleion/sphinx-c-autodoc/commits/v0.1.0

.. _autodoc_default_options: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_default_options
