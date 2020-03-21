Viewcode
========

Similar to the sphinx python extension `viewcode`_. This extension provides a
way to also list the contents of C files and link between the documentation
to the C file contents.

Enabling this feature simply requires adding the viewcode sub package of this
extension to the list of desired sphinx extensions::

    extensions = [
        'sphinx_c_autodoc.viewcode',
        ]

This functionality can be seen with the :ref:`example_c_file:Example C File`, there will be
tags of the form ``[source]`` which can be clicked on and will follow the
link to the html version of the C file.

In order for this to work, the C domain directives have been expanded to
support a ``:module:`` option. This option is the name of the C file,
relative to :ref:`configuration:c_autodoc_roots`.

The auto directives will automatically populate this option. If one needs to
use non auto directives then this option will need to be manually specified
for the source code file to be populated.

.. _viewcode: https://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html