Napoleon
========

This extension also provides a way to extend `napoleon`_ to work with C constructs.

Enabling this feature simply requires adding the napoleon sub package of this
extension to the list of desired sphinx extensions::

    extensions = [
        'sphinx_c_autodoc.napoleon',
        ]

.. note:: Currently only the Google style docstrings are supported.  

Using this extension will take:

.. literalinclude:: ../tests/assets/c_source/example.c
    :language: c
    :lines: 70-92

and convert it into 

.. autoctype:: example.c::members_documented_with_napoleon
    :members:
    :noindex:

.. _napoleon: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
