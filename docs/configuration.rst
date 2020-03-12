Configuring
===========

Configuration Variables
-----------------------

c_autodoc_roots
^^^^^^^^^^^^^^^

A list of directories which will be used to search for the files provided in the
:ref:`directives:Directives`. The directories are relative to documentation
source directory, often where ``conf.py`` is.

The list of directories will be searched in order so if duplicate named files
exist the first one encountered in the directory list will be used.

Example:

.. code-block:: python

    c_autodoc_roots = ['my/source/dir', 'other/source/dir']


Then a directive of the form::

    .. autocfunctoin:: some_file.c::some_function

would be searched first as ``my/source/dir/some_file.c`` then, if not found, it
would be searched as ``other/source/dir/some_file.c``.  Again this relative to
the top documentation source directory.

Events
------

c-autodoc-pre-process
^^^^^^^^^^^^^^^^^^^^^

There are times a project needs to perform some form of pre-processing of a
source file prior to the build up of the auto-documentation.  The
`c-autodoc-pre-process` is a sphinx event that will be triggered prior to the
parsing of the C file.

.. py:function:: c-autodoc-pre-process(app, filename, contents, *args)

    :param app: the Sphinx application object
    :param filename: The full filename being parsed
    :param contents: The file contents.  This is a list with one item, the file
        contents.  Modify the list in place.  Only the first element will be
        looked at by the parser.
    :param args: Unused, but provides compatibility for future expansions.

An example which replaces all instances of "the" with "this":

.. code-block:: python

    def pre_process(app, filename, contents, *args):
        file_body = contents[0]

        modified_contents = file_body.replace("the", "this")

        # replace the list to return back to the sphinx extension
        contents[:] = [modified_contents]

    app.connect("c-autodoc-pre-process", pre_process)

autodoc-process-docstring
^^^^^^^^^^^^^^^^^^^^^^^^^

Since this is extending the autodoc functionality the autodoc events are
available as well.  Of particular interest may be the `autodoc-process-docsting
<https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#event-autodoc-process-docstring>`_
which will be emitted for every C construct.
